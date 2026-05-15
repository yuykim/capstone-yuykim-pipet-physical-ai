#!/usr/bin/env python3
"""
Pygame keyboard teleop node for Indy7 + Mark7 data collection.

This node follows the working control_indy7 pattern:
  - start Indy task teleop in RELATIVE mode
  - keep a cumulative relative target [x,y,z,rx,ry,rz]
  - while a key is held, update that target at 30 Hz
  - publish it to /indy/teleop_pose for the Indy driver to execute with
    movetelel_rel()

It also calls Mark7 gripper services and data collector services so the
Pygame window can stay focused during collection.
"""

import time

import pygame

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float64MultiArray
from std_srvs.srv import Trigger
from indy_interfaces.srv import IndyService


ROBOT_CONTROL_HZ = 30
LINEAR_STEP_MM = 0.5
ANGULAR_STEP_DEG = 0.5
JOINT_STEP_DEG = 1.0

MSG_RECOVER = 1
MSG_MOVE_HOME = 2
MSG_MOVE_ZERO = 3
MSG_TELE_TASK_RLT = 5
MSG_TELE_JOINT_RLT = 7
MSG_TELE_STOP = 8

ACTION_HOLD = 0
ACTION_GRASP = 1
ACTION_OPEN = 2
ACTION_PRESS = 3
ACTION_RELEASE = 4


class KeyboardServoNode(Node):
    def __init__(self):
        super().__init__('keyboard_servo_node')

        self.pose_pub = self.create_publisher(Float64MultiArray, '/indy/teleop_pose', 10)
        self.joint_pub = self.create_publisher(Float64MultiArray, '/indy/teleop_joint', 10)

        self.create_subscription(Float64MultiArray, '/indy/ee_pose', self._ee_pose_cb, 10)
        self.create_subscription(JointState, '/joint_states', self._joint_state_cb, 10)
        self.create_subscription(Bool, '/data_collector/is_recording', self._recording_cb, 1)

        self.indy_srv = self.create_client(IndyService, 'indy_srv')

        self.gripper_grasp = self.create_client(Trigger, '/gripper/grasp')
        self.gripper_open = self.create_client(Trigger, '/gripper/open')
        self.gripper_press = self.create_client(Trigger, '/gripper/press')
        self.gripper_release = self.create_client(Trigger, '/gripper/release')

        self.log_grasp = self.create_client(Trigger, '/data_collector/log_grasp')
        self.log_open = self.create_client(Trigger, '/data_collector/log_open')
        self.log_press = self.create_client(Trigger, '/data_collector/log_press')
        self.log_release = self.create_client(Trigger, '/data_collector/log_release')

        self.data_start = self.create_client(Trigger, '/data_collector/start')
        self.data_stop = self.create_client(Trigger, '/data_collector/stop')
        self.data_mark_success = self.create_client(Trigger, '/data_collector/mark_success')
        self.data_mark_fail = self.create_client(Trigger, '/data_collector/mark_fail')
        self.data_discard = self.create_client(Trigger, '/data_collector/discard')

        self.ee_pose = None
        self.joint_positions_deg = None
        self.relative_pose = [0.0] * 6
        self.relative_joint = None

        self.linear_step = LINEAR_STEP_MM
        self.angular_step = ANGULAR_STEP_DEG
        self.joint_step = JOINT_STEP_DEG
        self.teleop_mode = None
        self.is_recording = False
        self.awaiting_label = False
        self.is_running = True

        self._init_pygame()
        self._wait_for_indy_service()
        self._print_help()

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 360))
        pygame.display.set_caption('Pipet Keyboard Teleop - Indy7 + Mark7')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    def _wait_for_indy_service(self):
        self.get_logger().info('Waiting for indy_srv...')
        while rclpy.ok() and not self.indy_srv.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('indy_srv not available, waiting...')
        self.get_logger().info('indy_srv connected')

    def _print_help(self):
        print('\n' + '=' * 72)
        print('  PYGAME KEYBOARD TELEOP - control_indy7 style')
        print('=' * 72)
        print('  Move:       W/S=x +/-   A/D=y +/-   Q/E=z +/-')
        print('  Rotate:     U/O=rx +/-  I/K=ry +/-  J/L=rz +/-')
        print('  Step:       [ / ] cartesian step down/up')
        print('  Indy7:      H=home   Z=zero   Ctrl+S=recover   P=stop teleop')
        print('  Gripper:    G=grasp  F=open   B=press     V=release')
        print('  Recording:  SPACE=start/label stop, then Y=success N=fail X=discard')
        print('  Quit:       ESC or window close')
        print('=' * 72 + '\n')

    def _ee_pose_cb(self, msg: Float64MultiArray):
        if len(msg.data) == 6:
            self.ee_pose = list(msg.data)

    def _joint_state_cb(self, msg: JointState):
        import math
        self.joint_positions_deg = [math.degrees(p) for p in msg.position]
        if self.relative_joint is None:
            self.relative_joint = [0.0] * len(self.joint_positions_deg)

    def _recording_cb(self, msg: Bool):
        self.is_recording = msg.data

    def _call_trigger(self, client, timeout=5.0):
        if not client.service_is_ready():
            self.get_logger().warn(f'Service not ready: {client.srv_name}')
            return False
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        result = future.result()
        if result is None:
            self.get_logger().error(f'{client.srv_name}: timeout')
            return False
        if not result.success:
            self.get_logger().warn(f'{client.srv_name}: {result.message}')
        return result.success

    def _call_indy(self, code: int, timeout=10.0):
        if not self.indy_srv.service_is_ready():
            self.get_logger().warn('indy_srv not available')
            return False
        req = IndyService.Request()
        req.data = code
        future = self.indy_srv.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        result = future.result()
        if result is None:
            self.get_logger().error(f'indy_srv cmd={code}: timeout')
            return False
        if not result.success:
            self.get_logger().warn(f'indy_srv cmd={code}: {result.message}')
        return result.success

    def _ensure_task_teleop(self):
        if self.teleop_mode == 'task':
            return True
        if self._call_indy(MSG_TELE_TASK_RLT):
            self.teleop_mode = 'task'
            self.relative_pose = [0.0] * 6
            return True
        return False

    def _ensure_joint_teleop(self):
        if self.teleop_mode == 'joint':
            return True
        if self._call_indy(MSG_TELE_JOINT_RLT):
            self.teleop_mode = 'joint'
            if self.relative_joint is not None:
                self.relative_joint = [0.0] * len(self.relative_joint)
            return True
        return False

    def _reset_teleop_targets(self):
        self.teleop_mode = None
        self.relative_pose = [0.0] * 6
        if self.relative_joint is not None:
            self.relative_joint = [0.0] * len(self.relative_joint)

    def _publish_pose(self):
        msg = Float64MultiArray()
        msg.data = list(self.relative_pose)
        self.pose_pub.publish(msg)

    def _publish_joint(self):
        if self.relative_joint is None:
            self.get_logger().warn('Waiting for /joint_states...')
            return
        msg = Float64MultiArray()
        msg.data = list(self.relative_joint)
        self.joint_pub.publish(msg)

    def _handle_gripper(self, action: int):
        if action == ACTION_GRASP:
            print('Gripper: GRASP')
            self._call_trigger(self.gripper_grasp)
            self._call_trigger(self.log_grasp)
        elif action == ACTION_OPEN:
            print('Gripper: OPEN')
            self._call_trigger(self.gripper_open)
            self._call_trigger(self.log_open)
        elif action == ACTION_PRESS:
            print('Gripper: PRESS')
            self._call_trigger(self.gripper_press)
            self._call_trigger(self.log_press)
        elif action == ACTION_RELEASE:
            print('Gripper: RELEASE')
            self._call_trigger(self.gripper_release)
            self._call_trigger(self.log_release)

    def _handle_record_key(self):
        if self.is_recording:
            self.awaiting_label = True
            print('Result? Y=success / N=fail / X=discard')
            return
        print('Starting recording...')
        self._call_trigger(self.data_start)

    def _finish_recording(self, label_key: str):
        self.awaiting_label = False
        if label_key == 'x':
            print('Discarding recording...')
            self._call_trigger(self.data_discard)
            return

        if label_key == 'y':
            print('Marking SUCCESS and saving...')
            self._call_trigger(self.data_mark_success)
        else:
            print('Marking FAIL and saving...')
            self._call_trigger(self.data_mark_fail)

        self._call_trigger(self.data_stop, timeout=300.0)

    def _handle_keydown(self, event):
        key = event.key

        if self.awaiting_label:
            if key == pygame.K_y:
                self._finish_recording('y')
            elif key == pygame.K_n:
                self._finish_recording('n')
            elif key == pygame.K_x:
                self._finish_recording('x')
            return

        if key == pygame.K_ESCAPE:
            self.is_running = False
        elif key == pygame.K_LEFTBRACKET:
            self.linear_step = max(0.1, self.linear_step - 0.1)
            self.angular_step = max(0.1, self.angular_step - 0.1)
            print(f'cart step -> linear={self.linear_step:.1f}mm angular={self.angular_step:.1f}deg')
        elif key == pygame.K_RIGHTBRACKET:
            self.linear_step += 0.1
            self.angular_step += 0.1
            print(f'cart step -> linear={self.linear_step:.1f}mm angular={self.angular_step:.1f}deg')
        elif key == pygame.K_SPACE:
            self._handle_record_key()
        elif key == pygame.K_h:
            if not self.is_recording:
                print('Indy7: HOME')
                self._call_indy(MSG_MOVE_HOME, timeout=15.0)
                self._reset_teleop_targets()
        elif key == pygame.K_z:
            if not self.is_recording:
                print('Indy7: ZERO')
                self._call_indy(MSG_MOVE_ZERO, timeout=15.0)
                self._reset_teleop_targets()
        elif key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            print('Indy7: RECOVER')
            self._call_indy(MSG_RECOVER)
            self._reset_teleop_targets()
        elif key == pygame.K_p:
            print('Indy7: STOP TELEOP')
            self._call_indy(MSG_TELE_STOP)
            self._reset_teleop_targets()
        elif key == pygame.K_g:
            self._handle_gripper(ACTION_GRASP)
        elif key == pygame.K_f:
            self._handle_gripper(ACTION_OPEN)
        elif key == pygame.K_b:
            self._handle_gripper(ACTION_PRESS)
        elif key == pygame.K_v:
            self._handle_gripper(ACTION_RELEASE)

    def _update_cartesian_from_keys(self):
        if self.awaiting_label:
            return

        keys = pygame.key.get_pressed()
        deltas = [0.0] * 6

        if keys[pygame.K_w]:
            deltas[0] += self.linear_step
        if keys[pygame.K_s]:
            deltas[0] -= self.linear_step
        if keys[pygame.K_a]:
            deltas[1] += self.linear_step
        if keys[pygame.K_d]:
            deltas[1] -= self.linear_step
        if keys[pygame.K_q]:
            deltas[2] += self.linear_step
        if keys[pygame.K_e]:
            deltas[2] -= self.linear_step

        if keys[pygame.K_u]:
            deltas[3] += self.angular_step
        if keys[pygame.K_o]:
            deltas[3] -= self.angular_step
        if keys[pygame.K_i]:
            deltas[4] += self.angular_step
        if keys[pygame.K_k]:
            deltas[4] -= self.angular_step
        if keys[pygame.K_j]:
            deltas[5] += self.angular_step
        if keys[pygame.K_l]:
            deltas[5] -= self.angular_step

        if not any(deltas):
            return

        if not self._ensure_task_teleop():
            return

        self.relative_pose = [
            self.relative_pose[i] + deltas[i] for i in range(6)
        ]
        self._publish_pose()

    def _update_screen(self):
        self.screen.fill((20, 24, 28))
        lines = [
            'Pipet Keyboard Teleop',
            f'cart step: {self.linear_step:.1f} mm / {self.angular_step:.1f} deg',
            f'teleop mode: {self.teleop_mode or "idle"}',
            f'recording: {"YES" if self.is_recording else "NO"}',
            'Move W/S A/D Q/E | Rotate U/O I/K J/L',
            'Gripper G=grasp F=open B=press V=release',
            'SPACE=start/stop, then Y/N/X label | Ctrl+S=recover | ESC=quit',
        ]
        if self.awaiting_label:
            lines.append('WAITING LABEL: Y success / N fail / X discard')
        for idx, line in enumerate(lines):
            color = (240, 240, 240) if idx != 3 else ((80, 220, 120) if self.is_recording else (220, 220, 120))
            surf = self.font.render(line, True, color)
            self.screen.blit(surf, (24, 24 + idx * 34))
        pygame.display.flip()

    def run(self):
        try:
            while self.is_running and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    elif event.type == pygame.KEYDOWN:
                        self._handle_keydown(event)

                self._update_cartesian_from_keys()
                self._update_screen()
                self.clock.tick(ROBOT_CONTROL_HZ)

        except KeyboardInterrupt:
            pass
        finally:
            if self.is_recording:
                self._call_trigger(self.data_stop, timeout=300.0)
            self._call_indy(MSG_TELE_STOP)
            pygame.quit()


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardServoNode()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
