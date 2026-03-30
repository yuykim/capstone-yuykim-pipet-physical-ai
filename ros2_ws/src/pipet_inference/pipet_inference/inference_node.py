#!/usr/bin/env python3
"""
Pipet Physical AI 추론(배포) 노드.

역할:
  - 학습된 LeRobot ACT policy를 로드한다.
  - 현재 센서 관측(관절 + 카메라)을 입력으로 action을 예측한다.
  - 예측된 action을 실제 로봇 명령으로 변환해 Indy7/Mark7에 전달한다.

입력(구독):
  - /joint_states
  - /wrist_camera/camera/color/image_raw
  - /overhead_camera/camera/color/image_raw

출력:
  - /joint_trajectory_controller/joint_trajectory (Indy7 관절 목표치)
  - /gripper/grasp|open|press|release (Mark7 프리셋 서비스)

현재 baseline 가정:
  - 변환된 LeRobotDataset이 아래 feature 키를 가진다.
      observation.images.front
      observation.images.overhead
      observation.state = [q(6), dq(6), tau(6)] concat (18)
      action = [delta_q(6), gripper_cmd(1)] concat (7)
  - Indy7은 `/joint_trajectory_controller/joint_trajectory` 토픽을 통해 position setpoint를 받는다.
    (만약 드라이버 인터페이스가 다르면 `_tick_arm()`만 바꾸면 된다.)
"""

from __future__ import annotations

import time
from typing import Optional

import numpy as np
import rclpy
from builtin_interfaces.msg import Duration
from cv_bridge import CvBridge
from control_msgs.action import FollowJointTrajectory  # noqa: F401  (kept for future action-based control)
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import Image, JointState
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.policies.factory import make_pre_post_processors, make_policy
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.utils.control_utils import predict_action
import torch


class InferenceNode(Node):
    def __init__(self):
        super().__init__("inference_node")

        # ROS 파라미터 (launch에서 주입)
        self.declare_parameter("policy_path", "")
        self.declare_parameter("dataset_root", "")
        self.declare_parameter("dataset_repo_id", "pipet_dataset")
        self.declare_parameter("task", "Pick up the pipette")
        self.declare_parameter("robot_type", "pipet")
        self.declare_parameter("inference_hz", 15.0)
        self.declare_parameter("use_amp", False)
        self.declare_parameter("device", "cuda" if torch.cuda.is_available() else "cpu")

        policy_path = self.get_parameter("policy_path").get_parameter_value().string_value
        dataset_root = self.get_parameter("dataset_root").get_parameter_value().string_value
        dataset_repo_id = self.get_parameter("dataset_repo_id").get_parameter_value().string_value
        task = self.get_parameter("task").get_parameter_value().string_value
        robot_type = self.get_parameter("robot_type").get_parameter_value().string_value
        inference_hz = self.get_parameter("inference_hz").get_parameter_value().double_value
        use_amp = self.get_parameter("use_amp").get_parameter_value().bool_value
        device_str = self.get_parameter("device").get_parameter_value().string_value

        self._task = task
        self._robot_type = robot_type
        self._use_amp = bool(use_amp)
        self._device = torch.device(device_str)
        self._dt = 1.0 / max(1e-6, float(inference_hz))

        self.get_logger().info(
            f"InferenceNode init: policy_path={policy_path}, dataset_root={dataset_root}, "
            f"hz={inference_hz}, device={self._device}, amp={self._use_amp}"
        )

        if not policy_path or not dataset_root:
            self.get_logger().warn("Missing policy_path or dataset_root. Node will idle.")
            return

        # 데이터셋(meta/stats.json)을 읽어서 정규화 통계(stats)를 확보한다.
        # LeRobot의 pre/post processor가 이 stats를 사용해 normalize/unnormalize를 수행한다.
        dataset = LeRobotDataset(
            repo_id=dataset_repo_id,
            root=dataset_root,
            download_videos=False,
        )
        self._dataset_meta = dataset.meta

        # checkpoint 폴더에서 ACT 설정을 읽고, dataset meta 기반으로 policy를 구성한다.
        # (입력/출력 feature shape는 dataset에서 자동 유추)
        cfg = ACTConfig.from_pretrained(policy_path)
        cfg.device = str(self._device)
        cfg.pretrained_path = str(policy_path)

        self._policy = make_policy(cfg, ds_meta=dataset.meta)
        self._preprocessor, self._postprocessor = make_pre_post_processors(
            policy_cfg=cfg, dataset_stats=dataset.meta.stats
        )

        # output_features는 make_policy()에서 dataset meta로부터 채워진다.
        action_dim = None
        if cfg.output_features and "action" in cfg.output_features:
            action_dim = cfg.output_features["action"].shape[0]
        self.get_logger().info(f"Policy loaded. action_dim={action_dim}")

        # 구독: 로봇 상태 + 두 카메라
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self._latest_joints: Optional[JointState] = None
        self._latest_front_rgb: Optional[np.ndarray] = None  # HWC uint8
        self._latest_overhead_rgb: Optional[np.ndarray] = None  # HWC uint8
        self._joint_names: Optional[list[str]] = None

        self.cv_bridge = CvBridge()

        self.create_subscription(JointState, "/joint_states", self._joint_cb, qos)
        self.create_subscription(
            Image, "/wrist_camera/camera/color/image_raw", self._wrist_rgb_cb, qos
        )
        self.create_subscription(
            Image, "/overhead_camera/camera/color/image_raw", self._overhead_rgb_cb, qos
        )

        # 퍼블리셔: Indy7 관절 목표치(토픽 방식, 피드백 없음)
        self._joint_traj_pub = self.create_publisher(
            JointTrajectory, "/joint_trajectory_controller/joint_trajectory", qos
        )

        # 서비스 클라이언트: Mark7 프리셋 (Trigger)
        # RF 통신/하드웨어 제약을 고려해:
        # - 같은 명령 연속 호출 방지
        # - 최소 호출 간격(min_interval) 적용
        self._gripper_last_cmd: Optional[int] = None
        self._last_gripper_call_ts = 0.0
        self._gripper_min_interval_s = 0.2

        self._client_grasp = self.create_client(Trigger, "/gripper/grasp")
        self._client_open = self.create_client(Trigger, "/gripper/open")
        self._client_press = self.create_client(Trigger, "/gripper/press")
        self._client_release = self.create_client(Trigger, "/gripper/release")

        # gripper 서비스가 없으면 중간에 계속 timeout 날 수 있으니, 시작 시점에 한 번 대기한다.
        for name, client in [
            ("grasp", self._client_grasp),
            ("open", self._client_open),
            ("press", self._client_press),
            ("release", self._client_release),
        ]:
            if not client.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn(f"Gripper service {name} not ready.")

        # 추론 루프: inference_hz 주기로 tick
        self._last_action_ts = 0.0
        self._last_sent_q_target: Optional[np.ndarray] = None
        self.create_timer(self._dt, self._inference_tick)

    # ---------------- callbacks (구독 콜백) ----------------
    def _joint_cb(self, msg: JointState):
        self._latest_joints = msg
        if self._joint_names is None and msg.name and len(msg.name) >= 6:
            self._joint_names = list(msg.name[:6])

    def _wrist_rgb_cb(self, msg: Image):
        try:
            img = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
            self._latest_front_rgb = img  # HWC uint8
        except Exception as e:  # pragma: no cover
            self.get_logger().error(f"Failed to decode wrist RGB image: {e}")

    def _overhead_rgb_cb(self, msg: Image):
        try:
            img = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
            self._latest_overhead_rgb = img  # HWC uint8
        except Exception as e:  # pragma: no cover
            self.get_logger().error(f"Failed to decode overhead RGB image: {e}")

    # ---------------- inference + control (추론/제어 로직) ----------------
    def _build_state_vector(self, joints: JointState) -> np.ndarray:
        """
        observation.state = concat(q[0..5], dq[0..5], tau[0..5]) -> (18,)

        JointState의 velocity/effort가 비어 있는 경우도 있어, (6,)으로 패딩한다.
        """
        q = np.array(joints.position, dtype=np.float32)
        dq = np.array(joints.velocity, dtype=np.float32) if joints.velocity else np.zeros(0, dtype=np.float32)
        tau = np.array(joints.effort, dtype=np.float32) if joints.effort else np.zeros(0, dtype=np.float32)

        def pad_to_6(x: np.ndarray) -> np.ndarray:
            if x.size >= 6:
                return x[:6]
            if x.size == 0:
                return np.zeros(6, dtype=np.float32)
            return np.pad(x, (0, 6 - x.size), mode="constant").astype(np.float32)

        q6 = pad_to_6(q)
        dq6 = pad_to_6(dq)
        tau6 = pad_to_6(tau)

        return np.concatenate([q6, dq6, tau6], axis=0).astype(np.float32)

    def _tick_gripper(self, gripper_cmd: int) -> None:
        # gripper_cmd 매핑(수집기 로깅 규약과 동일):
        #   0=유지, 1=잡기, 2=펴기, 3=누르기, 4=엄지 펴기
        if gripper_cmd == 0:
            return
        if self._gripper_last_cmd == gripper_cmd:
            return

        now = time.time()
        if now - self._last_gripper_call_ts < self._gripper_min_interval_s:
            return

        client = None
        if gripper_cmd == 1:
            client = self._client_grasp
        elif gripper_cmd == 2:
            client = self._client_open
        elif gripper_cmd == 3:
            client = self._client_press
        elif gripper_cmd == 4:
            client = self._client_release

        if client is None:
            return

        req = Trigger.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
        self._last_gripper_call_ts = time.time()
        self._gripper_last_cmd = gripper_cmd

    def _tick_arm(self, q_target: np.ndarray) -> None:
        # Indy7 제어를 가장 단순한 형태로 구현:
        #   q_target = q_current + delta_q
        #
        # 추후 개선 포인트:
        # - 다중 waypoint trajectory
        # - 속도/가속 제한
        # - FollowJointTrajectory(action) 기반 피드백 제어
        if self._joint_names is None:
            self.get_logger().warn("Joint names not ready yet; cannot publish trajectory.")
            return
        if q_target.size < 6:
            return

        traj = JointTrajectory()
        traj.joint_names = self._joint_names

        point = JointTrajectoryPoint()
        point.positions = q_target[:6].astype(float).tolist()

        # 일부 컨트롤러는 time_from_start가 0이면 무시할 수 있어, dt 기반으로 항상 양수로 넣는다.
        tns = int(max(1.0, self._dt) * 1e9)
        point.time_from_start = Duration(sec=0, nanosec=tns)

        traj.points = [point]
        self._joint_traj_pub.publish(traj)

    def _inference_tick(self) -> None:
        if self._latest_joints is None:
            return
        if self._latest_front_rgb is None or self._latest_overhead_rgb is None:
            return

        # 변환된 데이터셋 feature 키에 맞춰 observation dict를 만든다.
        # `predict_action()`이 내부에서 normalize/batch/device 처리까지 수행한다.
        obs = {
            "observation.images.front": self._latest_front_rgb,
            "observation.images.overhead": self._latest_overhead_rgb,
            "observation.state": self._build_state_vector(self._latest_joints),
        }

        action = predict_action(
            observation=obs,
            policy=self._policy,
            device=self._device,
            preprocessor=self._preprocessor,
            postprocessor=self._postprocessor,
            use_amp=self._use_amp,
            task=self._task,
            robot_type=self._robot_type,
        )

        action_vec = np.array(action.detach().cpu().squeeze(), dtype=np.float32)
        if action_vec.ndim != 1 or action_vec.shape[0] < 7:
            self.get_logger().error(f"Unexpected action shape: {action_vec.shape}")
            return

        delta_q = action_vec[:6]
        # gripper 출력은 연속값으로 나올 수 있어 반올림 후 [0,4]로 클립한다.
        # (action head를 분리하거나 분류로 바꾸면 이 로직을 교체하면 됨)
        gripper_raw = float(action_vec[6])
        gripper_cmd = int(np.clip(np.rint(gripper_raw), 0, 4))

        q_current = np.array(self._latest_joints.position, dtype=np.float32)
        if q_current.size < 6:
            q_current = np.pad(q_current, (0, 6 - q_current.size), mode="constant").astype(np.float32)
        q_target = q_current[:6] + delta_q

        self._tick_arm(q_target)
        self._tick_gripper(gripper_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = InferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
