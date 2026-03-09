#!/usr/bin/env python3
"""
Data Collector Node for Pipet Physical AI.

Subscribes to Indy7 joint states, RealSense RGB/Depth, and Mark7 gripper status.
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
    Synchronized data collector for Indy7 + Mark7 + RealSense.

    Provides /data_collector/start and /data_collector/stop services,
    publishes /data_collector/is_recording status.
    Saves episodes as NPZ files with the format specified in interface_spec.md.
    """

    def __init__(self):
        super().__init__('data_collector_node')

        # Parameters
        self.declare_parameter('output_dir', 'episodes')
        self.declare_parameter('image_size', 224)
        self.declare_parameter('sync_slop', 0.1)

        self.output_dir = os.path.expanduser(
            self.get_parameter('output_dir').get_parameter_value().string_value
        )
        self.image_size = self.get_parameter('image_size').get_parameter_value().integer_value
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
        # 0=hold, 1=grasp, 2=open, 3=press
        self._current_gripper_action: int = 0

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

        # Synchronized subscribers
        self.joint_sub = message_filters.Subscriber(
            self, JointState, '/joint_states'
        )
        self.rgb_sub = message_filters.Subscriber(
            self, Image, '/camera/camera/color/image_raw'
        )
        self.depth_sub = message_filters.Subscriber(
            self, Image, '/camera/camera/aligned_depth_to_color/image_raw'
        )
        self.gripper_sub = message_filters.Subscriber(
            self, GripperStatus, '/gripper/status'
        )

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.joint_sub, self.rgb_sub, self.depth_sub, self.gripper_sub],
            queue_size=10,
            slop=sync_slop,
        )
        self.sync.registerCallback(self._sync_callback)

        self.get_logger().info('DataCollectorNode initialized (4-topic sync)')

    def _clear_buffers(self):
        """Clear all data buffers."""
        self.timestamps: List[float] = []
        self.joint_positions: List[List[float]] = []
        self.joint_velocities: List[List[float]] = []
        self.joint_efforts: List[List[float]] = []
        self.rgb_images: List[np.ndarray] = []
        self.depth_images: List[np.ndarray] = []
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
            f'Episode saved: {os.path.basename(filepath)} '
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

    # -- Synchronized callback --

    def _sync_callback(
        self,
        joint_msg: JointState,
        rgb_msg: Image,
        depth_msg: Image,
        gripper_msg: GripperStatus,
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

        # RGB image
        try:
            rgb_cv = self.cv_bridge.imgmsg_to_cv2(rgb_msg, desired_encoding='rgb8')
            rgb_cv = self._resize_image(rgb_cv, is_depth=False)
            self.rgb_images.append(rgb_cv)
        except Exception as e:
            self.get_logger().error(f'RGB conversion failed: {e}')
            return

        # Depth image
        try:
            depth_cv = self.cv_bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough')
            depth_cv = self._resize_image(depth_cv, is_depth=True)
            self.depth_images.append(depth_cv)
        except Exception as e:
            self.get_logger().error(f'Depth conversion failed: {e}')

        # Gripper action
        self.gripper_actions.append(self._current_gripper_action)

    def _resize_image(self, image: np.ndarray, is_depth: bool = False) -> np.ndarray:
        """Resize image to target size."""
        try:
            import cv2
            interpolation = cv2.INTER_NEAREST if is_depth else cv2.INTER_LINEAR
            return cv2.resize(
                image,
                (self.image_size, self.image_size),
                interpolation=interpolation,
            )
        except ImportError:
            return image

    # -- Save --

    def _save_episode(self) -> str:
        """Save current episode as NPZ. Returns the file path."""
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'episode_{timestamp_str}.npz'
        filepath = os.path.join(self.output_dir, filename)

        np.savez_compressed(
            filepath,
            timestamps=np.array(self.timestamps, dtype=np.float64),
            joint_positions=np.array(self.joint_positions, dtype=np.float32),
            joint_velocities=np.array(self.joint_velocities, dtype=np.float32),
            joint_efforts=np.array(self.joint_efforts, dtype=np.float32),
            rgb_images=np.array(self.rgb_images, dtype=np.uint8),
            depth_images=np.array(self.depth_images, dtype=np.uint16),
            gripper_actions=np.array(self.gripper_actions, dtype=np.int8),
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
