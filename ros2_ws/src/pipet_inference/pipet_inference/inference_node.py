#!/usr/bin/env python3
"""
Inference Node for Pipet Physical AI (Stub).

Loads a trained model and uses sensor data to autonomously control
the Indy7 arm and Mark7 gripper for pipette manipulation.

This is a placeholder — implement model loading and inference logic
when trained models are available.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image
from std_srvs.srv import Trigger


class InferenceNode(Node):
    """Stub inference node. Subscribes to sensor topics, ready for model integration."""

    def __init__(self):
        super().__init__('inference_node')

        # Parameters
        self.declare_parameter('model_path', '')
        self.declare_parameter('model_type', 'lerobot')
        self.declare_parameter('inference_hz', 15.0)

        model_path = self.get_parameter('model_path').get_parameter_value().string_value
        model_type = self.get_parameter('model_type').get_parameter_value().string_value
        inference_hz = self.get_parameter('inference_hz').get_parameter_value().double_value

        self.get_logger().info(
            f'Inference node initialized (stub) - '
            f'model_type={model_type}, hz={inference_hz}'
        )

        if not model_path:
            self.get_logger().warn('No model_path specified. Node will idle.')
            return

        # Subscriptions
        self.create_subscription(
            JointState, '/joint_states', self._joint_cb, 10
        )
        self.create_subscription(
            Image, '/camera/camera/color/image_raw', self._rgb_cb, 10
        )
        self.create_subscription(
            Image, '/camera/camera/aligned_depth_to_color/image_raw', self._depth_cb, 10
        )

        # Service clients -- Mark7 gripper
        self.gripper_grasp = self.create_client(Trigger, '/gripper/grasp')
        self.gripper_open = self.create_client(Trigger, '/gripper/open')
        self.gripper_press = self.create_client(Trigger, '/gripper/press')

        # Inference timer
        period = 1.0 / inference_hz
        self.inference_timer = self.create_timer(period, self._inference_tick)

        # TODO: Load model from model_path
        self.get_logger().info(f'Model path: {model_path} (loading not implemented)')

    def _joint_cb(self, msg: JointState):
        self._latest_joints = msg

    def _rgb_cb(self, msg: Image):
        self._latest_rgb = msg

    def _depth_cb(self, msg: Image):
        self._latest_depth = msg

    def _inference_tick(self):
        # TODO: Run inference and send commands
        pass


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


if __name__ == '__main__':
    main()
