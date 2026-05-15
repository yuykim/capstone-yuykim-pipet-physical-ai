#!/usr/bin/env python3
"""
Inference Node for Pipet Physical AI (movetelel-based).

Loads a trained model (LeRobot ACT etc.) and autonomously controls Indy7
in Cartesian space via /indy/teleop_pose, plus Mark7 gripper services.

Observation:
  - /joint_states           sensor_msgs/JointState  (6 DoF)
  - /indy/ee_pose           Float64MultiArray (6D Indy native [mm,mm,mm,deg,deg,deg])
  - selected camera color image (wrist or overhead) - configurable

Action (per model output):
  - Cartesian delta + gripper code:
      [dx_mm, dy_mm, dz_mm, drx_deg, dry_deg, drz_deg, gripper(0..4)]
  - Publish absolute target = current ee_pose + delta to /indy/teleop_pose
  - Map gripper code to /gripper/grasp|open|press|release service call (on change)

Model loading is left as a stub; concrete LeRobot policy integration
should fill `_load_policy()` and `_predict()`.
"""

from typing import Optional

import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger

from cv_bridge import CvBridge


class InferenceNode(Node):

    def __init__(self):
        super().__init__('inference_node')

        # Parameters
        self.declare_parameter('model_path', '')
        self.declare_parameter('model_type', 'lerobot')
        self.declare_parameter('inference_hz', 15.0)
        self.declare_parameter('camera', 'wrist')  # 'wrist' | 'overhead'

        model_path = self.get_parameter('model_path').get_parameter_value().string_value
        model_type = self.get_parameter('model_type').get_parameter_value().string_value
        inference_hz = self.get_parameter('inference_hz').get_parameter_value().double_value
        camera = self.get_parameter('camera').get_parameter_value().string_value

        self.get_logger().info(
            f'inference_node: model_type={model_type}, hz={inference_hz}, camera={camera}'
        )

        # Publisher: target EE pose for movetelel
        self.pose_pub = self.create_publisher(
            Float64MultiArray, '/indy/teleop_pose', 10
        )

        # Sensor state
        self.cv_bridge = CvBridge()
        self._latest_joints: Optional[JointState] = None
        self._latest_ee_pose: Optional[list] = None
        self._latest_image: Optional[np.ndarray] = None
        self._last_gripper_cmd: int = 0

        # Subscriptions
        self.create_subscription(JointState, '/joint_states', self._joint_cb, 10)
        self.create_subscription(
            Float64MultiArray, '/indy/ee_pose', self._ee_pose_cb, 10
        )
        rgb_topic = f'/{camera}_camera/camera/color/image_raw'
        self.create_subscription(Image, rgb_topic, self._image_cb, 10)
        self.get_logger().info(f'Subscribed to image topic: {rgb_topic}')

        # Mark7 gripper service clients
        self.gripper_clients = {
            1: self.create_client(Trigger, '/gripper/grasp'),
            2: self.create_client(Trigger, '/gripper/open'),
            3: self.create_client(Trigger, '/gripper/press'),
            4: self.create_client(Trigger, '/gripper/release'),
        }

        # Model placeholder
        self.model = None
        if model_path:
            self._load_policy(model_path, model_type)
        else:
            self.get_logger().warn('No model_path specified. Node will not act.')

        # Inference loop
        period = 1.0 / inference_hz
        self.create_timer(period, self._inference_tick)

    # -- Callbacks --

    def _joint_cb(self, msg: JointState):
        self._latest_joints = msg

    def _ee_pose_cb(self, msg: Float64MultiArray):
        if len(msg.data) == 6:
            self._latest_ee_pose = list(msg.data)

    def _image_cb(self, msg: Image):
        try:
            self._latest_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        except Exception as e:
            self.get_logger().warn(f'image_cb conversion failed: {e}')

    # -- Inference --

    def _load_policy(self, model_path: str, model_type: str):
        """Load trained policy. TODO: implement LeRobot loading."""
        self.get_logger().info(f'Loading {model_type} policy from {model_path} (stub)')
        # TODO: from lerobot.policies.act import ACTPolicy; self.model = ACTPolicy.from_pretrained(...)
        self.model = None

    def _predict(self) -> Optional[np.ndarray]:
        """
        Run model forward pass. Return action vector:
            [dx_mm, dy_mm, dz_mm, drx_deg, dry_deg, drz_deg, gripper(0..4)]
        Returns None if model not loaded or observation incomplete.
        """
        if self.model is None:
            return None
        if (
            self._latest_joints is None
            or self._latest_ee_pose is None
            or self._latest_image is None
        ):
            return None
        # TODO: assemble observation tensor and call self.model.select_action(...)
        return None

    def _send_gripper(self, code: int):
        if code == self._last_gripper_cmd or code == 0:
            return
        client = self.gripper_clients.get(code)
        if client is None:
            return
        if not client.service_is_ready():
            return
        client.call_async(Trigger.Request())
        self._last_gripper_cmd = code

    def _inference_tick(self):
        if self._latest_ee_pose is None:
            return
        action = self._predict()
        if action is None:
            return
        if len(action) < 7:
            self.get_logger().warn(f'predict returned {len(action)} dims, expected 7')
            return

        delta = action[:6]
        gripper_code = int(round(action[6]))

        target_pose = [self._latest_ee_pose[i] + float(delta[i]) for i in range(6)]
        msg = Float64MultiArray()
        msg.data = target_pose
        self.pose_pub.publish(msg)

        self._send_gripper(gripper_code)


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
