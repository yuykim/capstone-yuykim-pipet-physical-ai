#!/usr/bin/env python3
"""
Pygame Xbox controller teleop node for Indy7 + Mark7 data collection.

This mirrors keyboard_servo_node's ROS behavior:
  - start Indy task teleop in RELATIVE mode
  - keep a cumulative relative target [x,y,z,rx,ry,rz]
  - publish it to /indy/teleop_pose
  - call Mark7 gripper services and data collector logging services
  - control data collection start/stop/labeling from the controller
"""

import os
import select
import struct
from glob import glob

os.environ.setdefault('SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS', '1')
os.environ.setdefault('SDL_JOYSTICK_HIDAPI', '0')
os.environ.setdefault('SDL_JOYSTICK_HIDAPI_XBOX', '0')

import pygame

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float64MultiArray, String
from std_srvs.srv import Trigger
from indy_interfaces.srv import IndyService


ROBOT_CONTROL_HZ = 30
DEFAULT_INDY_IP = '192.168.1.10'
DEFAULT_INPUT_BACKEND = 'linuxevdev'
DEFAULT_EVENT_DEVICE = ''
DEFAULT_JOYSTICK_DEVICE = '/dev/input/js0'
DEFAULT_JOYSTICK_INDEX = 0
LINEAR_STEP_MM = 1.0
ANGULAR_STEP_DEG = 1.0
LINEAR_STEP_DELTA_MM = 0.25
ANGULAR_STEP_DELTA_DEG = 0.25
MIN_LINEAR_STEP_MM = 0.1
MAX_LINEAR_STEP_MM = 5.0
MIN_ANGULAR_STEP_DEG = 0.1
MAX_ANGULAR_STEP_DEG = 5.0
DEADZONE = 0.18
TRIGGER_DEADZONE = 0.08
HOME_JOINT_DEG = [0.00, 25.00, -115.000, 90.0, 0.00, 0.000]
HOME_VEL_RATIO = 20
HOME_ACC_RATIO = 100

MSG_RECOVER = 1
MSG_MOVE_ZERO = 3
MSG_TELE_TASK_RLT = 5
MSG_TELE_STOP = 8

ACTION_GRASP = 1
ACTION_OPEN = 2
ACTION_PRESS = 3
ACTION_RELEASE = 4

GRIPPER_ACTION_NAMES = {
    0: 'hold',
    1: 'grasp',
    2: 'open',
    3: 'press',
    4: 'release',
}
HOLDING_GRIPPER_ACTIONS = {ACTION_GRASP, ACTION_PRESS}
RELEASED_GRIPPER_ACTIONS = {ACTION_OPEN, ACTION_RELEASE}

BTN_A = 0
BTN_B = 1
BTN_X = 2
BTN_Y = 3
BTN_LB = 4
BTN_RB = 5
BTN_BACK = 6
BTN_START = 7

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


class XboxServoNode(Node):
    def __init__(self):
        super().__init__('xbox_servo_node')

        self.declare_parameter('indy_ip', DEFAULT_INDY_IP)
        self.declare_parameter('input_backend', DEFAULT_INPUT_BACKEND)
        self.declare_parameter('event_device', DEFAULT_EVENT_DEVICE)
        self.declare_parameter('joystick_device', DEFAULT_JOYSTICK_DEVICE)
        self.declare_parameter('joystick_index', DEFAULT_JOYSTICK_INDEX)
        self.declare_parameter('linear_step_mm', LINEAR_STEP_MM)
        self.declare_parameter('angular_step_deg', ANGULAR_STEP_DEG)
        self.declare_parameter('deadzone', DEADZONE)
        self.declare_parameter('debug_input', False)
        self.declare_parameter('two_stage_collection', True)
        self.declare_parameter('remove_task_name', 'remove')
        self.declare_parameter('insert_task_name', 'insert')

        self.indy_ip = self.get_parameter('indy_ip').value
        self.input_backend = self.get_parameter('input_backend').value
        self.event_device = self.get_parameter('event_device').value
        self.joystick_device = self.get_parameter('joystick_device').value
        self.joystick_index = int(self.get_parameter('joystick_index').value)
        self.linear_step = float(self.get_parameter('linear_step_mm').value)
        self.angular_step = float(self.get_parameter('angular_step_deg').value)
        self.deadzone = float(self.get_parameter('deadzone').value)
        self.debug_input = bool(self.get_parameter('debug_input').value)
        self.two_stage_collection = bool(self.get_parameter('two_stage_collection').value)
        self.remove_task_name = self._sanitize_task_name(self.get_parameter('remove_task_name').value)
        self.insert_task_name = self._sanitize_task_name(self.get_parameter('insert_task_name').value)

        self.pose_pub = self.create_publisher(Float64MultiArray, '/indy/teleop_pose', 10)
        self.task_pub = self.create_publisher(String, '/data_collector/task_name', 10)
        self.task_pub_timer = self.create_timer(0.5, self._publish_current_task)

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
        self.teleop_mode = None
        self.is_recording = False
        self.awaiting_label = False
        self.collection_task = self.remove_task_name if self.two_stage_collection else ''
        self.recording_task = None
        self.workflow_prompt = None
        self.workflow_status = (
            'REMOVE ready: START records.'
            if self.two_stage_collection
            else 'Manual collection mode.'
        )
        self.last_gripper_action = 0
        self.is_running = True
        self._prev_buttons = {}
        self._last_debug_state = None
        self.joystick = None
        self.joystick_fd = None
        self.input_name = ''
        self.axes = [0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        self.buttons = [0] * 12

        self._init_pygame()
        self._wait_for_indy_service()
        self._print_help()

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((760, 420))
        pygame.display.set_caption('Pipet Xbox Teleop - Indy7 + Mark7')
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
            self.get_logger().info(
                f'Using pygame joystick {self.joystick_index}: {self.input_name} '
                f'({self.joystick.get_numaxes()} axes, '
                f'{self.joystick.get_numbuttons()} buttons, '
                f'{self.joystick.get_numhats()} hats)'
            )
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

    def _resolve_event_device(self):
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

    def _wait_for_indy_service(self):
        self.get_logger().info('Waiting for indy_srv...')
        while rclpy.ok() and not self.indy_srv.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('indy_srv not available, waiting...')
        self.get_logger().info('indy_srv connected')

    def _print_help(self):
        print('\n' + '=' * 72)
        print('  PYGAME XBOX TELEOP - control_indy7 style')
        print('=' * 72)
        print('  Move:       D-pad=x/y   LT/RT=z -/+')
        print('  Rotate:     Right stick=rx/ry   LB/RB=rz +/-')
        print('  Speed:      BACK+LB=slower   BACK+RB=faster')
        print('  Gripper:    A=grasp  B=open  X=press  Y=release')
        print('  Recording:  START=start/label stop, then A=success B=fail X=discard')
        print('  Workflow:   remove -> ask insert; A=arm insert, B=skip insert')
        print('  Indy7:      BACK=stop teleop   BACK+B=zero   BACK+Y=home   BACK+A=recover')
        print('  Quit:       window close or Ctrl+C')
        print('=' * 72 + '\n')

    @staticmethod
    def _sanitize_task_name(value: str) -> str:
        cleaned = str(value).strip().lower().replace(' ', '_')
        return ''.join(ch for ch in cleaned if ch.isalnum() or ch in ('_', '-'))

    def _task_label(self, task_name=None):
        task = self.collection_task if task_name is None else task_name
        return task.upper() if task else 'MANUAL'

    def _publish_current_task(self, repeat: int = 1):
        msg = String()
        msg.data = self.collection_task
        for _ in range(max(1, repeat)):
            self.task_pub.publish(msg)

    def _set_collection_task(self, task_name: str, status: str):
        self.collection_task = self._sanitize_task_name(task_name)
        self.workflow_status = status
        self._publish_current_task()
        print(f'Collection task: {self._task_label()} - {status}')

    def _expected_final_gripper_actions(self, task_name: str):
        task = task_name.lower()
        if task in ('remove', 'pick', 'pull', 'extract'):
            return 'holding', HOLDING_GRIPPER_ACTIONS
        if task in ('insert', 'return', 'place'):
            return 'released', RELEASED_GRIPPER_ACTIONS
        return None, set()

    def _final_gripper_warning(self, task_name: str):
        expected_name, expected_actions = self._expected_final_gripper_actions(task_name)
        if not expected_name:
            return None
        if self.last_gripper_action in expected_actions:
            return None
        final_name = GRIPPER_ACTION_NAMES.get(
            self.last_gripper_action,
            f'unknown({self.last_gripper_action})',
        )
        expected_list = ', '.join(
            GRIPPER_ACTION_NAMES[action] for action in sorted(expected_actions)
        )
        return (
            f'CHECK WARNING: {self._task_label(task_name)} should finish with '
            f'gripper {expected_name} ({expected_list}), but last action is {final_name}.'
        )

    def _ee_pose_cb(self, msg: Float64MultiArray):
        if len(msg.data) == 6:
            self.ee_pose = list(msg.data)

    def _joint_state_cb(self, msg: JointState):
        import math
        self.joint_positions_deg = [math.degrees(p) for p in msg.position]

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

    def _move_home(self):
        try:
            from neuromeka import IndyDCP3
        except ModuleNotFoundError:
            self.get_logger().error('neuromeka package not found; cannot move home')
            return False

        print(f'Indy7: HOME -> {HOME_JOINT_DEG} deg')
        self._call_indy(MSG_TELE_STOP)
        indy = IndyDCP3(robot_ip=self.indy_ip, index=0)
        indy.movej(
            jtarget=HOME_JOINT_DEG,
            vel_ratio=HOME_VEL_RATIO,
            acc_ratio=HOME_ACC_RATIO,
        )
        indy.wait_for_motion_state('is_target_reached')
        self._reset_teleop_targets()
        print('Indy7: HOME reached')
        return True

    def _ensure_task_teleop(self):
        if self.teleop_mode == 'task':
            return True
        if self._call_indy(MSG_TELE_TASK_RLT):
            self.teleop_mode = 'task'
            self.relative_pose = [0.0] * 6
            return True
        return False

    def _reset_teleop_targets(self):
        self.teleop_mode = None
        self.relative_pose = [0.0] * 6

    def _publish_pose(self):
        msg = Float64MultiArray()
        msg.data = list(self.relative_pose)
        self.pose_pub.publish(msg)

    def _poll_input(self):
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

    def _dpad(self):
        if self.input_backend == 'pygame':
            if self.joystick.get_numhats() <= 0:
                return (0.0, 0.0)
            hat_x, hat_y = self.joystick.get_hat(0)
            return (float(hat_x), float(hat_y))

        # Linux ABS_HAT0Y is usually -1 for up and +1 for down. Normalize to
        # pygame's convention: up is +1.
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

    def _raw_axes(self):
        if self.input_backend == 'pygame':
            return [
                round(float(self.joystick.get_axis(i)), 3)
                for i in range(self.joystick.get_numaxes())
            ]
        return [round(float(value), 3) for value in self.axes]

    def _button_values(self):
        return [1 if self._button(i) else 0 for i in range(self._button_count())]

    def _button_pressed(self, index: int) -> bool:
        pressed = self._button(index)
        was_pressed = self._prev_buttons.get(index, False)
        return pressed and not was_pressed

    def _remember_buttons(self):
        self._prev_buttons = {
            index: self._button(index)
            for index in range(self._button_count())
        }

    def _handle_gripper(self, action: int):
        if action == ACTION_GRASP:
            print('Gripper: GRASP')
            gripper_ok = self._call_trigger(self.gripper_grasp)
            log_ok = self._call_trigger(self.log_grasp)
        elif action == ACTION_OPEN:
            print('Gripper: OPEN')
            gripper_ok = self._call_trigger(self.gripper_open)
            log_ok = self._call_trigger(self.log_open)
        elif action == ACTION_PRESS:
            print('Gripper: PRESS')
            gripper_ok = self._call_trigger(self.gripper_press)
            log_ok = self._call_trigger(self.log_press)
        elif action == ACTION_RELEASE:
            print('Gripper: RELEASE')
            gripper_ok = self._call_trigger(self.gripper_release)
            log_ok = self._call_trigger(self.log_release)
        else:
            return

        if gripper_ok or log_ok:
            self.last_gripper_action = action

    def _handle_record_button(self):
        if self.workflow_prompt:
            print('Choose workflow first: A=collect INSERT / B=skip INSERT')
            return
        if self.is_recording:
            self.awaiting_label = True
            task = self.recording_task or self.collection_task
            warning = self._final_gripper_warning(task)
            if warning:
                print(warning)
            print('Result? A=success / B=fail / X=discard')
            return
        self.recording_task = self.collection_task
        self._publish_current_task(repeat=3)
        print(f'Starting {self._task_label(self.recording_task)} recording...')
        if not self._call_trigger(self.data_start):
            self.recording_task = None

    def _adjust_speed(self, direction: int):
        self.linear_step = min(
            MAX_LINEAR_STEP_MM,
            max(MIN_LINEAR_STEP_MM, self.linear_step + direction * LINEAR_STEP_DELTA_MM),
        )
        self.angular_step = min(
            MAX_ANGULAR_STEP_DEG,
            max(MIN_ANGULAR_STEP_DEG, self.angular_step + direction * ANGULAR_STEP_DELTA_DEG),
        )
        print(
            f'step -> linear={self.linear_step:.2f} mm, '
            f'angular={self.angular_step:.2f} deg'
        )

    def _finish_recording(self, label: str):
        self.awaiting_label = False
        finished_task = self.recording_task or self.collection_task
        if label == 'discard':
            print(f'Discarding {self._task_label(finished_task)} recording...')
            self._call_trigger(self.data_discard)
            self.recording_task = None
            return

        warning = self._final_gripper_warning(finished_task)
        if warning:
            print(warning)

        if label == 'success':
            print(f'Marking {self._task_label(finished_task)} SUCCESS and saving...')
            self._call_trigger(self.data_mark_success)
        else:
            print(f'Marking {self._task_label(finished_task)} FAIL and saving...')
            self._call_trigger(self.data_mark_fail)

        self._call_trigger(self.data_stop, timeout=300.0)
        self._after_recording_finished(finished_task, label)

    def _after_recording_finished(self, finished_task: str, label: str):
        self.recording_task = None
        if not self.two_stage_collection:
            return

        if finished_task == self.remove_task_name and label == 'success':
            self.workflow_prompt = 'ask_insert'
            self.workflow_status = (
                'REMOVE saved. A=arm INSERT, B=skip.'
            )
            print(self.workflow_status)
        elif finished_task == self.insert_task_name:
            self.workflow_prompt = None
            self._set_collection_task(
                self.remove_task_name,
                'INSERT saved. Next REMOVE ready.',
            )
        elif finished_task == self.remove_task_name:
            self._set_collection_task(
                self.remove_task_name,
                'Repeat REMOVE when ready.',
            )

    def _handle_workflow_prompt(self, button: int) -> bool:
        if self.workflow_prompt != 'ask_insert':
            return False
        if button == BTN_A:
            self.workflow_prompt = None
            self._set_collection_task(
                self.insert_task_name,
                'INSERT armed. Move robot, then START records.',
            )
            return True
        if button == BTN_B:
            self.workflow_prompt = None
            self._set_collection_task(
                self.remove_task_name,
                'INSERT skipped. Next REMOVE ready.',
            )
            return True
        return True

    def _handle_joybuttondown(self, button: int):
        if self.awaiting_label:
            if button == BTN_A:
                self._finish_recording('success')
            elif button == BTN_B:
                self._finish_recording('fail')
            elif button == BTN_X:
                self._finish_recording('discard')
            return

        if self._handle_workflow_prompt(button):
            return

        back = self._button(BTN_BACK)
        if button == BTN_START:
            self._handle_record_button()
        elif back and button == BTN_A:
            print('Indy7: RECOVER')
            self._call_indy(MSG_RECOVER)
            self._reset_teleop_targets()
        elif back and button == BTN_B:
            print('Indy7: ZERO')
            self._call_indy(MSG_MOVE_ZERO, timeout=15.0)
            self._reset_teleop_targets()
        elif back and button == BTN_Y:
            self._move_home()
        elif back and button == BTN_LB:
            self._adjust_speed(-1)
        elif back and button == BTN_RB:
            self._adjust_speed(1)
        elif button == BTN_BACK:
            print('Indy7: STOP TELEOP')
            self._call_indy(MSG_TELE_STOP)
            self._reset_teleop_targets()
        elif button == BTN_A:
            self._handle_gripper(ACTION_GRASP)
        elif button == BTN_B:
            self._handle_gripper(ACTION_OPEN)
        elif button == BTN_X:
            self._handle_gripper(ACTION_PRESS)
        elif button == BTN_Y:
            self._handle_gripper(ACTION_RELEASE)

    def _handle_button_edges(self):
        for button in range(self._button_count()):
            if self._button_pressed(button):
                self._handle_joybuttondown(button)

    def _update_cartesian_from_joystick(self):
        if self.awaiting_label:
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

        self.relative_pose = [
            self.relative_pose[i] + deltas[i] for i in range(6)
        ]
        self._publish_pose()

    def _debug_input(self):
        if not self.debug_input:
            return

        raw_axes = self._raw_axes()
        buttons = self._button_values()
        control_state = (
            round(self._dpad()[0], 3),
            round(self._dpad()[1], 3),
            round(self._trigger(2), 3),
            round(self._axis(3), 3),
            round(self._axis(4), 3),
            round(self._trigger(5), 3),
            round(self.linear_step, 2),
            round(self.angular_step, 2),
            tuple(buttons),
        )
        if control_state == self._last_debug_state:
            return

        self._last_debug_state = control_state
        print(
            f'Xbox input backend={self.input_backend} '
            f'raw_axes={raw_axes} controls={control_state[:-1]} buttons={buttons}'
        )

    def _update_screen(self):
        self.screen.fill((18, 22, 26))
        shown_task = self.recording_task if self.is_recording else self.collection_task
        gripper_name = GRIPPER_ACTION_NAMES.get(
            self.last_gripper_action,
            f'unknown({self.last_gripper_action})',
        )
        lines = [
            'Pipet Xbox Teleop',
            f'controller: {self.input_name} ({self.input_backend})',
            f'cart step: {self.linear_step:.1f} mm / {self.angular_step:.1f} deg',
            f'teleop mode: {self.teleop_mode or "idle"}',
            f'task: {self._task_label(shown_task)}',
            f'recording: {"YES" if self.is_recording else "NO"}',
            f'last gripper: {gripper_name}',
            f'workflow: {self.workflow_status}',
            'Move D-pad + LT/RT | Rotate right stick + LB/RB',
            'Speed BACK+LB slower | BACK+RB faster',
            'Gripper A=grasp B=open X=press Y=release',
            'START=start/stop, then A/B/X label | BACK=stop | BACK+A/B/Y=recover/zero/home',
        ]
        if self.awaiting_label:
            lines.append('WAITING LABEL: A success / B fail / X discard')
        elif self.workflow_prompt == 'ask_insert':
            lines.append('COLLECT INSERT? A yes / B skip')
        for idx, line in enumerate(lines):
            color = (240, 240, 240)
            if line.startswith('task:'):
                color = (120, 190, 255)
            if line.startswith('recording:'):
                color = (80, 220, 120) if self.is_recording else (220, 220, 120)
            if self.awaiting_label and idx == len(lines) - 1:
                color = (255, 190, 90)
            if self.workflow_prompt and idx == len(lines) - 1:
                color = (255, 190, 90)
            surf = self.font.render(line, True, color)
            self.screen.blit(surf, (24, 20 + idx * 28))
        pygame.display.flip()

    def run(self):
        try:
            while self.is_running and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False

                self._poll_input()
                self._handle_button_edges()
                self._update_cartesian_from_joystick()
                self._debug_input()
                self._update_screen()
                self._remember_buttons()
                self.clock.tick(ROBOT_CONTROL_HZ)

        except KeyboardInterrupt:
            pass
        finally:
            if self.is_recording:
                self._call_trigger(self.data_stop, timeout=300.0)
            self._call_indy(MSG_TELE_STOP)
            if self.joystick_fd is not None:
                os.close(self.joystick_fd)
            pygame.quit()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = XboxServoNode()
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
