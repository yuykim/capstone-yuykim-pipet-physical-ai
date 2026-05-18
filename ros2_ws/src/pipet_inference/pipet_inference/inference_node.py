#!/usr/bin/env python3
"""
LeRobot ACT 체크포인트로 Indy7 + Mark7 자율 추론.

ROS Humble은 Python 3.10, LeRobot 0.5.x는 Python 3.12+ 이라 기본은 ZMQ 사이드카다.

  터미널 A (conda lerobot):
    export PYTHONPATH="$PWD/install/pipet_inference/lib/python3.10/site-packages:$PYTHONPATH"
    conda activate lerobot
    zmq_act_server --model-path .../checkpoints/last --bind tcp://127.0.0.1:5560

  터미널 B:
    ros2 launch pipet_bringup inference.launch.py indy_ip:=192.168.1.10 autonomy_enabled:=true

관측: /joint_states 6축 + 손목/오버헤드 RGB(+depth).
액션: 기본 joint 모드는 delta_q(6) + gripper 0~4.
  control_mode=cartesian 이면 observation.state를 [q,dq,ee_pose]로 맞추고,
  delta_ee_pose(6) + gripper 0~4 로 해석하고
  /indy/teleop_pose 에 누적 상대 pose [x_mm,y_mm,z_mm,rx_deg,ry_deg,rz_deg]를 발행한다.
  state_target_dim=26(extended)이면 TF(world<-tcp)와 마지막 그리퍼 명령으로 observation.state를 채움
  (변환 시 --fk_urdf와 동일 URDF의 fk_urdf_path를 주면 TF 실패 시 Pinocchio FK).

안전: 기본 autonomy_enabled=false. dry_run=true 로 명령 없이 로그만.
"""

from __future__ import annotations

import importlib.util
import threading
from pathlib import Path
from typing import Any, List, Optional, Union

import numpy as np
import rclpy
import tf2_ros
from builtin_interfaces.msg import Duration
from cv_bridge import CvBridge
from rclpy.duration import Duration as RclDuration
from rclpy.node import Node
from rclpy.time import Time
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

import message_filters

from indy_interfaces.srv import IndyService

# Neuromeka indy_driver teleop mode codes. Forks may differ, so launch params can override them.
_DEFAULT_MSG_TELE_TASK_RLT = 5
_DEFAULT_MSG_TELE_JOINT_ABS = 6

from pipet_inference.lerobot_act_backend import (
    LeRobotActBackend,
    read_dataset_root_from_train_config,
    resolve_pretrained_model_dir,
)
from pipet_inference.sidecar_zmq_client import ZmqLerobotClient


def _joint_vec_to_six(seq) -> List[float]:
    xs = list(seq)
    if len(xs) < 6:
        return xs + [0.0] * (6 - len(xs))
    return xs[:6]


def _depth_to_u8_rgb(depth_hw: np.ndarray) -> np.ndarray:
    """
    Convert depth image (uint16/mm) to pseudo-RGB uint8.
    Matches conversion-time behavior: per-frame robust scaling over valid pixels.
    """
    d = np.asarray(depth_hw)
    if d.ndim != 2:
        raise ValueError(f"Depth image must be 2D, got {d.shape}")
    d = d.astype(np.float32, copy=False)
    valid = d > 0
    out_u8 = np.zeros_like(d, dtype=np.uint8)
    if np.any(valid):
        v = d[valid]
        lo = float(np.percentile(v, 1.0))
        hi = float(np.percentile(v, 99.0))
        if hi <= lo:
            hi = lo + 1.0
        scaled = (d - lo) / (hi - lo)
        scaled = np.clip(scaled, 0.0, 1.0)
        out_u8 = (scaled * 255.0).astype(np.uint8)
        out_u8[~valid] = 0
    return np.repeat(out_u8[..., None], 3, axis=2)


# NPZ / convert.py 와 동일한 그리퍼 디스크리트 코드
GRIP_HOLD = 0
GRIP_GRASP = 1
GRIP_OPEN = 2
GRIP_PRESS = 3
GRIP_RELEASE = 4


class InferenceNode(Node):
    def __init__(self) -> None:
        super().__init__("inference_node")

        self.declare_parameter("model_path", "")
        self.declare_parameter("model_type", "lerobot")
        self.declare_parameter("dataset_repo_id", "pipet_dataset")
        self.declare_parameter("dataset_root", "")
        self.declare_parameter("task", "Pick up the pipette")
        self.declare_parameter("device", "cuda")
        self.declare_parameter("inference_hz", 20.0)
        self.declare_parameter("sync_slop", 0.08)
        self.declare_parameter("control_mode", "joint")
        self.declare_parameter("trajectory_topic", "/joint_trajectory_controller/joint_trajectory")
        self.declare_parameter("cartesian_pose_topic", "/indy/teleop_pose")
        self.declare_parameter("trajectory_horizon_sec", 0.12)
        self.declare_parameter("max_delta_rad", 0.25)
        self.declare_parameter(
            "max_joint_speed_rad_s",
            0.0,
        )
        self.declare_parameter("max_delta_mm", 2.0)
        self.declare_parameter("max_delta_deg", 2.0)
        self.declare_parameter("max_cartesian_speed_mm_s", 0.0)
        self.declare_parameter("max_angular_speed_deg_s", 0.0)
        self.declare_parameter(
            "action_delta_scale",
            1.0,
        )
        self.declare_parameter(
            "grasp_delay_steps",
            0,
        )
        self.declare_parameter(
            "pre_grasp_delta_scale",
            1.0,
        )
        self.declare_parameter(
            "grasp_confirm_steps",
            0,
        )
        self.declare_parameter(
            "grasp_max_delta_norm",
            0.0,
        )
        self.declare_parameter(
            "grasp_min_elapsed_steps",
            0,
        )
        self.declare_parameter(
            "grasp_min_motion_rad",
            0.0,
        )
        self.declare_parameter("enable_gripper", True)
        self.declare_parameter("image_target_height", 0)
        self.declare_parameter("image_target_width", 0)
        self.declare_parameter(
            "state_target_dim",
            0,
        )
        self.declare_parameter("ee_pose_topic", "/indy/ee_pose")
        self.declare_parameter("use_tf_ee_pose", True)
        self.declare_parameter("ee_tf_parent_frame", "world")
        self.declare_parameter("ee_tf_child_frame", "tcp")
        self.declare_parameter("fk_urdf_path", "")
        self.declare_parameter("fk_tcp_frame", "tcp")
        self.declare_parameter(
            "fk_joint_names",
            "joint0,joint1,joint2,joint3,joint4,joint5",
        )
        self.declare_parameter("dry_run", False)
        self.declare_parameter("autonomy_enabled", False)
        self.declare_parameter("use_zmq_sidecar", True)
        self.declare_parameter("zmq_endpoint", "tcp://127.0.0.1:5560")
        self.declare_parameter("indy_prep_joint_teleop", True)
        self.declare_parameter("indy_prep_joint_teleop_code", _DEFAULT_MSG_TELE_JOINT_ABS)
        self.declare_parameter("indy_prep_task_teleop_code", _DEFAULT_MSG_TELE_TASK_RLT)

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        model_type = self.get_parameter("model_type").get_parameter_value().string_value
        dataset_repo_id = self.get_parameter("dataset_repo_id").get_parameter_value().string_value
        dataset_root_str = self.get_parameter("dataset_root").get_parameter_value().string_value
        task = self.get_parameter("task").get_parameter_value().string_value
        device = self.get_parameter("device").get_parameter_value().string_value
        inference_hz = self.get_parameter("inference_hz").get_parameter_value().double_value
        sync_slop = self.get_parameter("sync_slop").get_parameter_value().double_value
        control_mode = (
            self.get_parameter("control_mode").get_parameter_value().string_value.strip().lower()
        )
        if control_mode in ("ee_pose", "task", "task_relative"):
            control_mode = "cartesian"
        if control_mode not in ("joint", "cartesian"):
            self.get_logger().warn(
                f"지원하지 않는 control_mode={control_mode!r}; joint 모드로 대체합니다."
            )
            control_mode = "joint"
        self._control_mode = control_mode
        trajectory_topic = self.get_parameter("trajectory_topic").get_parameter_value().string_value
        cartesian_pose_topic = self.get_parameter("cartesian_pose_topic").get_parameter_value().string_value
        traj_sec = self.get_parameter("trajectory_horizon_sec").get_parameter_value().double_value
        self._max_delta = float(self.get_parameter("max_delta_rad").get_parameter_value().double_value)
        self._max_joint_speed = float(
            self.get_parameter("max_joint_speed_rad_s").get_parameter_value().double_value
        )
        self._max_cart_delta_mm = float(
            self.get_parameter("max_delta_mm").get_parameter_value().double_value
        )
        if self._max_cart_delta_mm <= 0.0:
            self.get_logger().warn("max_delta_mm<=0 이므로 2.0mm로 대체합니다.")
            self._max_cart_delta_mm = 2.0
        self._max_cart_delta_deg = float(
            self.get_parameter("max_delta_deg").get_parameter_value().double_value
        )
        if self._max_cart_delta_deg <= 0.0:
            self.get_logger().warn("max_delta_deg<=0 이므로 2.0deg로 대체합니다.")
            self._max_cart_delta_deg = 2.0
        self._max_cartesian_speed = float(
            self.get_parameter("max_cartesian_speed_mm_s").get_parameter_value().double_value
        )
        self._max_angular_speed = float(
            self.get_parameter("max_angular_speed_deg_s").get_parameter_value().double_value
        )
        self._period_sec = 1.0 / max(1.0, float(inference_hz))
        self._action_delta_scale = float(
            self.get_parameter("action_delta_scale").get_parameter_value().double_value
        )
        if self._action_delta_scale <= 0.0:
            self.get_logger().warn("action_delta_scale<=0 이므로 1.0으로 대체합니다.")
            self._action_delta_scale = 1.0
        self._grasp_delay_steps = max(
            0,
            int(self.get_parameter("grasp_delay_steps").get_parameter_value().integer_value),
        )
        self._pre_grasp_delta_scale = float(
            self.get_parameter("pre_grasp_delta_scale").get_parameter_value().double_value
        )
        if self._pre_grasp_delta_scale <= 0.0:
            self.get_logger().warn("pre_grasp_delta_scale<=0 이므로 1.0으로 대체합니다.")
            self._pre_grasp_delta_scale = 1.0
        self._grasp_confirm_steps = max(
            0,
            int(self.get_parameter("grasp_confirm_steps").get_parameter_value().integer_value),
        )
        self._grasp_max_delta_norm = max(
            0.0,
            float(self.get_parameter("grasp_max_delta_norm").get_parameter_value().double_value),
        )
        self._grasp_min_elapsed_steps = max(
            0,
            int(self.get_parameter("grasp_min_elapsed_steps").get_parameter_value().integer_value),
        )
        self._grasp_min_motion_rad = max(
            0.0,
            float(self.get_parameter("grasp_min_motion_rad").get_parameter_value().double_value),
        )
        img_th = int(self.get_parameter("image_target_height").get_parameter_value().integer_value)
        img_tw = int(self.get_parameter("image_target_width").get_parameter_value().integer_value)
        self._state_target_dim = int(self.get_parameter("state_target_dim").get_parameter_value().integer_value)
        ee_pose_topic = self.get_parameter("ee_pose_topic").get_parameter_value().string_value
        self._img_resize_hw: Optional[tuple[int, int]] = None
        self._cv2_resize = None
        if img_th > 0 and img_tw > 0:
            self._img_resize_hw = (img_th, img_tw)
            try:
                import cv2

                self._cv2_resize = cv2
            except ImportError:
                self.get_logger().error(
                    "image_target_height/width가 설정됐지만 OpenCV(cv2)가 없어 리사이즈를 건너뜁니다."
                )
        self._dry_run = bool(self.get_parameter("dry_run").get_parameter_value().bool_value)
        self._autonomy_enabled = bool(self.get_parameter("autonomy_enabled").get_parameter_value().bool_value)
        self._enable_gripper = bool(self.get_parameter("enable_gripper").get_parameter_value().bool_value)
        use_zmq = bool(self.get_parameter("use_zmq_sidecar").get_parameter_value().bool_value)
        zmq_endpoint = self.get_parameter("zmq_endpoint").get_parameter_value().string_value

        self._cv_bridge = CvBridge()
        self._backend: Optional[Union[LeRobotActBackend, ZmqLerobotClient]] = None
        self._joint_names: List[str] = []
        self._obs_lock = threading.Lock()
        self._latest_obs: Optional[dict[str, np.ndarray]] = None
        self._latest_ee_pose6: Optional[np.ndarray] = None
        # 이산 그리퍼 모드(0~4). 피드백 없이도 학습 시 gripper_state 슬롯과 맞추기 위해 유지.
        self._last_grip_cmd: int = GRIP_HOLD
        self._pending_grasp_ticks = 0
        self._grasp_confirm_count = 0
        self._grasp_delay_done = False
        self._start_q: Optional[np.ndarray] = None
        self._relative_pose = np.zeros((6,), dtype=np.float64)
        self._gripper_disabled_warned = False
        self._grasp_elapsed_block_warn_tick = -10_000
        self._grasp_motion_block_warn_tick = -10_000
        self._tf_buffer: Optional[Any] = None
        self._tf_listener: Optional[Any] = None
        self._fk: Optional[Any] = None
        self._use_tf_ee = False
        self._ee_tf_parent = "world"
        self._ee_tf_child = "tcp"
        self._ee_warn_last_ns = 0
        self._ee6_warn_last_ns = 0
        self._tick_count = 0
        self._indy_prep_done = False
        self._indy_prep_pending = False
        self._indy_prep_enabled = bool(
            self.get_parameter("indy_prep_joint_teleop").get_parameter_value().bool_value
        )
        indy_joint_code = int(
            self.get_parameter("indy_prep_joint_teleop_code").get_parameter_value().integer_value
        )
        indy_task_code = int(
            self.get_parameter("indy_prep_task_teleop_code").get_parameter_value().integer_value
        )
        if self._control_mode == "cartesian":
            self._indy_prep_code = indy_task_code
            self._indy_prep_mode_label = "task-relative teleop"
        else:
            self._indy_prep_code = indy_joint_code
            self._indy_prep_mode_label = "joint absolute teleop"
        self._indy_srv = self.create_client(IndyService, "indy_srv")

        if model_type != "lerobot":
            self.get_logger().error(f"지원하지 않는 model_type={model_type} (lerobot 만 지원).")
            return

        if use_zmq:
            try:
                self._backend = ZmqLerobotClient(zmq_endpoint)
                self.get_logger().info(
                    f"ZMQ 사이드카 → {zmq_endpoint} | "
                    f"터미널에서 먼저: zmq_act_server --model-path .../checkpoints/last --bind {zmq_endpoint}"
                )
            except Exception as e:
                self.get_logger().error(f"ZMQ 클라이언트 생성 실패: {e}")
                return
        else:
            if not model_path:
                self.get_logger().warn("embedded 모드인데 model_path 비어 있음.")
                return
            try:
                pretrained_dir = resolve_pretrained_model_dir(model_path)
            except FileNotFoundError as e:
                self.get_logger().error(str(e))
                return

            ds_root = dataset_root_str.strip()
            if not ds_root:
                ds_root = read_dataset_root_from_train_config(pretrained_dir)
            if not ds_root:
                self.get_logger().error(
                    "dataset_root가 비어 있고 train_config.json에서도 읽지 못했습니다. "
                    "파라미터 dataset_root에 LeRobot v3 데이터셋 루트를 주세요."
                )
                return

            self.get_logger().info(f"Loading ACT (embedded py) from {pretrained_dir} (dataset_root={ds_root})")
            try:
                self._backend = LeRobotActBackend(
                    pretrained_model_dir=pretrained_dir,
                    dataset_repo_id=dataset_repo_id,
                    dataset_root=Path(ds_root),
                    device=device,
                    task=task,
                )
            except ImportError as e:
                self.get_logger().error(
                    f"embedded 모드에서 LeRobot 로드 실패: {e}. "
                    "기본 use_zmq_sidecar:=true 와 zmq_act_server 사용을 권장합니다."
                )
                return
            except Exception as e:
                self.get_logger().error(f"모델 로드 실패: {e}")
                return

        if self._state_target_dim >= 26:
            self._use_tf_ee = bool(
                self.get_parameter("use_tf_ee_pose").get_parameter_value().bool_value
            )
            self._ee_tf_parent = (
                self.get_parameter("ee_tf_parent_frame").get_parameter_value().string_value.strip()
                or "world"
            )
            self._ee_tf_child = (
                self.get_parameter("ee_tf_child_frame").get_parameter_value().string_value.strip() or "tcp"
            )
            fk_path = self.get_parameter("fk_urdf_path").get_parameter_value().string_value.strip()
            fk_tcp = (
                self.get_parameter("fk_tcp_frame").get_parameter_value().string_value.strip() or "tcp"
            )
            fk_jn = self.get_parameter("fk_joint_names").get_parameter_value().string_value
            jn_list = [x.strip() for x in fk_jn.split(",") if x.strip()]

            if self._use_tf_ee:
                self._tf_buffer = tf2_ros.Buffer(cache_time=RclDuration(seconds=60.0))
                self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self, spin_thread=True)
                self.get_logger().info(
                    f"ee_pose(26D): TF lookup {self._ee_tf_parent} <- {self._ee_tf_child} "
                    f"(Pinocchio fallback={'yes' if fk_path else 'no'})"
                )
            if fk_path:
                fk_mod_path = (
                    Path(__file__).resolve().parents[3]
                    / "ai"
                    / "data_conversion"
                    / "npz_to_lerobot"
                    / "indy7_tcp_fk.py"
                )
                if not fk_mod_path.is_file():
                    self.get_logger().error(f"indy7_tcp_fk.py 없음: {fk_mod_path}")
                else:
                    try:
                        spec = importlib.util.spec_from_file_location("indy7_tcp_fk", str(fk_mod_path))
                        if spec is None or spec.loader is None:
                            raise RuntimeError("importlib spec failed")
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        self._fk = mod.Indy7TcpFk(fk_path, tcp_frame=fk_tcp, joint_names=jn_list)
                        self.get_logger().info(f"ee_pose: Pinocchio FK OK ({fk_path})")
                    except Exception as e:
                        self.get_logger().error(f"Pinocchio FK 초기화 실패: {e}")
            if not self._use_tf_ee and self._fk is None:
                self.get_logger().warn(
                    "state_target_dim>=26 인데 use_tf_ee_pose=false 이고 fk_urdf_path가 비어 있음. "
                    "ee_pose(7)는 0으로 남습니다."
                )

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(Float64MultiArray, ee_pose_topic, self._ee_pose6_cb, qos)
        self.joint_sub = message_filters.Subscriber(self, JointState, "/joint_states")
        self.wrist_rgb_sub = message_filters.Subscriber(
            self, Image, "/wrist_camera/camera/color/image_raw"
        )
        self.wrist_depth_sub = message_filters.Subscriber(
            self, Image, "/wrist_camera/camera/aligned_depth_to_color/image_raw"
        )
        self.overhead_rgb_sub = message_filters.Subscriber(
            self, Image, "/overhead_camera/camera/color/image_raw"
        )
        self.overhead_depth_sub = message_filters.Subscriber(
            self, Image, "/overhead_camera/camera/aligned_depth_to_color/image_raw"
        )
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [
                self.joint_sub,
                self.wrist_rgb_sub,
                self.wrist_depth_sub,
                self.overhead_rgb_sub,
                self.overhead_depth_sub,
            ],
            queue_size=10,
            slop=sync_slop,
        )
        self.sync.registerCallback(self._sync_callback)

        self._traj_pub = self.create_publisher(JointTrajectory, trajectory_topic, qos)
        self._cartesian_pub = self.create_publisher(Float64MultiArray, cartesian_pose_topic, qos)
        self.gripper_grasp = self.create_client(Trigger, "/gripper/grasp")
        self.gripper_open = self.create_client(Trigger, "/gripper/open")
        self.gripper_press = self.create_client(Trigger, "/gripper/press")
        self.gripper_release = self.create_client(Trigger, "/gripper/release")

        self._traj_sec = max(0.05, float(traj_sec))
        self.create_timer(self._period_sec, self._inference_tick)

        extra = (
            f"action_delta_scale={self._action_delta_scale} | "
            f"grasp_delay_steps={self._grasp_delay_steps} | "
            f"pre_grasp_delta_scale={self._pre_grasp_delta_scale} | "
            f"grasp_confirm_steps={self._grasp_confirm_steps} | "
            f"grasp_max_delta_norm={self._grasp_max_delta_norm} | "
            f"grasp_min_elapsed_steps={self._grasp_min_elapsed_steps} | "
            f"grasp_min_motion_rad={self._grasp_min_motion_rad} | "
            f"enable_gripper={self._enable_gripper}"
        )
        if self._control_mode == "cartesian":
            extra += (
                f" | max_delta_mm={self._max_cart_delta_mm} | "
                f"max_delta_deg={self._max_cart_delta_deg} | "
                f"max_cartesian_speed_mm_s={self._max_cartesian_speed} | "
                f"max_angular_speed_deg_s={self._max_angular_speed} | "
                f"ee_pose_topic={ee_pose_topic}"
            )
            output_topic = f"cartesian_pose_topic={cartesian_pose_topic}"
        else:
            extra += (
                f" | max_delta_rad={self._max_delta} | "
                f"max_joint_speed_rad_s={self._max_joint_speed}"
            )
            output_topic = f"trajectory_topic={trajectory_topic}"
        if self._img_resize_hw is not None:
            extra += f" | image_resize={self._img_resize_hw[0]}x{self._img_resize_hw[1]}"
        self.get_logger().info(
            f"추론 {inference_hz}Hz | zmq={use_zmq} | autonomy_enabled={self._autonomy_enabled} | "
            f"dry_run={self._dry_run} | control_mode={self._control_mode} | {output_topic} | {extra}"
        )

    def _lookup_ee_pose7(self, q: np.ndarray) -> Optional[np.ndarray]:
        """TCP pose [x,y,z,qx,qy,qz,qw] in parent frame; TF 우선, 실패 시 Pinocchio FK."""
        if self._tf_buffer is not None and self._use_tf_ee:
            try:
                tfm = self._tf_buffer.lookup_transform(
                    self._ee_tf_parent,
                    self._ee_tf_child,
                    Time(),
                    timeout=RclDuration(seconds=0.05),
                )
                tr = tfm.transform.translation
                rr = tfm.transform.rotation
                return np.array([tr.x, tr.y, tr.z, rr.x, rr.y, rr.z, rr.w], dtype=np.float32)
            except Exception:
                pass
        if self._fk is not None:
            try:
                return self._fk.compute(np.asarray(q, dtype=np.float64))
            except Exception:
                pass
        return None

    def _resize_rgb_if_needed(self, img: np.ndarray) -> np.ndarray:
        if self._img_resize_hw is None or self._cv2_resize is None:
            return img
        th, tw = self._img_resize_hw
        if img.shape[0] == th and img.shape[1] == tw:
            return img
        return self._cv2_resize.resize(img, (tw, th), interpolation=self._cv2_resize.INTER_AREA)

    def _ee_pose6_cb(self, msg: Float64MultiArray) -> None:
        if len(msg.data) >= 6:
            self._latest_ee_pose6 = np.asarray(list(msg.data[:6]), dtype=np.float32)

    def _sync_callback(
        self,
        joint_msg: JointState,
        wrist_rgb_msg: Image,
        wrist_depth_msg: Image,
        overhead_rgb_msg: Image,
        overhead_depth_msg: Image,
    ) -> None:
        if len(joint_msg.name) >= 6:
            self._joint_names = list(joint_msg.name[:6])
        elif not self._joint_names:
            self._joint_names = [f"joint{i}" for i in range(6)]

        try:
            wrist_rgb = self._cv_bridge.imgmsg_to_cv2(wrist_rgb_msg, desired_encoding="rgb8")
            overhead_rgb = self._cv_bridge.imgmsg_to_cv2(overhead_rgb_msg, desired_encoding="rgb8")
            wrist_depth = self._cv_bridge.imgmsg_to_cv2(wrist_depth_msg, desired_encoding="passthrough")
            overhead_depth = self._cv_bridge.imgmsg_to_cv2(overhead_depth_msg, desired_encoding="passthrough")
        except Exception as e:
            self.get_logger().error(f"이미지 변환 실패: {e}")
            return

        wrist_rgb = self._resize_rgb_if_needed(wrist_rgb)
        overhead_rgb = self._resize_rgb_if_needed(overhead_rgb)
        wrist_depth_rgb = self._resize_rgb_if_needed(_depth_to_u8_rgb(wrist_depth))
        overhead_depth_rgb = self._resize_rgb_if_needed(_depth_to_u8_rgb(overhead_depth))

        q = np.array(_joint_vec_to_six(joint_msg.position), dtype=np.float32)
        dq = np.array(_joint_vec_to_six(joint_msg.velocity), dtype=np.float32)
        tau = np.array(_joint_vec_to_six(joint_msg.effort), dtype=np.float32)
        if self._control_mode == "cartesian":
            ee6 = self._latest_ee_pose6
            if ee6 is None:
                ee6 = np.zeros((6,), dtype=np.float32)
                now_ns = self.get_clock().now().nanoseconds
                if now_ns - self._ee6_warn_last_ns > 3_000_000_000:
                    self._ee6_warn_last_ns = now_ns
                    self.get_logger().warn(
                        "cartesian 모델 state는 [q,dq,ee_pose]를 기대하지만 /indy/ee_pose를 아직 받지 못했습니다. "
                        "ee_pose 6D를 0으로 채웁니다."
                    )
            # convert.py cartesian baseline: [joint_positions(6), joint_velocities(6), ee_poses(6)] == 18D
            state_vec = np.concatenate([q, dq, ee6.astype(np.float32)], axis=0)
            if self._state_target_dim >= 19:
                state_vec = np.concatenate(
                    [state_vec, np.array([float(self._last_grip_cmd)], dtype=np.float32)],
                    axis=0,
                )
        else:
            state_vec = np.concatenate([q, dq, tau], axis=0)
        if self._state_target_dim > 0:
            cur_dim = int(state_vec.shape[0])
            if self._state_target_dim > cur_dim:
                pad = np.zeros((self._state_target_dim - cur_dim,), dtype=np.float32)
                state_vec = np.concatenate([state_vec, pad], axis=0)
            elif self._state_target_dim < cur_dim:
                state_vec = state_vec[: self._state_target_dim]
        # convert.py extended: 18 + ee_pose(7) + gripper_state(1) == 26
        if self._control_mode != "cartesian" and self._state_target_dim >= 26 and int(state_vec.shape[0]) >= 26:
            ee7 = self._lookup_ee_pose7(q)
            if ee7 is not None:
                state_vec[18:25] = ee7
            else:
                now_ns = self.get_clock().now().nanoseconds
                if now_ns - self._ee_warn_last_ns > 3_000_000_000:
                    self._ee_warn_last_ns = now_ns
                    self.get_logger().warn(
                        "ee_pose(7)를 TF 또는 Pinocchio로 얻지 못했습니다. "
                        "ee_tf_parent_frame/ee_tf_child_frame, fk_urdf_path, pinocchio 설치를 확인하세요."
                    )
            state_vec[25] = float(self._last_grip_cmd)
        elif self._control_mode != "cartesian" and int(state_vec.shape[0]) > 18:
            state_vec[-1] = float(self._last_grip_cmd)

        obs = {
            "observation.images.front": np.ascontiguousarray(wrist_rgb),
            "observation.images.front_depth": np.ascontiguousarray(wrist_depth_rgb),
            "observation.images.overhead": np.ascontiguousarray(overhead_rgb),
            "observation.images.overhead_depth": np.ascontiguousarray(overhead_depth_rgb),
            "observation.state": state_vec,
        }
        with self._obs_lock:
            self._latest_obs = obs

    def _inference_tick(self) -> None:
        if self._backend is None:
            return
        with self._obs_lock:
            obs = self._latest_obs
        if obs is None:
            return

        self._tick_count += 1
        try:
            action = self._backend.predict(obs)
        except Exception as e:
            self.get_logger().error(f"predict 실패: {e}")
            return

        if action.shape[0] < 7:
            self.get_logger().warn(f"액션 차원 부족: {action.shape}")
            return

        q_now = obs["observation.state"][:6].astype(np.float64)
        if self._start_q is None:
            self._start_q = q_now.copy()
        motion_from_start = float(np.linalg.norm(q_now - self._start_q))

        raw6_base = action[:6].astype(np.float64) * self._action_delta_scale
        if self._control_mode == "cartesian":
            gate_delta = self._clip_cartesian_delta(raw6_base)
        else:
            gate_delta = self._clip_joint_delta(raw6_base)
        gate_delta_norm = float(np.linalg.norm(gate_delta))

        g_raw = float(action[6])
        raw_g_cmd = int(np.clip(np.round(g_raw), 0, 4))
        g_cmd, grasp_gate_active = self._gate_gripper_cmd(
            raw_g_cmd,
            gate_delta_norm,
            motion_from_start,
        )

        raw6 = raw6_base
        if grasp_gate_active:
            raw6 = raw6 * self._pre_grasp_delta_scale
        if self._control_mode == "cartesian":
            delta = self._clip_cartesian_delta(raw6)
        else:
            delta = self._clip_joint_delta(raw6)

        if self._tick_count % 40 == 0:
            if self._control_mode == "cartesian":
                self.get_logger().info(
                    f"cart_delta_xyz_mm=({delta[0]:.2f},{delta[1]:.2f},{delta[2]:.2f}) "
                    f"cart_delta_rpy_deg=({delta[3]:.2f},{delta[4]:.2f},{delta[5]:.2f}) "
                    f"cart_delta_norm={float(np.linalg.norm(delta)):.4f} "
                    f"motion_from_start={motion_from_start:.4f} "
                    f"(scale={self._action_delta_scale}) grip_raw={g_raw:.2f} "
                    f"raw_grip_cmd={raw_g_cmd} grip_cmd={g_cmd} "
                    f"grasp_pending={self._pending_grasp_ticks} "
                    f"grasp_confirm={self._grasp_confirm_count}/{self._grasp_confirm_steps} "
                    f"autonomy={self._autonomy_enabled}"
                )
            else:
                self.get_logger().info(
                    f"delta_norm={float(np.linalg.norm(delta)):.4f} "
                    f"motion_from_start={motion_from_start:.4f} "
                    f"(scale={self._action_delta_scale}) grip_raw={g_raw:.2f} "
                    f"raw_grip_cmd={raw_g_cmd} grip_cmd={g_cmd} "
                    f"grasp_pending={self._pending_grasp_ticks} "
                    f"grasp_confirm={self._grasp_confirm_count}/{self._grasp_confirm_steps} "
                    f"autonomy={self._autonomy_enabled}"
                )

        if self._dry_run or not self._autonomy_enabled:
            return

        if not self._prepare_indy_teleop_if_needed():
            return

        if self._control_mode == "cartesian":
            self._publish_cartesian_delta(delta)
        else:
            self._publish_joint_targets(q_now + delta)
        self._maybe_gripper_service(g_cmd)

    def _clip_joint_delta(self, raw6: np.ndarray) -> np.ndarray:
        delta = np.clip(np.asarray(raw6, dtype=np.float64), -self._max_delta, self._max_delta)
        if self._max_joint_speed > 0.0:
            speed_delta_limit = float(self._max_joint_speed) * float(self._period_sec)
            delta = np.clip(delta, -speed_delta_limit, speed_delta_limit)
        return delta

    def _clip_cartesian_delta(self, raw6: np.ndarray) -> np.ndarray:
        delta = np.asarray(raw6, dtype=np.float64).copy()
        delta[:3] = np.clip(
            delta[:3],
            -self._max_cart_delta_mm,
            self._max_cart_delta_mm,
        )
        delta[3:6] = np.clip(
            delta[3:6],
            -self._max_cart_delta_deg,
            self._max_cart_delta_deg,
        )
        if self._max_cartesian_speed > 0.0:
            linear_limit = float(self._max_cartesian_speed) * float(self._period_sec)
            delta[:3] = np.clip(delta[:3], -linear_limit, linear_limit)
        if self._max_angular_speed > 0.0:
            angular_limit = float(self._max_angular_speed) * float(self._period_sec)
            delta[3:6] = np.clip(delta[3:6], -angular_limit, angular_limit)
        return delta

    def _prepare_indy_teleop_if_needed(self) -> bool:
        if not self._indy_prep_enabled or self._indy_prep_done:
            return True
        if self._indy_prep_pending:
            return False
        if not self._indy_srv.wait_for_service(timeout_sec=0.0):
            if self._tick_count % 40 == 0:
                self.get_logger().warn("indy_srv 대기 중 — 팔 명령은 서비스 준비 후 전송됩니다.")
            return False

        self._indy_prep_pending = True
        req = IndyService.Request()
        req.data = self._indy_prep_code
        fut = self._indy_srv.call_async(req)

        def _on_prep_done(f) -> None:
            try:
                r = f.result()
                if r.success:
                    self._indy_prep_done = True
                    if self._control_mode == "cartesian":
                        self._relative_pose[:] = 0.0
                    self.get_logger().info(
                        f"Indy {self._indy_prep_mode_label} 준비 완료 "
                        f"(indy_srv data={self._indy_prep_code})."
                    )
                else:
                    self.get_logger().error(
                        f"indy_srv 준비 실패: {r.message} (data={self._indy_prep_code})"
                    )
            except Exception as ex:
                self.get_logger().error(f"indy_srv 호출 예외: {ex}")
            finally:
                self._indy_prep_pending = False

        fut.add_done_callback(_on_prep_done)
        return False

    def _gate_gripper_cmd(
        self,
        raw_cmd: int,
        delta_norm: float,
        motion_from_start: float,
    ) -> tuple[int, bool]:
        """Hold grasp until the command is stable and the arm is near a settled target."""
        if (
            self._grasp_delay_steps <= 0
            and self._grasp_confirm_steps <= 0
            and self._grasp_max_delta_norm <= 0.0
            and self._grasp_min_elapsed_steps <= 0
            and self._grasp_min_motion_rad <= 0.0
        ):
            return raw_cmd, False
        if self._last_grip_cmd == GRIP_GRASP:
            return raw_cmd, False

        if raw_cmd != GRIP_GRASP:
            if self._pending_grasp_ticks > 0 or self._grasp_confirm_count > 0:
                self.get_logger().info(
                    f"grasp gate 취소: raw_grip_cmd={raw_cmd} "
                    f"pending={self._pending_grasp_ticks} "
                    f"confirm={self._grasp_confirm_count}/{self._grasp_confirm_steps}"
                )
            self._pending_grasp_ticks = 0
            self._grasp_confirm_count = 0
            self._grasp_delay_done = False
            return raw_cmd, False

        if self._tick_count < self._grasp_min_elapsed_steps:
            if self._tick_count - self._grasp_elapsed_block_warn_tick >= 20:
                self._grasp_elapsed_block_warn_tick = self._tick_count
                self.get_logger().info(
                    f"grasp gate 보류: elapsed={self._tick_count}/"
                    f"{self._grasp_min_elapsed_steps} ticks"
                )
            return self._last_grip_cmd, True

        if (
            self._grasp_min_motion_rad > 0.0
            and motion_from_start < self._grasp_min_motion_rad
        ):
            if self._tick_count - self._grasp_motion_block_warn_tick >= 20:
                self._grasp_motion_block_warn_tick = self._tick_count
                self.get_logger().info(
                    f"grasp gate 보류: motion_from_start={motion_from_start:.4f} "
                    f"< {self._grasp_min_motion_rad:.4f}"
                )
            return self._last_grip_cmd, True

        if self._pending_grasp_ticks > 0:
            self._pending_grasp_ticks -= 1
            if self._pending_grasp_ticks <= 0:
                self._grasp_delay_done = True
                self.get_logger().info("grasp delay 완료: 안정 조건 확인 시작")
            return self._last_grip_cmd, True

        if (
            self._pending_grasp_ticks == 0
            and self._grasp_confirm_count == 0
            and self._grasp_delay_steps > 0
            and not self._grasp_delay_done
        ):
            self._pending_grasp_ticks = self._grasp_delay_steps
            self.get_logger().info(
                f"grasp delay 시작: {self._grasp_delay_steps} ticks 동안 그리퍼 hold"
            )
            return self._last_grip_cmd, True

        if self._grasp_max_delta_norm > 0.0 and delta_norm > self._grasp_max_delta_norm:
            if self._grasp_confirm_count > 0:
                self.get_logger().info(
                    f"grasp gate 리셋: 아직 팔 이동 중 "
                    f"delta_norm={delta_norm:.4f} > {self._grasp_max_delta_norm:.4f}"
                )
            self._grasp_confirm_count = 0
            return self._last_grip_cmd, True

        self._grasp_confirm_count += 1
        required = max(1, self._grasp_confirm_steps)
        if self._grasp_confirm_count >= required:
            self.get_logger().info(
                f"grasp gate 통과: confirm={self._grasp_confirm_count}/{required}, "
                f"delta_norm={delta_norm:.4f}"
            )
            self._grasp_confirm_count = 0
            self._grasp_delay_done = False
            return GRIP_GRASP, False

        return self._last_grip_cmd, True

    def _publish_joint_targets(self, positions: np.ndarray) -> None:
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = self._joint_names
        pt = JointTrajectoryPoint()
        pt.positions = [float(x) for x in positions]
        ns = int(self._traj_sec * 1e9)
        pt.time_from_start = Duration(sec=ns // 1_000_000_000, nanosec=ns % 1_000_000_000)
        msg.points = [pt]
        self._traj_pub.publish(msg)

    def _publish_cartesian_delta(self, delta: np.ndarray) -> None:
        self._relative_pose = self._relative_pose + np.asarray(delta, dtype=np.float64)
        msg = Float64MultiArray()
        msg.data = [float(x) for x in self._relative_pose]
        self._cartesian_pub.publish(msg)

    def _maybe_gripper_service(self, cmd: int) -> None:
        if cmd == self._last_grip_cmd:
            return
        if not self._enable_gripper:
            if not self._gripper_disabled_warned:
                self._gripper_disabled_warned = True
                self.get_logger().warn("enable_gripper=false: 그리퍼 서비스 호출을 차단합니다.")
            return
        if cmd == GRIP_HOLD:
            self._last_grip_cmd = cmd
            return
        clients = {
            GRIP_GRASP: self.gripper_grasp,
            GRIP_OPEN: self.gripper_open,
            GRIP_PRESS: self.gripper_press,
            GRIP_RELEASE: self.gripper_release,
        }
        cli = clients.get(cmd)
        if cli is None:
            return
        if not cli.service_is_ready():
            self.get_logger().warn(f"그리퍼 서비스 대기 중: {cli.srv_name}")
            return
        fut = cli.call_async(Trigger.Request())
        self._last_grip_cmd = cmd

        def _on_gripper_done(f) -> None:
            try:
                r = f.result()
                if not r.success:
                    self.get_logger().warn(f"{cli.srv_name} 실패: {r.message}")
            except Exception as ex:
                self.get_logger().warn(f"{cli.srv_name} 호출 예외: {ex}")

        fut.add_done_callback(_on_gripper_done)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = InferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
