#!/usr/bin/env python3
"""DAgger supervisor for model rollout + human correction recording.

Pipeline:
  - inference_node publishes model cartesian relative pose to /dagger/model_teleop_pose
  - this node forwards model pose to /indy/teleop_pose while in AUTO
  - START enters TAKEOVER, stops forwarding model commands, starts recording
  - human Xbox commands are published to /indy/teleop_pose and recorded
  - START again asks for label: A=success, B=fail, X=discard

Only the human takeover segment is recorded by the existing data_collector_node.
"""

from __future__ import annotations

from collections import deque
from glob import glob
import os
import select
import struct
import time
from typing import Deque, Optional

os.environ.setdefault('SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS', '1')
os.environ.setdefault('SDL_JOYSTICK_HIDAPI', '0')
os.environ.setdefault('SDL_JOYSTICK_HIDAPI_XBOX', '0')

import pygame

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String
from std_srvs.srv import Trigger
from indy_interfaces.srv import IndyService


ROBOT_CONTROL_HZ = 30

DEFAULT_INPUT_BACKEND = 'linuxevdev'
DEFAULT_EVENT_DEVICE = ''
DEFAULT_JOYSTICK_DEVICE = '/dev/input/js0'
DEFAULT_JOYSTICK_INDEX = 0
DEFAULT_ROBOT_IP = '192.168.1.10'
HOME_JOINT_DEG = [0.0, 25.0, -115.0, 90.0, 0.0, 0.0]
HOME_VEL_RATIO = 10
HOME_ACC_RATIO = 10

LINEAR_STEP_MM = 1.0
ANGULAR_STEP_DEG = 1.0
LINEAR_STEP_DELTA_MM = 0.1
ANGULAR_STEP_DELTA_DEG = 0.1
MIN_LINEAR_STEP_MM = 0.05
MAX_LINEAR_STEP_MM = 5.0
MIN_ANGULAR_STEP_DEG = 0.05
MAX_ANGULAR_STEP_DEG = 5.0
DEADZONE = 0.18
TRIGGER_DEADZONE = 0.08

MSG_RECOVER = 1
MSG_MOVE_ZERO = 3
MSG_TELE_TASK_RLT = 5
MSG_TELE_STOP = 8

ACTION_HOLD = 0
ACTION_GRASP = 1
ACTION_OPEN = 2
ACTION_PRESS = 3
ACTION_RELEASE = 4

GRIPPER_ACTION_NAMES = {
    ACTION_HOLD: 'hold',
    ACTION_GRASP: 'grasp',
    ACTION_OPEN: 'open',
    ACTION_PRESS: 'press',
    ACTION_RELEASE: 'release',
}
HOLDING_GRIPPER_ACTIONS = {ACTION_GRASP, ACTION_PRESS}

BTN_A = 0
BTN_B = 1
BTN_X = 2
BTN_Y = 3
BTN_LB = 4
BTN_RB = 5
BTN_BACK = 6
BTN_START = 7
BTN_THUMBL = 9
BTN_THUMBR = 10

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80
JS_EVENT_FORMAT = 'IhBB'
JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FORMAT)

EV_KEY = 0x01
EV_ABS = 0x03
EVDEV_EVENT_FORMAT = 'llHHi'
EVDEV_EVENT_SIZE = struct.calcsize(EVDEV_EVENT_FORMAT)

EVDEV_AXIS_TO_INDEX = {
    0: 0,    # ABS_X
    1: 1,    # ABS_Y
    2: 2,    # ABS_Z / LT
    3: 3,    # ABS_RX
    4: 4,    # ABS_RY
    5: 5,    # ABS_RZ / RT
    16: 6,   # ABS_HAT0X
    17: 7,   # ABS_HAT0Y
}

EVDEV_KEY_TO_BUTTON = {
    304: BTN_A,      # BTN_SOUTH
    305: BTN_B,      # BTN_EAST
    307: BTN_X,      # BTN_NORTH
    308: BTN_Y,      # BTN_WEST
    310: BTN_LB,     # BTN_TL
    311: BTN_RB,     # BTN_TR
    314: BTN_BACK,   # BTN_SELECT
    315: BTN_START,  # BTN_START
    316: 8,          # BTN_MODE
    317: 9,          # BTN_THUMBL
    318: 10,         # BTN_THUMBR
}


class DaggerSupervisorNode(Node):
    def __init__(self) -> None:
        super().__init__('dagger_supervisor_node')

        self.declare_parameter('input_backend', DEFAULT_INPUT_BACKEND)
        self.declare_parameter('event_device', DEFAULT_EVENT_DEVICE)
        self.declare_parameter('joystick_device', DEFAULT_JOYSTICK_DEVICE)
        self.declare_parameter('joystick_index', DEFAULT_JOYSTICK_INDEX)
        self.declare_parameter('indy_ip', DEFAULT_ROBOT_IP)
        self.declare_parameter('model_pose_topic', '/dagger/model_teleop_pose')
        self.declare_parameter('output_pose_topic', '/indy/teleop_pose')
        self.declare_parameter('ee_pose_topic', '/indy/ee_pose')
        self.declare_parameter('task_name', 'remove_dagger')
        self.declare_parameter('linear_step_mm', LINEAR_STEP_MM)
        self.declare_parameter('angular_step_deg', ANGULAR_STEP_DEG)
        self.declare_parameter('deadzone', DEADZONE)
        self.declare_parameter('auto_home_after_save', True)
        self.declare_parameter('auto_resume_after_home', True)
        self.declare_parameter('home_joint_deg', HOME_JOINT_DEG)
        self.declare_parameter('home_vel_ratio', HOME_VEL_RATIO)
        self.declare_parameter('home_acc_ratio', HOME_ACC_RATIO)
        self.declare_parameter('stuck_window_sec', 3.0)
        self.declare_parameter('stuck_linear_mm', 1.0)
        self.declare_parameter('stuck_angular_deg', 1.0)
        self.declare_parameter('stop_teleop_after_save', True)
        self.declare_parameter('debug_input', False)

        self.input_backend = self.get_parameter('input_backend').value
        self.event_device = self.get_parameter('event_device').value
        self.joystick_device = self.get_parameter('joystick_device').value
        self.joystick_index = int(self.get_parameter('joystick_index').value)
        self.indy_ip = self.get_parameter('indy_ip').value
        self.model_pose_topic = self.get_parameter('model_pose_topic').value
        self.output_pose_topic = self.get_parameter('output_pose_topic').value
        self.ee_pose_topic = self.get_parameter('ee_pose_topic').value
        self.task_name = self._sanitize_task_name(self.get_parameter('task_name').value)
        self.linear_step = float(self.get_parameter('linear_step_mm').value)
        self.angular_step = float(self.get_parameter('angular_step_deg').value)
        self.deadzone = float(self.get_parameter('deadzone').value)
        self.auto_home_after_save = bool(self.get_parameter('auto_home_after_save').value)
        self.auto_resume_after_home = bool(self.get_parameter('auto_resume_after_home').value)
        self.home_joint_deg = list(
            self.get_parameter('home_joint_deg').get_parameter_value().double_array_value
        )
        self.home_vel_ratio = int(self.get_parameter('home_vel_ratio').value)
        self.home_acc_ratio = int(self.get_parameter('home_acc_ratio').value)
        self.stuck_window_sec = float(self.get_parameter('stuck_window_sec').value)
        self.stuck_linear_mm = float(self.get_parameter('stuck_linear_mm').value)
        self.stuck_angular_deg = float(self.get_parameter('stuck_angular_deg').value)
        self.stop_teleop_after_save = bool(self.get_parameter('stop_teleop_after_save').value)
        self.debug_input = bool(self.get_parameter('debug_input').value)

        self.pose_pub = self.create_publisher(Float64MultiArray, self.output_pose_topic, 10)
        self.task_pub = self.create_publisher(String, '/data_collector/task_name', 10)
        self.create_subscription(
            Float64MultiArray, self.model_pose_topic, self._model_pose_cb, 10
        )
        self.create_subscription(
            Float64MultiArray, self.ee_pose_topic, self._ee_pose_cb, 10
        )

        self.indy_srv = self.create_client(IndyService, 'indy_srv')
        self.data_start = self.create_client(Trigger, '/data_collector/start')
        self.data_stop = self.create_client(Trigger, '/data_collector/stop')
        self.data_mark_success = self.create_client(Trigger, '/data_collector/mark_success')
        self.data_mark_fail = self.create_client(Trigger, '/data_collector/mark_fail')
        self.data_discard = self.create_client(Trigger, '/data_collector/discard')

        self.gripper_grasp = self.create_client(Trigger, '/gripper/grasp')
        self.gripper_open = self.create_client(Trigger, '/gripper/open')
        self.gripper_press = self.create_client(Trigger, '/gripper/press')
        self.gripper_release = self.create_client(Trigger, '/gripper/release')
        self.log_grasp = self.create_client(Trigger, '/data_collector/log_grasp')
        self.log_open = self.create_client(Trigger, '/data_collector/log_open')
        self.log_press = self.create_client(Trigger, '/data_collector/log_press')
        self.log_release = self.create_client(Trigger, '/data_collector/log_release')

        self.mode = 'AUTO'
        self.awaiting_label = False
        self.is_running = True
        self.teleop_ready = False
        self.relative_pose = [0.0] * 6
        self.last_model_pose: Optional[list[float]] = None
        self.last_forwarded_model_pose: Optional[list[float]] = None
        self.model_pose_offset: Optional[list[float]] = None
        self.awaiting_model_reset = False
        self.last_model_msg_time: Optional[float] = None
        self.last_ee_pose: Optional[list[float]] = None
        self.ee_history: Deque[tuple[float, list[float]]] = deque()
        self.stuck_warning = False
        self.last_gripper_action = ACTION_HOLD
        self.saved_episode_count = 0
        self.status_text = 'AUTO: model drives. START = takeover + record.'
        self._prev_buttons: dict[int, bool] = {}
        self._last_debug_state = None

        self.joystick = None
        self.joystick_fd = None
        self.input_name = ''
        self.axes = [0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        self.buttons = [0] * 12

        self._init_pygame()
        self._publish_task_name(repeat=3)
        self._print_help()

    @staticmethod
    def _sanitize_task_name(value: str) -> str:
        cleaned = str(value).strip().lower().replace(' ', '_')
        return ''.join(ch for ch in cleaned if ch.isalnum() or ch in ('_', '-'))

    def _init_pygame(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((840, 430))
        pygame.display.set_caption('Pipet DAgger Collection')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        if self.input_backend == 'pygame':
            pygame.joystick.init()
            count = pygame.joystick.get_count()
            if count <= self.joystick_index:
                raise RuntimeError(
                    f'Xbox controller not found: joystick_index={self.joystick_index}, '
                    f'connected={count}'
                )
            self.joystick = pygame.joystick.Joystick(self.joystick_index)
            self.joystick.init()
            self.input_name = self.joystick.get_name()
            self.get_logger().info(f'Using pygame joystick: {self.input_name}')
        elif self.input_backend == 'linuxjs':
            self.joystick_fd = os.open(self.joystick_device, os.O_RDONLY | os.O_NONBLOCK)
            self.input_name = self.joystick_device
            self.get_logger().info(f'Using Linux joystick device: {self.joystick_device}')
            self._poll_input()
        elif self.input_backend == 'linuxevdev':
            self.event_device = self._resolve_event_device()
            self.joystick_fd = os.open(self.event_device, os.O_RDONLY | os.O_NONBLOCK)
            self.input_name = self.event_device
            self.get_logger().info(f'Using Linux evdev device: {self.event_device}')
            self._poll_input()
        else:
            raise RuntimeError(
                f'Unsupported input_backend={self.input_backend!r}; '
                'use "linuxevdev", "linuxjs", or "pygame"'
            )

    def _resolve_event_device(self) -> str:
        if self.event_device:
            return self.event_device
        candidates = sorted(glob('/dev/input/by-id/*event-joystick'))
        preferred = [
            path for path in candidates
            if 'Microsoft' in path or 'Xbox' in path or 'Controller' in path
        ]
        if preferred:
            return preferred[0]
        if candidates:
            return candidates[0]
        return '/dev/input/event16'

    def _print_help(self) -> None:
        print('\n' + '=' * 76)
        print('  PIPET DAGGER COLLECTION')
        print('=' * 76)
        print('  AUTO:       model output is forwarded to /indy/teleop_pose')
        print('  TAKEOVER:   START = stop model forwarding + start correction recording')
        print('  Move:       D-pad=x/y   LT/RT=z -/+')
        print('  Rotate:     Right stick=rx/ry   LB/RB=rz +/-')
        print('  Speed:      left stick click=slower   right stick click=faster')
        print('  Gripper:    A=grasp  B=open  X=press  Y=release')
        print('  Finish:     START, then A=success B=fail X=discard')
        print('  After save: home automatically, then AUTO resumes for next rollout')
        print('  Safety:     BACK=stop teleop/discard active recording, stay PAUSED')
        print('=' * 76 + '\n')

    def _publish_task_name(self, repeat: int = 1) -> None:
        msg = String()
        msg.data = self.task_name
        for _ in range(max(1, repeat)):
            self.task_pub.publish(msg)

    def _model_pose_cb(self, msg: Float64MultiArray) -> None:
        if len(msg.data) < 6:
            return
        pose = [float(x) for x in msg.data[:6]]
        self.last_model_pose = pose
        self.last_model_msg_time = self._now_sec()
        if self.mode != 'AUTO':
            return

        if self.awaiting_model_reset:
            self.model_pose_offset = list(pose)
            self.awaiting_model_reset = False
            self.relative_pose = [0.0] * 6
            self.last_forwarded_model_pose = list(self.relative_pose)
            self.status_text = 'AUTO resumed: model output reset at home.'
            self._publish_pose()
            return

        self.relative_pose = self._model_pose_to_relative(pose)
        self.last_forwarded_model_pose = list(self.relative_pose)
        self._publish_pose()

    def _forward_auto_pose(self) -> None:
        if self.mode != 'AUTO':
            return
        if self.awaiting_model_reset:
            return
        if self.last_model_pose is None:
            return
        self.relative_pose = self._model_pose_to_relative(self.last_model_pose)
        self.last_forwarded_model_pose = list(self.relative_pose)
        self._publish_pose()

    def _model_pose_to_relative(self, pose: list[float]) -> list[float]:
        if self.model_pose_offset is None:
            return list(pose)
        return [
            float(pose[i]) - float(self.model_pose_offset[i])
            for i in range(6)
        ]

    def _ee_pose_cb(self, msg: Float64MultiArray) -> None:
        if len(msg.data) < 6:
            return
        now = self._now_sec()
        pose = [float(x) for x in msg.data[:6]]
        self.last_ee_pose = pose
        self.ee_history.append((now, pose))
        while self.ee_history and now - self.ee_history[0][0] > self.stuck_window_sec:
            self.ee_history.popleft()
        self._update_stuck_warning(now)

    def _now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _update_stuck_warning(self, now: float) -> None:
        self.stuck_warning = False
        if self.mode != 'AUTO' or len(self.ee_history) < 2:
            return
        if now - self.ee_history[0][0] < self.stuck_window_sec:
            return
        first = self.ee_history[0][1]
        last = self.ee_history[-1][1]
        linear = sum((last[i] - first[i]) ** 2 for i in range(3)) ** 0.5
        angular = sum((last[i] - first[i]) ** 2 for i in range(3, 6)) ** 0.5
        self.stuck_warning = linear < self.stuck_linear_mm and angular < self.stuck_angular_deg

    def _publish_pose(self) -> None:
        msg = Float64MultiArray()
        msg.data = [float(x) for x in self.relative_pose]
        self.pose_pub.publish(msg)

    def _call_trigger(self, client, timeout: float = 5.0) -> bool:
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
        return bool(result.success)

    def _call_indy(self, code: int, timeout: float = 10.0) -> bool:
        if not self.indy_srv.service_is_ready():
            self.get_logger().warn('indy_srv not available')
            return False
        req = IndyService.Request()
        req.data = int(code)
        future = self.indy_srv.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        result = future.result()
        if result is None:
            self.get_logger().error(f'indy_srv cmd={code}: timeout')
            return False
        if not result.success:
            self.get_logger().warn(f'indy_srv cmd={code}: {result.message}')
        return bool(result.success)

    def _ensure_task_teleop(self) -> bool:
        if self.teleop_ready:
            return True
        if self._call_indy(MSG_TELE_TASK_RLT):
            self.teleop_ready = True
            return True
        return False

    def _start_takeover(self) -> None:
        if self.mode != 'AUTO':
            return
        self.mode = 'TAKEOVER'
        self.awaiting_label = False
        if self.last_forwarded_model_pose is not None:
            self.relative_pose = list(self.last_forwarded_model_pose)
        elif self.last_model_pose is not None:
            self.relative_pose = self._model_pose_to_relative(self.last_model_pose)
        self._publish_pose()
        self._publish_task_name(repeat=5)
        self.status_text = 'TAKEOVER recording: correct alignment, grasp, pull.'
        print('DAgger TAKEOVER: model forwarding stopped, correction recording starts.')
        if not self._call_trigger(self.data_start):
            self.status_text = 'TAKEOVER start failed: data_collector/start not ready.'
            print(self.status_text)
            self.mode = 'PAUSED'
            self._call_indy(MSG_TELE_STOP)
            self.teleop_ready = False
            return
        self._ensure_task_teleop()

    def _request_label(self) -> None:
        if self.mode != 'TAKEOVER':
            return
        self.awaiting_label = True
        warning = self._final_gripper_warning()
        if warning:
            print(warning)
        self.status_text = 'LABEL: A=success, B=fail, X=discard.'
        print(self.status_text)

    def _finish_recording(self, label: str) -> None:
        self.awaiting_label = False
        saved = label != 'discard'
        if label == 'discard':
            print('Discarding DAgger correction.')
            self._call_trigger(self.data_discard)
        else:
            if label == 'success':
                warning = self._final_gripper_warning()
                if warning:
                    print(warning)
                print('Saving DAgger correction as SUCCESS.')
                self._call_trigger(self.data_mark_success)
            else:
                print('Saving DAgger correction as FAIL.')
                self._call_trigger(self.data_mark_fail)
            self._call_trigger(self.data_stop, timeout=300.0)
            self.saved_episode_count += 1

        if self.stop_teleop_after_save:
            self._call_indy(MSG_TELE_STOP)
            self.teleop_ready = False

        if self.auto_home_after_save:
            self._home_and_resume(label=label, saved=saved)
        else:
            self.mode = 'PAUSED'
            self.status_text = 'Saved/finished. Move home and relaunch for next rollout.'

    def _home_and_resume(self, label: str, saved: bool) -> None:
        self.mode = 'HOMING'
        self.awaiting_label = False
        self.status_text = f'{label} handled. Moving Indy7 home...'
        self._update_screen()
        print(self.status_text)

        if not self._move_home():
            self.mode = 'PAUSED'
            self.status_text = 'Home failed. Check robot, then relaunch or recover manually.'
            print(self.status_text)
            return

        self.relative_pose = [0.0] * 6
        self.last_forwarded_model_pose = list(self.relative_pose)
        self.ee_history.clear()
        self.stuck_warning = False
        self.teleop_ready = False
        self.awaiting_model_reset = True
        self.mode = 'AUTO' if self.auto_resume_after_home else 'PAUSED'
        if self.mode == 'AUTO':
            outcome = 'saved' if saved else 'discarded'
            self.status_text = (
                f'{outcome}. Home reached. AUTO waiting for next model baseline.'
            )
        else:
            self.status_text = 'Home reached. Auto resume disabled.'
        print(self.status_text)

    def _move_home(self) -> bool:
        try:
            from neuromeka import IndyDCP3
        except ModuleNotFoundError:
            self.get_logger().error('neuromeka package not found; cannot move home')
            return False

        print(f'Indy7: HOME -> {self.home_joint_deg} deg')
        self._call_indy(MSG_TELE_STOP)
        self.teleop_ready = False

        try:
            indy = IndyDCP3(robot_ip=self.indy_ip, index=0)
            try:
                indy.stop_motion(2)
                time.sleep(0.3)
            except Exception as exc:
                self.get_logger().warn(f'Indy stop_motion before home failed: {exc}')
            indy.movej(
                jtarget=self.home_joint_deg,
                vel_ratio=self.home_vel_ratio,
                acc_ratio=self.home_acc_ratio,
            )
            indy.wait_for_motion_state('is_target_reached')
        except Exception as exc:
            self.get_logger().error(f'Failed to move Indy7 home: {exc}')
            return False

        print('Indy7: HOME reached')
        return True

    def _final_gripper_warning(self) -> Optional[str]:
        if self.last_gripper_action in HOLDING_GRIPPER_ACTIONS:
            return None
        name = GRIPPER_ACTION_NAMES.get(self.last_gripper_action, str(self.last_gripper_action))
        return f'CHECK WARNING: remove_dagger should finish holding pipette, last gripper={name}.'

    def _emergency_stop(self) -> None:
        print('EMERGENCY STOP: model forwarding disabled.')
        was_takeover = self.mode == 'TAKEOVER'
        self.mode = 'PAUSED'
        self.awaiting_label = False
        self._call_indy(MSG_TELE_STOP)
        self.teleop_ready = False
        if was_takeover:
            self._call_trigger(self.data_discard)
        self.status_text = 'PAUSED after BACK. Relaunch recommended.'

    def _handle_gripper(self, action: int) -> None:
        if self.awaiting_label:
            return
        if self.mode == 'AUTO' and action != ACTION_OPEN:
            return
        if self.mode not in ('AUTO', 'TAKEOVER'):
            return
        calls = {
            ACTION_GRASP: (self.gripper_grasp, self.log_grasp, 'GRASP'),
            ACTION_OPEN: (self.gripper_open, self.log_open, 'OPEN'),
            ACTION_PRESS: (self.gripper_press, self.log_press, 'PRESS'),
            ACTION_RELEASE: (self.gripper_release, self.log_release, 'RELEASE'),
        }
        item = calls.get(action)
        if item is None:
            return
        gripper_client, log_client, label = item
        print(f'Gripper: {label}')
        gripper_ok = self._call_trigger(gripper_client)
        log_ok = self._call_trigger(log_client)
        if gripper_ok or log_ok:
            self.last_gripper_action = action

    def _adjust_speed(self, direction: int) -> None:
        self.linear_step = min(
            MAX_LINEAR_STEP_MM,
            max(MIN_LINEAR_STEP_MM, self.linear_step + direction * LINEAR_STEP_DELTA_MM),
        )
        self.angular_step = min(
            MAX_ANGULAR_STEP_DEG,
            max(MIN_ANGULAR_STEP_DEG, self.angular_step + direction * ANGULAR_STEP_DELTA_DEG),
        )
        print(f'step -> linear={self.linear_step:.2f} mm, angular={self.angular_step:.2f} deg')

    def _handle_joybuttondown(self, button: int) -> None:
        back = self._button(BTN_BACK)

        if button == BTN_THUMBL:
            self._adjust_speed(-1)
            return
        if button == BTN_THUMBR:
            self._adjust_speed(1)
            return

        if self.awaiting_label:
            if button == BTN_A:
                self._finish_recording('success')
            elif button == BTN_B:
                self._finish_recording('fail')
            elif button == BTN_X:
                self._finish_recording('discard')
            return

        if back and button == BTN_LB:
            self._adjust_speed(-1)
            return
        if back and button == BTN_RB:
            self._adjust_speed(1)
            return
        if button == BTN_BACK:
            self._emergency_stop()
            return
        if back and button == BTN_A:
            print('Indy7: RECOVER')
            self._call_indy(MSG_RECOVER)
            self.teleop_ready = False
            return
        if back and button == BTN_B:
            print('Indy7: ZERO')
            self._call_indy(MSG_MOVE_ZERO, timeout=15.0)
            self.teleop_ready = False
            return

        if button == BTN_START:
            if self.mode == 'AUTO':
                self._start_takeover()
            elif self.mode == 'TAKEOVER':
                self._request_label()
            return

        if button == BTN_A:
            self._handle_gripper(ACTION_GRASP)
        elif button == BTN_B:
            self._handle_gripper(ACTION_OPEN)
        elif button == BTN_X:
            self._handle_gripper(ACTION_PRESS)
        elif button == BTN_Y:
            self._handle_gripper(ACTION_RELEASE)

    def _update_cartesian_from_joystick(self) -> None:
        if self.mode != 'TAKEOVER' or self.awaiting_label:
            return
        if self._button(BTN_BACK):
            return

        dpad_x, dpad_y = self._dpad()
        lt = self._trigger(2)
        right_x = self._axis(3)
        right_y = self._axis(4)
        rt = self._trigger(5)

        rz = 0.0
        if self._button(BTN_LB):
            rz += 1.0
        if self._button(BTN_RB):
            rz -= 1.0

        deltas = [
            dpad_y * self.linear_step,
            -dpad_x * self.linear_step,
            (rt - lt) * self.linear_step,
            -right_y * self.angular_step,
            -right_x * self.angular_step,
            rz * self.angular_step,
        ]
        if not any(deltas):
            return
        if not self._ensure_task_teleop():
            return
        self.relative_pose = [self.relative_pose[i] + deltas[i] for i in range(6)]
        self._publish_pose()

    def _poll_input(self) -> None:
        if self.input_backend == 'pygame':
            pygame.event.pump()
            return
        while self.joystick_fd is not None:
            ready, _, _ = select.select([self.joystick_fd], [], [], 0.0)
            if not ready:
                return
            try:
                read_size = JS_EVENT_SIZE if self.input_backend == 'linuxjs' else EVDEV_EVENT_SIZE
                data = os.read(self.joystick_fd, read_size)
            except BlockingIOError:
                return
            if self.input_backend == 'linuxjs':
                if len(data) != JS_EVENT_SIZE:
                    return
                _, value, event_type, number = struct.unpack(JS_EVENT_FORMAT, data)
                event_type &= ~JS_EVENT_INIT
                if event_type == JS_EVENT_AXIS:
                    while len(self.axes) <= number:
                        self.axes.append(0.0)
                    self.axes[number] = max(-1.0, min(1.0, value / 32767.0))
                elif event_type == JS_EVENT_BUTTON:
                    while len(self.buttons) <= number:
                        self.buttons.append(0)
                    self.buttons[number] = 1 if value else 0
            else:
                if len(data) != EVDEV_EVENT_SIZE:
                    return
                _, _, event_type, code, value = struct.unpack(EVDEV_EVENT_FORMAT, data)
                if event_type == EV_ABS and code in EVDEV_AXIS_TO_INDEX:
                    index = EVDEV_AXIS_TO_INDEX[code]
                    while len(self.axes) <= index:
                        self.axes.append(0.0)
                    self.axes[index] = self._normalize_evdev_axis(code, value)
                elif event_type == EV_KEY and code in EVDEV_KEY_TO_BUTTON:
                    button = EVDEV_KEY_TO_BUTTON[code]
                    while len(self.buttons) <= button:
                        self.buttons.append(0)
                    self.buttons[button] = 1 if value else 0

    def _normalize_evdev_axis(self, code: int, value: int) -> float:
        if code in (16, 17):
            return max(-1.0, min(1.0, float(value)))
        if code in (2, 5):
            if value < 0:
                return max(-1.0, min(1.0, value / 32767.0))
            return max(-1.0, min(1.0, (value / 1023.0) * 2.0 - 1.0))
        return max(-1.0, min(1.0, value / 32767.0))

    def _axis(self, index: int) -> float:
        if self.input_backend == 'pygame':
            if index >= self.joystick.get_numaxes():
                return 0.0
            value = float(self.joystick.get_axis(index))
        elif index < len(self.axes):
            value = self.axes[index]
        else:
            return 0.0
        if abs(value) < self.deadzone:
            return 0.0
        return value

    def _trigger(self, index: int) -> float:
        if self.input_backend == 'pygame':
            if index >= self.joystick.get_numaxes():
                return 0.0
            raw = float(self.joystick.get_axis(index))
        elif index < len(self.axes):
            raw = self.axes[index]
        else:
            return 0.0
        value = (raw + 1.0) * 0.5
        if value < TRIGGER_DEADZONE:
            return 0.0
        return value

    def _dpad(self) -> tuple[float, float]:
        if self.input_backend == 'pygame':
            if self.joystick.get_numhats() <= 0:
                return (0.0, 0.0)
            hat_x, hat_y = self.joystick.get_hat(0)
            return (float(hat_x), float(hat_y))
        return (self._axis(6), -self._axis(7))

    def _button(self, index: int) -> bool:
        if self.input_backend == 'pygame':
            if index >= self.joystick.get_numbuttons():
                return False
            return bool(self.joystick.get_button(index))
        if index >= len(self.buttons):
            return False
        return bool(self.buttons[index])

    def _button_count(self) -> int:
        if self.input_backend == 'pygame':
            return self.joystick.get_numbuttons()
        return len(self.buttons)

    def _button_pressed(self, index: int) -> bool:
        pressed = self._button(index)
        was_pressed = self._prev_buttons.get(index, False)
        return pressed and not was_pressed

    def _remember_buttons(self) -> None:
        self._prev_buttons = {
            index: self._button(index)
            for index in range(self._button_count())
        }

    def _handle_button_edges(self) -> None:
        for button in range(self._button_count()):
            if self._button_pressed(button):
                self._handle_joybuttondown(button)

    def _raw_axes(self) -> list[float]:
        if self.input_backend == 'pygame':
            return [
                round(float(self.joystick.get_axis(i)), 3)
                for i in range(self.joystick.get_numaxes())
            ]
        return [round(float(value), 3) for value in self.axes]

    def _button_values(self) -> list[int]:
        return [1 if self._button(i) else 0 for i in range(self._button_count())]

    def _debug_input(self) -> None:
        if not self.debug_input:
            return
        control_state = (
            tuple(self._raw_axes()),
            tuple(self._button_values()),
            self.mode,
        )
        if control_state == self._last_debug_state:
            return
        self._last_debug_state = control_state
        print(f'DAgger input mode={self.mode} axes={control_state[0]} buttons={control_state[1]}')

    def _update_screen(self) -> None:
        self.screen.fill((18, 22, 26))
        gripper_name = GRIPPER_ACTION_NAMES.get(self.last_gripper_action, 'unknown')
        model_age = None
        if self.last_model_msg_time is not None:
            model_age = self._now_sec() - self.last_model_msg_time
        lines = [
            'Pipet DAgger Collection',
            f'mode: {self.mode}',
            f'control: {self._control_status_text()}',
            f'task: {self.task_name}',
            f'saved corrections: {self.saved_episode_count}',
            f'controller: {self.input_name} ({self.input_backend})',
            f'cart step: {self.linear_step:.2f} mm / {self.angular_step:.2f} deg',
            f'last gripper: {gripper_name}',
            f'model pose age: {model_age:.2f}s' if model_age is not None else 'model pose age: none',
            f'status: {self.status_text}',
            'AUTO: B=open gripper, START when model is stuck/wrong/dangerous',
            'TAKEOVER: D-pad/LT/RT/right stick/LB/RB correct, A/B/X/Y gripper',
            'Finish: START then A success / B fail / X discard',
            'Speed: left stick click slower / right stick click faster',
            'Safety: BACK stop/discard | BACK+A/B recover/zero',
        ]
        if self.stuck_warning:
            lines.append('WARNING: EE pose barely changed. Consider START takeover.')
        if self.awaiting_label:
            lines.append('WAITING LABEL: A success / B fail / X discard')

        for idx, line in enumerate(lines):
            color = (235, 235, 235)
            if line.startswith('mode:'):
                color = (90, 220, 130) if self.mode == 'AUTO' else (255, 190, 90)
            if line.startswith('control:'):
                color = (90, 220, 130) if self.mode == 'TAKEOVER' and not self.awaiting_label else (255, 220, 120)
            if line.startswith('status:'):
                color = (120, 190, 255)
            if line.startswith('WARNING') or line.startswith('WAITING'):
                color = (255, 120, 90)
            surf = self.font.render(line, True, color)
            self.screen.blit(surf, (24, 20 + idx * 28))
        pygame.display.flip()

    def _control_status_text(self) -> str:
        if self.mode == 'AUTO':
            if self.awaiting_model_reset:
                return 'AUTO locked until next model baseline'
            return 'MODEL AUTO active; controller START takeover, B open'
        if self.mode == 'TAKEOVER':
            if self.awaiting_label:
                return 'LABEL ONLY; A success, B fail, X discard'
            return 'HUMAN TAKEOVER ACTIVE; controller drives Indy7'
        if self.mode == 'HOMING':
            return 'LOCKED; moving home before next rollout'
        if self.mode == 'PAUSED':
            return 'PAUSED; relaunch or recover manually'
        return 'UNKNOWN'

    def run(self) -> None:
        try:
            while self.is_running and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                self._poll_input()
                self._handle_button_edges()
                self._update_cartesian_from_joystick()
                self._forward_auto_pose()
                self._debug_input()
                self._update_screen()
                self._remember_buttons()
                self.clock.tick(ROBOT_CONTROL_HZ)
        except KeyboardInterrupt:
            pass
        finally:
            if self.mode == 'TAKEOVER':
                self._call_trigger(self.data_stop, timeout=300.0)
            self._call_indy(MSG_TELE_STOP)
            if self.joystick_fd is not None:
                os.close(self.joystick_fd)
            pygame.quit()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = DaggerSupervisorNode()
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
