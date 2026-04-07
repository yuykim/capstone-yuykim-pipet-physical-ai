#!/usr/bin/env python3
"""
System Teleop Node for Pipet Physical AI.

Keyboard interface that calls Indy7 services (teaching mode, home, recover),
Mark7 gripper services (grasp, open, press), and data collector services
(start/stop recording).

Key mapping follows interface_spec.md section 2.5.
"""

import sys
import termios
import tty
import select
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_srvs.srv import Trigger
from indy_interfaces.srv import IndyService

# Indy7 command codes (from indy_define.py)
MSG_RECOVER = 1
MSG_MOVE_HOME = 2
MSG_DIRECT_TEACHING_ON = 9
MSG_DIRECT_TEACHING_OFF = 10
MSG_MOVE_SAFE = 11


class KeyboardReader:
    """Non-blocking keyboard input reader."""

    def __init__(self):
        if not sys.stdin.isatty():
            raise RuntimeError(
                'stdin is not a TTY. Run this node directly, not via launch.'
            )
        self.settings = termios.tcgetattr(sys.stdin)

    def read_one(self) -> str:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def restore(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


class SystemTeleopNode(Node):
    """
    Integrated teleop node for Indy7 + Mark7 + data collection.

    Key mapping:
        SPACE  - Toggle recording (start/stop)
        H      - Indy7 home position
        D      - Direct teaching ON
        d      - Direct teaching OFF
        G      - Mark7 grasp
        O      - Mark7 open
        P      - Mark7 press (pipette)
        R      - Mark7 release (thumb open)
        E      - Error recovery + resume teaching
        S      - Show status
        Q      - Quit
    """

    def __init__(self):
        super().__init__('system_teleop_node')

        # Service clients -- Indy7
        self.indy_srv = self.create_client(IndyService, 'indy_srv')

        # Service clients -- Mark7 gripper
        self.gripper_grasp = self.create_client(Trigger, '/gripper/grasp')
        self.gripper_open = self.create_client(Trigger, '/gripper/open')
        self.gripper_press = self.create_client(Trigger, '/gripper/press')
        self.gripper_release = self.create_client(Trigger, '/gripper/release')

        # Service clients -- Data collector
        self.data_start = self.create_client(Trigger, '/data_collector/start')
        self.data_stop = self.create_client(Trigger, '/data_collector/stop')
        self.data_mark_success = self.create_client(Trigger, '/data_collector/mark_success')
        self.data_mark_fail = self.create_client(Trigger, '/data_collector/mark_fail')
        self.data_discard = self.create_client(Trigger, '/data_collector/discard')

        # Service clients -- Data collector gripper action logging
        self.log_grasp = self.create_client(Trigger, '/data_collector/log_grasp')
        self.log_open = self.create_client(Trigger, '/data_collector/log_open')
        self.log_press = self.create_client(Trigger, '/data_collector/log_press')
        self.log_release = self.create_client(Trigger, '/data_collector/log_release')

        # Subscriber -- recording status
        self._is_recording = False
        self.create_subscription(
            Bool, '/data_collector/is_recording',
            self._recording_status_cb, 1
        )

        # State
        self._teaching_enabled = False
        self.is_running = True

        # Keyboard
        self.keyboard = KeyboardReader()

        # Wait for essential services
        self._wait_for_services()

        self._print_instructions()

    def _wait_for_services(self):
        """Wait for Indy7 service. Mark7 and data collector are optional."""
        self.get_logger().info('Waiting for indy_srv...')
        while not self.indy_srv.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('indy_srv not available, waiting...')
        self.get_logger().info('indy_srv connected')

        # Check optional services (non-blocking)
        mark7_ready = self.gripper_grasp.wait_for_service(timeout_sec=2.0)
        data_ready = self.data_start.wait_for_service(timeout_sec=2.0)

        if mark7_ready:
            self.get_logger().info('Mark7 gripper services connected')
        else:
            self.get_logger().warn('Mark7 gripper services not available (G/O/P keys disabled)')

        if data_ready:
            self.get_logger().info('Data collector services connected')
        else:
            self.get_logger().warn('Data collector not available (SPACE key disabled)')

    def _recording_status_cb(self, msg: Bool):
        self._is_recording = msg.data

    def _print_instructions(self):
        print('\n' + '=' * 60)
        print('  PIPET SYSTEM TELEOP - Indy7 + Mark7')
        print('=' * 60)
        print('\n  Recording:')
        print('    [SPACE]  Start/Stop recording')
        print('\n  Indy7:')
        print('    [H]  Home position')
        print('    [D]  Direct teaching ON')
        print('    [d]  Direct teaching OFF')
        print('    [E]  Error recovery + resume teaching')
        print('\n  Mark7 Gripper:')
        print('    [G]  Grasp (pipette)')
        print('    [O]  Open (release)')
        print('    [P]  Press (pipette button)')
        print('    [R]  Release (thumb open)')
        print('\n  Other:')
        print('    [S]  Show status')
        print('    [Q]  Quit')
        print('\n  Status:')
        print(f'    Teaching: {"ON" if self._teaching_enabled else "OFF"}')
        print(f'    Recording: {"YES" if self._is_recording else "NO"}')
        print('=' * 60 + '\n')

    # -- Indy7 service calls --

    def _call_indy(self, command: int, timeout: float = 5.0) -> bool:
        req = IndyService.Request()
        req.data = command
        future = self.indy_srv.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        if future.result() is not None and future.result().success:
            return True
        self.get_logger().error(
            f'Indy service call failed (cmd={command}): '
            f'{future.result().message if future.result() else "timeout"}'
        )
        return False

    # -- Trigger service call helper --

    def _call_trigger(self, client, timeout: float = 5.0) -> bool:
        if not client.service_is_ready():
            self.get_logger().warn(f'Service not ready: {client.srv_name}')
            return False
        req = Trigger.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        if future.result() is not None:
            result = future.result()
            if not result.success:
                self.get_logger().warn(f'{client.srv_name}: {result.message}')
            return result.success
        self.get_logger().error(f'{client.srv_name}: timeout')
        return False

    # -- Key handlers --

    def _handle_space(self):
        if self._is_recording:
            print('\nStopping recording...')
            print('Result? [Y] Success / [N] Fail / [X] Discard: ', end='', flush=True)
            while True:
                result_key = self.keyboard.read_one()
                if result_key and result_key.upper() in ('Y', 'N', 'X'):
                    break
            choice = result_key.upper()
            if choice == 'X':
                print('DISCARD')
                self._call_trigger(self.data_discard)
                print('Recording discarded.\n')
            else:
                if choice == 'Y':
                    self._call_trigger(self.data_mark_success)
                    print('SUCCESS')
                else:
                    self._call_trigger(self.data_mark_fail)
                    print('FAIL')
                print('Saving data (this may take a moment)...')
                req = Trigger.Request()
                future = self.data_stop.call_async(req)
                rclpy.spin_until_future_complete(self, future, timeout_sec=120.0)
                if future.result() is not None and future.result().success:
                    print(f'{future.result().message}\n')
                else:
                    print('Failed to stop recording.\n')
        else:
            print('\nStarting recording...')
            if self._call_trigger(self.data_start):
                print('Recording started. Press [SPACE] to stop.\n')
            else:
                print('Failed to start recording.\n')

    def _handle_home(self):
        if self._is_recording:
            self.get_logger().warn('Cannot move to home while recording')
            return
        print('\nMoving to home position...')
        if self._call_indy(MSG_MOVE_HOME, timeout=15.0):
            print('Home position reached.\n')
        else:
            print('Failed to move to home.\n')

    def _handle_teaching_on(self):
        print('\nEnabling direct teaching mode...')
        if self._call_indy(MSG_DIRECT_TEACHING_ON):
            self._teaching_enabled = True
            print('Teaching mode ON. You can move the robot arm.\n')
        else:
            print('Failed to enable teaching mode.\n')

    def _handle_teaching_off(self):
        print('\nDisabling direct teaching mode...')
        if self._call_indy(MSG_DIRECT_TEACHING_OFF):
            self._teaching_enabled = False
            print('Teaching mode OFF.\n')
        else:
            print('Failed to disable teaching mode.\n')

    def _handle_grasp(self):
        print('Gripper: GRASP')
        self._call_trigger(self.gripper_grasp)
        self._call_trigger(self.log_grasp)

    def _handle_open(self):
        print('Gripper: OPEN')
        self._call_trigger(self.gripper_open)
        self._call_trigger(self.log_open)

    def _handle_press(self):
        print('Gripper: PRESS')
        self._call_trigger(self.gripper_press)
        self._call_trigger(self.log_press)

    def _handle_release(self):
        print('Gripper: RELEASE (thumb open)')
        self._call_trigger(self.gripper_release)
        self._call_trigger(self.log_release)

    def _handle_error_recovery(self):
        if self._is_recording:
            print('\nStopping recording before recovery...')
            self._call_trigger(self.data_stop)

        print('\n' + '-' * 60)
        print('  ERROR RECOVERY')
        print('-' * 60)

        print('  Step 1/3: Recovering from error...')
        if not self._call_indy(MSG_RECOVER):
            print('  Recovery failed.\n')
            return

        time.sleep(0.5)

        print('  Step 2/3: Moving to safe positions...')
        self._call_indy(MSG_MOVE_SAFE, timeout=15.0)
        time.sleep(1.0)

        print('  Step 3/3: Re-enabling teaching mode...')
        if self._call_indy(MSG_DIRECT_TEACHING_ON):
            self._teaching_enabled = True
            print('  Recovery complete! Teaching mode ON.\n')
        else:
            print('  Failed to re-enable teaching mode.\n')
        print('-' * 60 + '\n')

    def _handle_status(self):
        print('\n' + '-' * 40)
        print(f'  Teaching: {"ON" if self._teaching_enabled else "OFF"}')
        print(f'  Recording: {"YES" if self._is_recording else "NO"}')
        mark7 = 'connected' if self.gripper_grasp.service_is_ready() else 'not available'
        data = 'connected' if self.data_start.service_is_ready() else 'not available'
        print(f'  Mark7: {mark7}')
        print(f'  Data Collector: {data}')
        print('-' * 40 + '\n')

    def _handle_quit(self):
        print('\nShutting down...')
        if self._is_recording:
            self._call_trigger(self.data_stop)
        if self._teaching_enabled:
            self._call_indy(MSG_DIRECT_TEACHING_OFF)
        self.is_running = False
        print('Goodbye.\n')

    # -- Main loop --

    def run(self):
        try:
            while self.is_running and rclpy.ok():
                key = self.keyboard.read_one()
                if not key:
                    continue

                key_upper = key.upper() if len(key) == 1 else key

                if key == ' ':
                    self._handle_space()
                elif key_upper == 'H':
                    self._handle_home()
                elif key_upper == 'D' and key == 'D':
                    self._handle_teaching_on()
                elif key_upper == 'D' and key == 'd':
                    self._handle_teaching_off()
                elif key_upper == 'G':
                    self._handle_grasp()
                elif key_upper == 'O':
                    self._handle_open()
                elif key_upper == 'P':
                    self._handle_press()
                elif key_upper == 'R':
                    self._handle_release()
                elif key_upper == 'E':
                    self._handle_error_recovery()
                elif key_upper == 'S':
                    self._handle_status()
                elif key_upper == 'Q':
                    self._handle_quit()
                    break

        except KeyboardInterrupt:
            self._handle_quit()
        finally:
            self.keyboard.restore()

    def destroy_node(self):
        if self._is_recording:
            self._call_trigger(self.data_stop)
        if self._teaching_enabled:
            self._call_indy(MSG_DIRECT_TEACHING_OFF)
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SystemTeleopNode()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()
        spin_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()
