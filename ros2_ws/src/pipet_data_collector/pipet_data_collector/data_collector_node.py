#!/usr/bin/env python3
"""
Data Collector Node for Pipet Physical AI.

Subscribes to Indy7 joint states, two RealSense D435 cameras (wrist + overhead),
and Mark7 gripper status.
Synchronizes all data using ApproximateTimeSynchronizer and saves episodes as NPZ.
"""

import os
from datetime import datetime
from typing import List, Optional

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import JointState, Image
from std_msgs.msg import Bool
from std_srvs.srv import Trigger
from pipet_hand_mark7_msgs.msg import GripperStatus

from cv_bridge import CvBridge
import message_filters


class DataCollectorNode(Node):
    """
    Synchronized data collector for Indy7 + Mark7 + 2x RealSense D435.

    Provides /data_collector/start and /data_collector/stop services,
    publishes /data_collector/is_recording status.
    Saves episodes as NPZ files with wrist and overhead camera data.
    """

    def __init__(self):
        super().__init__('data_collector_node')

        # Parameters
        self.declare_parameter('output_dir', 'episodes')
        self.declare_parameter('sync_slop', 1.0)

        self.output_dir = os.path.expanduser(
            self.get_parameter('output_dir').get_parameter_value().string_value
        )
        sync_slop = self.get_parameter('sync_slop').get_parameter_value().double_value

        os.makedirs(self.output_dir, exist_ok=True)
        self.get_logger().info(f'Output directory: {self.output_dir}')

        # CV Bridge
        self.cv_bridge = CvBridge()

        # Recording state
        self.is_recording = False
        self.recording_start_time: Optional[float] = None
        self.episode_count = 0

        # Data buffers
        self._clear_buffers()

        # Gripper action tracking
        # 0=hold, 1=grasp, 2=open, 3=press, 4=release
        self._current_gripper_action: int = 0

        # Episode result (True=success, False=fail, None=unmarked)
        self._episode_success: Optional[bool] = None

        # Services
        self.start_srv = self.create_service(
            Trigger, '/data_collector/start', self._start_callback
        )
        self.stop_srv = self.create_service(
            Trigger, '/data_collector/stop', self._stop_callback
        )

        # Publisher
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE)
        self.recording_pub = self.create_publisher(
            Bool, '/data_collector/is_recording', qos
        )
        self.status_timer = self.create_timer(0.5, self._publish_status)

        # Gripper action services (to intercept gripper commands for logging)
        self.gripper_action_srv_grasp = self.create_service(
            Trigger, '/data_collector/log_grasp', self._log_grasp_callback
        )
        self.gripper_action_srv_open = self.create_service(
            Trigger, '/data_collector/log_open', self._log_open_callback
        )
        self.gripper_action_srv_press = self.create_service(
            Trigger, '/data_collector/log_press', self._log_press_callback
        )
        self.gripper_action_srv_release = self.create_service(
            Trigger, '/data_collector/log_release', self._log_release_callback
        )

        # Episode result services
        self.mark_success_srv = self.create_service(
            Trigger, '/data_collector/mark_success', self._mark_success_callback
        )
        self.mark_fail_srv = self.create_service(
            Trigger, '/data_collector/mark_fail', self._mark_fail_callback
        )

        # Gripper status - separate subscriber (slow ~0.7Hz, not synced)
        self._latest_gripper_status = None
        self.create_subscription(
            GripperStatus, '/gripper/status',
            self._gripper_status_cb, 10
        )

        # Synchronized subscribers (5-topic sync, without gripper)
        self.joint_sub = message_filters.Subscriber(
            self, JointState, '/joint_states'
        )
        self.wrist_rgb_sub = message_filters.Subscriber(
            self, Image, '/wrist_camera/camera/color/image_raw'
        )
        self.wrist_depth_sub = message_filters.Subscriber(
            self, Image, '/wrist_camera/camera/aligned_depth_to_color/image_raw'
        )
        self.overhead_rgb_sub = message_filters.Subscriber(
            self, Image, '/overhead_camera/camera/color/image_raw'
        )
        self.overhead_depth_sub = message_filters.Subscriber(
            self, Image, '/overhead_camera/camera/aligned_depth_to_color/image_raw'
        )

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.joint_sub,
             self.wrist_rgb_sub, self.wrist_depth_sub,
             self.overhead_rgb_sub, self.overhead_depth_sub],
            queue_size=10,
            slop=sync_slop,
        )
        self.sync.registerCallback(self._sync_callback)

        self.get_logger().info('DataCollectorNode initialized (5-topic sync + gripper cache)')

    def _clear_buffers(self):
        """Clear all data buffers."""
        self.timestamps: List[float] = []
        self.joint_positions: List[List[float]] = []
        self.joint_velocities: List[List[float]] = []
        self.joint_efforts: List[List[float]] = []
        self.wrist_rgb_images: List[np.ndarray] = []
        self.wrist_depth_images: List[np.ndarray] = []
        self.overhead_rgb_images: List[np.ndarray] = []
        self.overhead_depth_images: List[np.ndarray] = []
        self.gripper_actions: List[int] = []

    # -- Service callbacks --

    def _start_callback(self, request, response):
        if self.is_recording:
            response.success = False
            response.message = 'Already recording'
            return response

        self._clear_buffers()
        self.is_recording = True
        self.recording_start_time = self.get_clock().now().nanoseconds / 1e9
        self._current_gripper_action = 0
        self._episode_success = None
        self.episode_count += 1

        response.success = True
        response.message = f'Recording started (episode {self.episode_count})'
        self.get_logger().info(response.message)
        return response

    def _stop_callback(self, request, response):
        if not self.is_recording:
            response.success = False
            response.message = 'Not recording'
            return response

        self.is_recording = False
        sample_count = len(self.timestamps)

        if sample_count == 0:
            response.success = False
            response.message = 'No data collected'
            return response

        filepath = self._save_episode()
        duration = self.timestamps[-1] - self.timestamps[0] if sample_count > 1 else 0.0
        rate = sample_count / duration if duration > 0 else 0.0

        response.success = True
        response.message = (
            f'Episode saved: {os.path.abspath(filepath)} '
            f'({sample_count} frames, {duration:.1f}s, {rate:.1f}Hz)'
        )
        self.get_logger().info(response.message)
        return response

    # -- Gripper action logging callbacks --

    def _log_grasp_callback(self, request, response):
        self._current_gripper_action = 1
        response.success = True
        response.message = 'Gripper action set to GRASP'
        return response

    def _log_open_callback(self, request, response):
        self._current_gripper_action = 2
        response.success = True
        response.message = 'Gripper action set to OPEN'
        return response

    def _log_press_callback(self, request, response):
        self._current_gripper_action = 3
        response.success = True
        response.message = 'Gripper action set to PRESS'
        return response

    def _log_release_callback(self, request, response):
        self._current_gripper_action = 4
        response.success = True
        response.message = 'Gripper action set to RELEASE'
        return response

    def _mark_success_callback(self, request, response):
        self._episode_success = True
        response.success = True
        response.message = 'Episode marked as SUCCESS'
        return response

    def _mark_fail_callback(self, request, response):
        self._episode_success = False
        response.success = True
        response.message = 'Episode marked as FAIL'
        return response

    def _gripper_status_cb(self, msg: GripperStatus):
        self._latest_gripper_status = msg

    # -- Synchronized callback --

    def _sync_callback(
        self,
        joint_msg: JointState,
        wrist_rgb_msg: Image,
        wrist_depth_msg: Image,
        overhead_rgb_msg: Image,
        overhead_depth_msg: Image,
    ):
        if not self.is_recording:
            return

        current_time = self.get_clock().now().nanoseconds / 1e9
        relative_time = current_time - self.recording_start_time

        # Joint data
        self.timestamps.append(relative_time)
        self.joint_positions.append(list(joint_msg.position))
        self.joint_velocities.append(list(joint_msg.velocity))
        self.joint_efforts.append(list(joint_msg.effort))

        # Wrist camera
        try:
            wrist_rgb = self.cv_bridge.imgmsg_to_cv2(wrist_rgb_msg, desired_encoding='rgb8')
            self.wrist_rgb_images.append(wrist_rgb)
        except Exception as e:
            self.get_logger().error(f'Wrist RGB conversion failed: {e}')
            return

        try:
            wrist_depth = self.cv_bridge.imgmsg_to_cv2(wrist_depth_msg, desired_encoding='passthrough')
            self.wrist_depth_images.append(wrist_depth)
        except Exception as e:
            self.get_logger().error(f'Wrist depth conversion failed: {e}')
            return

        # Overhead camera
        try:
            overhead_rgb = self.cv_bridge.imgmsg_to_cv2(overhead_rgb_msg, desired_encoding='rgb8')
            self.overhead_rgb_images.append(overhead_rgb)
        except Exception as e:
            self.get_logger().error(f'Overhead RGB conversion failed: {e}')
            return

        try:
            overhead_depth = self.cv_bridge.imgmsg_to_cv2(overhead_depth_msg, desired_encoding='passthrough')
            self.overhead_depth_images.append(overhead_depth)
        except Exception as e:
            self.get_logger().error(f'Overhead depth conversion failed: {e}')
            return

        # Gripper action
        self.gripper_actions.append(self._current_gripper_action)

    # -- Save --

    def _save_episode(self) -> str:
        """Save current episode as NPZ. Returns the file path."""
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        if self._episode_success is True:
            label = 'success'
        elif self._episode_success is False:
            label = 'fail'
        else:
            label = 'unlabeled'
        filename = f'episode_{timestamp_str}_{label}.npz'
        filepath = os.path.join(self.output_dir, filename)

        np.savez_compressed(
            filepath,
            timestamps=np.array(self.timestamps, dtype=np.float64),
            joint_positions=np.array(self.joint_positions, dtype=np.float32),
            joint_velocities=np.array(self.joint_velocities, dtype=np.float32),
            joint_efforts=np.array(self.joint_efforts, dtype=np.float32),
            wrist_rgb_images=np.array(self.wrist_rgb_images, dtype=np.uint8),
            wrist_depth_images=np.array(self.wrist_depth_images, dtype=np.uint16),
            overhead_rgb_images=np.array(self.overhead_rgb_images, dtype=np.uint8),
            overhead_depth_images=np.array(self.overhead_depth_images, dtype=np.uint16),
            gripper_actions=np.array(self.gripper_actions, dtype=np.int8),
            success=np.array(self._episode_success if self._episode_success is not None else False),
        )

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        self.get_logger().info(f'Saved {filepath} ({size_mb:.1f} MB)')
        return filepath

    # -- Status --

    def _publish_status(self):
        msg = Bool()
        msg.data = self.is_recording
        self.recording_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DataCollectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
