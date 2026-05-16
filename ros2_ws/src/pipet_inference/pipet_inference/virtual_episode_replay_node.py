#!/usr/bin/env python3
"""
가상(리플레이) 에피소드 퍼블리셔 노드(ROS2).

목적:
  - 기존에 물리환경에서 수집한 `episodes/episode_*.npz`를 읽어서,
    물리 센서와 **동일한 토픽 이름/메시지 타입**으로 다시 퍼블리시한다.
  - 이렇게 하면 `pipet_data_collector`를 그대로 사용하면서,
    "가상환경에서도 동일한 데이터 수집 파이프라인"을 먼저 검증할 수 있다.

퍼블리시 토픽(물리환경과 동일한 이름):
  - /joint_states
  - /wrist_camera/camera/color/image_raw
  - /wrist_camera/camera/aligned_depth_to_color/image_raw
  - /overhead_camera/camera/color/image_raw
  - /overhead_camera/camera/aligned_depth_to_color/image_raw

추가 호환:
  - `pipet_data_collector`는 gripper action을 토픽이 아니라
    `/data_collector/log_*` 서비스 호출로 기록한다.
  - 따라서 NPZ의 `gripper_actions[t]` 값 변화에 맞춰
    `/data_collector/log_grasp|log_open|log_press|log_release`를 호출해준다.

확장 방향:
  - 나중에 Gazebo/Isaac/Unity가 준비되면,
    이 노드 대신 시뮬레이터가 위 토픽들을 직접 퍼블리시하도록 바꾸면 된다.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image, JointState
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory  # noqa: F401 (kept for optional future expansion)

from pipet_hand_mark7_msgs.msg import FingerState, GripperStatus


def _derive_replay_fps_from_timestamps(timestamps: np.ndarray) -> int:
    if timestamps.ndim != 1 or len(timestamps) < 3:
        return 15
    dts = timestamps[1:] - timestamps[:-1]
    dts = dts[dts > 0]
    if len(dts) == 0:
        return 15
    dt = float(np.median(dts))
    fps = int(round(1.0 / dt))
    return max(1, fps)


class VirtualEpisodeReplayNode(Node):
    def __init__(self):
        super().__init__("virtual_episode_replay_node")

        self.declare_parameter("episode_npz_path", "")
        # replay_fps=0이면 timestamps로부터 대략적인 fps를 추정한다.
        # (정확히 맞출 필요는 없고, collector 동작/동기화 검증용이 목적)
        self.declare_parameter("replay_fps", 0)
        self.declare_parameter("auto_record", True)
        self.declare_parameter("success_key", "success")
        # success==True일 때 mark_success를 호출할지 여부
        self.declare_parameter("task_success", True)
        # 1.0=실시간, 2.0=2배속
        self.declare_parameter("replay_speed", 1.0)

        self.declare_parameter("sleep_when_idle_s", 0.02)

        episode_npz_path = self.get_parameter("episode_npz_path").get_parameter_value().string_value
        replay_fps = self.get_parameter("replay_fps").get_parameter_value().integer_value
        auto_record = self.get_parameter("auto_record").get_parameter_value().bool_value
        success_key = self.get_parameter("success_key").get_parameter_value().string_value
        task_success = self.get_parameter("task_success").get_parameter_value().bool_value
        replay_speed = self.get_parameter("replay_speed").get_parameter_value().double_value
        sleep_when_idle_s = self.get_parameter("sleep_when_idle_s").get_parameter_value().double_value

        if not episode_npz_path:
            self.get_logger().warn("episode_npz_path is empty. Node will idle.")
            return

        self._episode_npz_path = Path(episode_npz_path)
        if not self._episode_npz_path.exists():
            raise FileNotFoundError(f"episode_npz_path not found: {self._episode_npz_path}")

        with np.load(str(self._episode_npz_path)) as ep:
            self._timestamps = ep["timestamps"]
            self._joint_positions = ep["joint_positions"]
            self._joint_velocities = ep["joint_velocities"]
            self._joint_efforts = ep["joint_efforts"]
            self._wrist_rgb_images = ep["wrist_rgb_images"]
            self._wrist_depth_images = ep["wrist_depth_images"]
            self._overhead_rgb_images = ep["overhead_rgb_images"]
            self._overhead_depth_images = ep["overhead_depth_images"]
            self._gripper_actions = ep["gripper_actions"]
            self._success = bool(_get_success(ep, success_key, self._episode_npz_path))

        self._replay_fps = int(replay_fps) if int(replay_fps) > 0 else _derive_replay_fps_from_timestamps(self._timestamps)
        self._period_s = 1.0 / max(1.0, self._replay_fps)
        self._replay_speed = float(replay_speed) if replay_speed > 0 else 1.0
        self._auto_record = bool(auto_record)
        self._task_success = bool(task_success)
        self._success_key = success_key
        self._sleep_when_idle_s = float(sleep_when_idle_s)

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)

        # 퍼블리셔: collector가 구독하는 토픽 계약을 그대로 맞춘다.
        self._joint_pub = self.create_publisher(JointState, "/joint_states", qos)
        self._wrist_rgb_pub = self.create_publisher(Image, "/wrist_camera/camera/color/image_raw", qos)
        self._wrist_depth_pub = self.create_publisher(
            Image, "/wrist_camera/camera/aligned_depth_to_color/image_raw", qos
        )
        self._overhead_rgb_pub = self.create_publisher(Image, "/overhead_camera/camera/color/image_raw", qos)
        self._overhead_depth_pub = self.create_publisher(
            Image, "/overhead_camera/camera/aligned_depth_to_color/image_raw", qos
        )

        self._gripper_status_pub = self.create_publisher(GripperStatus, "/gripper/status", qos)

        self.cv_bridge = CvBridge()

        # (옵션) data_collector 자동 start/stop
        self._srv_start = self.create_client(Trigger, "/data_collector/start")
        self._srv_stop = self.create_client(Trigger, "/data_collector/stop")
        self._srv_mark_success = self.create_client(Trigger, "/data_collector/mark_success")
        self._srv_mark_fail = self.create_client(Trigger, "/data_collector/mark_fail")

        # gripper action 로깅 서비스(collector가 gripper_actions를 기록하는 방식)
        self._srv_log_grasp = self.create_client(Trigger, "/data_collector/log_grasp")
        self._srv_log_open = self.create_client(Trigger, "/data_collector/log_open")
        self._srv_log_press = self.create_client(Trigger, "/data_collector/log_press")
        self._srv_log_release = self.create_client(Trigger, "/data_collector/log_release")

        for c in [
            self._srv_log_grasp,
            self._srv_log_open,
            self._srv_log_press,
            self._srv_log_release,
        ]:
            if not c.wait_for_service(timeout_sec=2.0):
                self.get_logger().warn(f"Service not available yet: {c.srv_name}")

        if self._auto_record:
            for c in [self._srv_start, self._srv_stop, self._srv_mark_success, self._srv_mark_fail]:
                if not c.wait_for_service(timeout_sec=5.0):
                    self.get_logger().warn(f"Service not available yet: {c.srv_name}")

        # 리플레이 상태
        self._idx = 0
        self._last_logged_cmd: Optional[int] = None
        self._timer = self.create_timer(self._period_s / self._replay_speed, self._tick)

        self.get_logger().info(
            f"Loaded replay file={self._episode_npz_path.name}, N={self._joint_positions.shape[0]}, "
            f"replay_fps={self._replay_fps}, period={(self._period_s / self._replay_speed):.4f}s, "
            f"auto_record={self._auto_record}, success={self._success}"
        )

        # auto_record=True면 시작하자마자 녹화를 시작한다.
        if self._auto_record:
            self._call_trigger(self._srv_start)

    def _call_trigger(self, client: any, timeout_sec: float = 5.0) -> None:
        req = Trigger.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout_sec)

    def _publish_gripper_status(self, stamp):
        # 현재 DataCollectorNode는 gripper_actions 저장에 /gripper/status를 쓰지 않지만,
        # 추후 gripper_state/실측 상태를 저장하는 스키마로 확장할 수 있어 기본 토픽은 유지한다.
        msg = GripperStatus()
        msg.header.stamp = stamp
        msg.fingers = [
            FingerState(position=0.0, current=0.0, temperature=0.0) for _ in range(6)
        ]
        self._gripper_status_pub.publish(msg)

    def _log_gripper_action_if_needed(self, cmd: int) -> None:
        # DataCollectorNode records gripper_actions as a mode value.
        # hold(0)에 해당하는 서비스는 없으므로, cmd==0이면 아무것도 호출하지 않는다.
        if cmd == 0:
            return
        if self._last_logged_cmd == cmd:
            return

        if cmd == 1:
            self._call_trigger(self._srv_log_grasp, timeout_sec=2.0)
        elif cmd == 2:
            self._call_trigger(self._srv_log_open, timeout_sec=2.0)
        elif cmd == 3:
            self._call_trigger(self._srv_log_press, timeout_sec=2.0)
        elif cmd == 4:
            self._call_trigger(self._srv_log_release, timeout_sec=2.0)
        else:
            return

        self._last_logged_cmd = cmd

    def _tick(self) -> None:
        n = self._joint_positions.shape[0]
        if self._idx >= n:
            if self._auto_record:
                # 리플레이가 끝나면 성공/실패 마킹 후 stop을 호출해 NPZ를 저장한다.
                if self._success and self._task_success:
                    self._call_trigger(self._srv_mark_success)
                else:
                    self._call_trigger(self._srv_mark_fail)
                self._call_trigger(self._srv_stop, timeout_sec=120.0)
            self.get_logger().info("Replay finished. Shutting down.")
            self.destroy_node()
            rclpy.shutdown()
            return

        stamp = self.get_clock().now().to_msg()

        # 1) gripper action log를 먼저 갱신한다.
        #    collector는 sync callback에서 "현재 gripper action mode"를 frame에 저장한다.
        desired_cmd = int(self._gripper_actions[self._idx])
        self._log_gripper_action_if_needed(desired_cmd)

        # 2) 관절 상태 퍼블리시
        js = JointState()
        js.header.stamp = stamp
        js.name = [f"joint_{i}" for i in range(6)]
        js.position = self._joint_positions[self._idx, :6].astype(float).tolist()
        js.velocity = self._joint_velocities[self._idx, :6].astype(float).tolist()
        js.effort = self._joint_efforts[self._idx, :6].astype(float).tolist()
        self._joint_pub.publish(js)

        # 3) 카메라 퍼블리시(RGB + Depth)
        wrist_rgb = self._wrist_rgb_images[self._idx]
        wrist_depth = self._wrist_depth_images[self._idx]
        overhead_rgb = self._overhead_rgb_images[self._idx]
        overhead_depth = self._overhead_depth_images[self._idx]

        wrist_rgb_msg = self.cv_bridge.cv2_to_imgmsg(wrist_rgb, encoding="rgb8")
        wrist_rgb_msg.header.stamp = stamp
        wrist_rgb_msg.header.frame_id = "wrist_camera"
        self._wrist_rgb_pub.publish(wrist_rgb_msg)

        wrist_depth_msg = self.cv_bridge.cv2_to_imgmsg(wrist_depth, encoding="16UC1")
        wrist_depth_msg.header.stamp = stamp
        wrist_depth_msg.header.frame_id = "wrist_camera"
        self._wrist_depth_pub.publish(wrist_depth_msg)

        overhead_rgb_msg = self.cv_bridge.cv2_to_imgmsg(overhead_rgb, encoding="rgb8")
        overhead_rgb_msg.header.stamp = stamp
        overhead_rgb_msg.header.frame_id = "overhead_camera"
        self._overhead_rgb_pub.publish(overhead_rgb_msg)

        overhead_depth_msg = self.cv_bridge.cv2_to_imgmsg(overhead_depth, encoding="16UC1")
        overhead_depth_msg.header.stamp = stamp
        overhead_depth_msg.header.frame_id = "overhead_camera"
        self._overhead_depth_pub.publish(overhead_depth_msg)

        self._publish_gripper_status(stamp)

        self._idx += 1


def _get_success(npz: np.lib.npyio.NpzFile, success_key: str, episode_path: Path) -> bool:
    if episode_path.parent.name == "success" or episode_path.stem.endswith("_success"):
        return True
    if episode_path.parent.name in {"fail", "unlabeled"}:
        return False
    if episode_path.stem.endswith("_fail") or episode_path.stem.endswith("_unlabeled"):
        return False

    # Backward compatibility for older NPZ files that stored the label internally.
    if success_key in npz:
        return npz[success_key].item() if hasattr(npz[success_key], "item") else npz[success_key]
    if "success" in npz:
        return npz["success"].item() if hasattr(npz["success"], "item") else npz["success"]
    if "episode_success" in npz:
        return npz["episode_success"].item() if hasattr(npz["episode_success"], "item") else npz["episode_success"]
    return False


def main(args=None):
    rclpy.init(args=args)
    node = VirtualEpisodeReplayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
