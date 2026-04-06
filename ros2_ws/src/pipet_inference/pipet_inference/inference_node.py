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

관측: /joint_states 6축 + 손목/오버헤드 RGB. 액션: delta_q(6) + gripper 0~4.

안전: 기본 autonomy_enabled=false. dry_run=true 로 명령 없이 로그만.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import rclpy
from builtin_interfaces.msg import Duration
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image, JointState
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

import message_filters

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
        self.declare_parameter("trajectory_topic", "/joint_trajectory_controller/joint_trajectory")
        self.declare_parameter("trajectory_horizon_sec", 0.12)
        self.declare_parameter("max_delta_rad", 0.25)
        self.declare_parameter("dry_run", False)
        self.declare_parameter("autonomy_enabled", False)
        self.declare_parameter("use_zmq_sidecar", True)
        self.declare_parameter("zmq_endpoint", "tcp://127.0.0.1:5560")

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        model_type = self.get_parameter("model_type").get_parameter_value().string_value
        dataset_repo_id = self.get_parameter("dataset_repo_id").get_parameter_value().string_value
        dataset_root_str = self.get_parameter("dataset_root").get_parameter_value().string_value
        task = self.get_parameter("task").get_parameter_value().string_value
        device = self.get_parameter("device").get_parameter_value().string_value
        inference_hz = self.get_parameter("inference_hz").get_parameter_value().double_value
        sync_slop = self.get_parameter("sync_slop").get_parameter_value().double_value
        trajectory_topic = self.get_parameter("trajectory_topic").get_parameter_value().string_value
        traj_sec = self.get_parameter("trajectory_horizon_sec").get_parameter_value().double_value
        self._max_delta = float(self.get_parameter("max_delta_rad").get_parameter_value().double_value)
        self._dry_run = bool(self.get_parameter("dry_run").get_parameter_value().bool_value)
        self._autonomy_enabled = bool(self.get_parameter("autonomy_enabled").get_parameter_value().bool_value)
        use_zmq = bool(self.get_parameter("use_zmq_sidecar").get_parameter_value().bool_value)
        zmq_endpoint = self.get_parameter("zmq_endpoint").get_parameter_value().string_value

        self._cv_bridge = CvBridge()
        self._backend: Optional[Union[LeRobotActBackend, ZmqLerobotClient]] = None
        self._joint_names: List[str] = []
        self._obs_lock = threading.Lock()
        self._latest_obs: Optional[dict[str, np.ndarray]] = None
        self._last_grip_cmd: Optional[int] = None
        self._tick_count = 0

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

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.joint_sub = message_filters.Subscriber(self, JointState, "/joint_states")
        self.wrist_rgb_sub = message_filters.Subscriber(
            self, Image, "/wrist_camera/camera/color/image_raw"
        )
        self.overhead_rgb_sub = message_filters.Subscriber(
            self, Image, "/overhead_camera/camera/color/image_raw"
        )
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.joint_sub, self.wrist_rgb_sub, self.overhead_rgb_sub],
            queue_size=10,
            slop=sync_slop,
        )
        self.sync.registerCallback(self._sync_callback)

        self._traj_pub = self.create_publisher(JointTrajectory, trajectory_topic, qos)
        self.gripper_grasp = self.create_client(Trigger, "/gripper/grasp")
        self.gripper_open = self.create_client(Trigger, "/gripper/open")
        self.gripper_press = self.create_client(Trigger, "/gripper/press")
        self.gripper_release = self.create_client(Trigger, "/gripper/release")

        self._traj_sec = max(0.05, float(traj_sec))
        period = 1.0 / max(1.0, inference_hz)
        self.create_timer(period, self._inference_tick)

        self.get_logger().info(
            f"추론 {inference_hz}Hz | zmq={use_zmq} | autonomy_enabled={self._autonomy_enabled} | "
            f"dry_run={self._dry_run} | trajectory_topic={trajectory_topic}"
        )

    def _sync_callback(self, joint_msg: JointState, wrist_rgb_msg: Image, overhead_rgb_msg: Image) -> None:
        if len(joint_msg.name) >= 6:
            self._joint_names = list(joint_msg.name[:6])
        elif not self._joint_names:
            self._joint_names = [f"joint{i}" for i in range(6)]

        try:
            wrist_rgb = self._cv_bridge.imgmsg_to_cv2(wrist_rgb_msg, desired_encoding="rgb8")
            overhead_rgb = self._cv_bridge.imgmsg_to_cv2(overhead_rgb_msg, desired_encoding="rgb8")
        except Exception as e:
            self.get_logger().error(f"이미지 변환 실패: {e}")
            return

        q = np.array(_joint_vec_to_six(joint_msg.position), dtype=np.float32)
        dq = np.array(_joint_vec_to_six(joint_msg.velocity), dtype=np.float32)
        tau = np.array(_joint_vec_to_six(joint_msg.effort), dtype=np.float32)
        state_vec = np.concatenate([q, dq, tau], axis=0)

        obs = {
            "observation.images.front": np.ascontiguousarray(wrist_rgb),
            "observation.images.overhead": np.ascontiguousarray(overhead_rgb),
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

        delta = np.clip(action[:6], -self._max_delta, self._max_delta)
        g_raw = float(action[6])
        g_cmd = int(np.clip(np.round(g_raw), 0, 4))

        q_now = obs["observation.state"][:6].astype(np.float64)
        q_tgt = q_now + delta.astype(np.float64)

        if self._tick_count % 40 == 0:
            self.get_logger().info(
                f"delta_norm={float(np.linalg.norm(delta)):.4f} grip_cmd={g_cmd} autonomy={self._autonomy_enabled}"
            )

        if self._dry_run or not self._autonomy_enabled:
            return

        self._publish_joint_targets(q_tgt)
        self._maybe_gripper_service(g_cmd)

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

    def _maybe_gripper_service(self, cmd: int) -> None:
        if cmd == self._last_grip_cmd:
            return
        self._last_grip_cmd = cmd
        if cmd == GRIP_HOLD:
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
        fut.add_done_callback(lambda _f: None)


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
