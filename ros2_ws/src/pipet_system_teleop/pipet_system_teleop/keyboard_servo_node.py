#!/usr/bin/env python3
"""
Keyboard Servo Node for Indy7 (Neuromeka-style + gripper).

Publishes:
    /indy/teleop_pose   Float64MultiArray  - Cartesian target [mm, deg]
    /indy/teleop_joint  Float64MultiArray  - Joint target [deg]

Calls:
    indy_srv            (Home / Zero / Recover / TeleopStop)
    /gripper/{grasp,open,press,release}

Key layout (Neuromeka standard + gripper):

  Cartesian jog (workspace):
    Up / Down arrow         -> x +/-
    Left / Right arrow      -> y +/-
    .  /  ;                 -> z +/-
    N  /  M  /  ,           -> rx (U) / ry (V) / rz (W) jog (direction by [R])

  Joint jog:
    1 / 2 / 3 / 4 / 5 / 6 / 7  -> joint 1~7 (direction by [R])

  Frame:
    W / E                   -> Global (base) / Tool frame for Cartesian jog

  Speed:
    -, +                    -> joint step size (deg) down/up
    9, 0                    -> Cartesian step size (mm, deg) down/up
    R                       -> Toggle jog direction (+1 <-> -1)

  Indy7 commands (via indy_srv):
    H                       -> Move Home
    Z                       -> Move Zero
    S                       -> Recover (clear error)
    P                       -> Stop teleop

  Mark7 gripper:
    G                       -> Grasp
    O                       -> Open
    B                       -> Press (Button)
    V                       -> Release (thumb open)

  Quit:
    Q
"""

import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from std_srvs.srv import Trigger
from indy_interfaces.srv import IndyService


# Default step sizes
LINEAR_STEP_MM = 5.0
ANGULAR_STEP_DEG = 2.0
JOINT_STEP_DEG = 1.0

# Indy7 service command codes (must match indy_define.py)
MSG_RECOVER = 1
MSG_MOVE_HOME = 2
MSG_MOVE_ZERO = 3
MSG_TELE_STOP = 8


class KeyboardReader:
    """Reads single keys including arrow keys (escape sequences)."""

    ARROW_MAP = {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}

    def __init__(self):
        if not sys.stdin.isatty():
            raise RuntimeError('stdin is not a TTY')
        self.fd = sys.stdin.fileno()
        self.settings = termios.tcgetattr(self.fd)
        # cbreak: read each char without Enter, but keep output processing
        # (so newlines still produce CRLF, no staircase output).
        tty.setcbreak(self.fd)

    def read_one(self) -> str:
        """
        Returns:
            - single character for normal keys
            - 'UP'|'DOWN'|'LEFT'|'RIGHT' for arrow keys
            - '' if no input
        """
        # First wait for any byte
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not rlist:
            return ''
        ch = sys.stdin.read(1)
        if ch != '\x1b':
            return ch
        # ESC: try to read up to 2 follow-up bytes within a slightly larger window.
        # Some terminals send the 3 bytes of arrow keys with small gaps; 50ms is safer.
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not rlist:
            return ch  # lone ESC
        ch2 = sys.stdin.read(1)
        if ch2 != '[':
            return ch + ch2
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not rlist:
            return ch + ch2
        ch3 = sys.stdin.read(1)
        return self.ARROW_MAP.get(ch3, ch + ch2 + ch3)

    def restore(self):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.settings)


class KeyboardServoNode(Node):
    def __init__(self):
        super().__init__('keyboard_servo_node')

        # Publishers
        self.pose_pub = self.create_publisher(Float64MultiArray, '/indy/teleop_pose', 10)
        self.joint_pub = self.create_publisher(Float64MultiArray, '/indy/teleop_joint', 10)

        # Subscribers
        self.create_subscription(Float64MultiArray, '/indy/ee_pose', self._ee_pose_cb, 10)
        from sensor_msgs.msg import JointState
        self.create_subscription(JointState, '/joint_states', self._joint_state_cb, 10)

        # Service clients
        self.indy_srv = self.create_client(IndyService, 'indy_srv')
        self.gripper_grasp = self.create_client(Trigger, '/gripper/grasp')
        self.gripper_open = self.create_client(Trigger, '/gripper/open')
        self.gripper_press = self.create_client(Trigger, '/gripper/press')
        self.gripper_release = self.create_client(Trigger, '/gripper/release')
        self.log_grasp = self.create_client(Trigger, '/data_collector/log_grasp')
        self.log_open = self.create_client(Trigger, '/data_collector/log_open')
        self.log_press = self.create_client(Trigger, '/data_collector/log_press')
        self.log_release = self.create_client(Trigger, '/data_collector/log_release')

        # State
        self.ee_pose = None         # latest Cartesian pose [x,y,z,rx,ry,rz]
        self.target_pose = None     # target to publish on /indy/teleop_pose
        self.joint_positions = None # latest joint positions in rad (from /joint_states)
        self.target_joint_deg = None  # target to publish on /indy/teleop_joint

        self.linear_step = LINEAR_STEP_MM
        self.angular_step = ANGULAR_STEP_DEG
        self.joint_step = JOINT_STEP_DEG
        self.direction = 1          # toggled by R key (used for N/M/, and 1-7)
        self.frame = 'base'         # 'base' or 'tool' (Tool frame transform not yet implemented)

        self.is_running = True
        self.keyboard = KeyboardReader()
        self._print_help()

    # -- Subscribers --
    def _ee_pose_cb(self, msg: Float64MultiArray):
        if len(msg.data) == 6:
            self.ee_pose = list(msg.data)
            if self.target_pose is None:
                self.target_pose = list(self.ee_pose)

    def _joint_state_cb(self, msg):
        # rad -> deg
        import math
        self.joint_positions = [math.degrees(p) for p in msg.position]
        if self.target_joint_deg is None and self.joint_positions:
            self.target_joint_deg = list(self.joint_positions)

    # -- Help --
    def _print_help(self):
        print('\n' + '=' * 64)
        print('  KEYBOARD SERVO (Neuromeka standard + gripper)')
        print('=' * 64)
        print('  Cartesian jog (workspace):')
        print('    UP / DOWN          -> x +/-')
        print('    LEFT / RIGHT       -> y +/-')
        print('    .  /  ;            -> z +/-')
        print('    N  /  M  /  ,      -> rx / ry / rz  (direction by [R])')
        print('  Joint jog:')
        print('    1  2  3  4  5  6  7   -> joint i  (direction by [R])')
        print('  Frame toggle:')
        print('    W -> base (global)   E -> tool')
        print('  Speed (step size):')
        print('    -, +    joint deg down/up')
        print('    9, 0    Cartesian (mm, deg) down/up')
        print('    R       jog direction toggle (+/-)')
        print('  Indy7 commands:')
        print('    H = Home    Z = Zero    S = Recover    P = Stop teleop')
        print('  Mark7 gripper:')
        print('    G = Grasp   O = Open    B = Press      V = Release')
        print('  Quit:')
        print('    Q')
        print()
        print(f'  step: linear={self.linear_step:.1f}mm '
              f'angular={self.angular_step:.1f}deg joint={self.joint_step:.1f}deg '
              f'dir={self.direction:+d} frame={self.frame}')
        print('=' * 64 + '\n')

    # -- Helpers --
    def _call_trigger(self, client, timeout=2.0):
        if not client.service_is_ready():
            self.get_logger().warn(f'Service not ready: {client.srv_name}')
            return
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)

    def _call_indy(self, code: int, timeout=10.0):
        if not self.indy_srv.service_is_ready():
            self.get_logger().warn('indy_srv not available')
            return
        req = IndyService.Request()
        req.data = code
        future = self.indy_srv.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)

    # -- Cartesian jog --
    def _step_cartesian(self, axis: int, sign: int):
        if self.target_pose is None:
            self.get_logger().warn('Waiting for /indy/ee_pose...')
            return
        step = self.linear_step if axis < 3 else self.angular_step
        delta = sign * step
        # TODO: tool frame transform when frame == 'tool'
        self.target_pose[axis] += delta
        msg = Float64MultiArray()
        msg.data = list(self.target_pose)
        self.pose_pub.publish(msg)
        labels = ['x', 'y', 'z', 'rx', 'ry', 'rz']
        unit = 'mm' if axis < 3 else 'deg'
        print(f'  {labels[axis]} {sign:+d}{step:.2f}{unit} -> {self.target_pose[axis]:.2f}')

    # -- Joint jog --
    def _step_joint(self, joint_idx: int, sign: int):
        if self.target_joint_deg is None:
            self.get_logger().warn('Waiting for /joint_states...')
            return
        if joint_idx >= len(self.target_joint_deg):
            self.get_logger().warn(f'joint{joint_idx} out of range')
            return
        self.target_joint_deg[joint_idx] += sign * self.joint_step
        msg = Float64MultiArray()
        msg.data = list(self.target_joint_deg)
        self.joint_pub.publish(msg)
        print(f'  joint{joint_idx} {sign:+d}{self.joint_step:.2f}deg -> '
              f'{self.target_joint_deg[joint_idx]:.2f}')

    # -- Main loop --
    def run(self):
        try:
            while self.is_running and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)
                key = self.keyboard.read_one()
                if not key:
                    continue

                # Cartesian translation
                if key == 'UP':
                    self._step_cartesian(0, +1)
                elif key == 'DOWN':
                    self._step_cartesian(0, -1)
                elif key == 'LEFT':
                    self._step_cartesian(1, +1)
                elif key == 'RIGHT':
                    self._step_cartesian(1, -1)
                elif key == '.':
                    self._step_cartesian(2, +1)
                elif key == ';':
                    self._step_cartesian(2, -1)
                # Cartesian rotation UVW (direction toggled by R)
                elif key == 'N' or key == 'n':
                    self._step_cartesian(3, self.direction)
                elif key == 'M' or key == 'm':
                    self._step_cartesian(4, self.direction)
                elif key == ',':
                    self._step_cartesian(5, self.direction)
                # Joint jog (direction toggled by R)
                elif key in '1234567':
                    j = int(key) - 1
                    self._step_joint(j, self.direction)
                # Frame toggle
                elif key == 'W' or key == 'w':
                    self.frame = 'base'
                    print('  frame -> BASE (global)')
                elif key == 'E' or key == 'e':
                    self.frame = 'tool'
                    print('  frame -> TOOL (note: tool transform not yet applied)')
                # Direction toggle
                elif key == 'R' or key == 'r':
                    self.direction *= -1
                    print(f'  direction -> {self.direction:+d}')
                # Joint speed
                elif key == '-' or key == '_':
                    self.joint_step = max(0.1, self.joint_step / 1.5)
                    print(f'  joint_step -> {self.joint_step:.2f}deg')
                elif key == '+' or key == '=':
                    self.joint_step *= 1.5
                    print(f'  joint_step -> {self.joint_step:.2f}deg')
                # Cartesian speed
                elif key == '9':
                    self.linear_step = max(0.1, self.linear_step / 1.5)
                    self.angular_step = max(0.1, self.angular_step / 1.5)
                    print(f'  cart step -> linear={self.linear_step:.2f}mm '
                          f'angular={self.angular_step:.2f}deg')
                elif key == '0':
                    self.linear_step *= 1.5
                    self.angular_step *= 1.5
                    print(f'  cart step -> linear={self.linear_step:.2f}mm '
                          f'angular={self.angular_step:.2f}deg')
                # Indy7 commands
                elif key == 'H' or key == 'h':
                    print('  cmd: Move Home')
                    self._call_indy(MSG_MOVE_HOME, timeout=15.0)
                elif key == 'Z' or key == 'z':
                    print('  cmd: Move Zero')
                    self._call_indy(MSG_MOVE_ZERO, timeout=15.0)
                elif key == 'S' or key == 's':
                    print('  cmd: Recover')
                    self._call_indy(MSG_RECOVER)
                elif key == 'P' or key == 'p':
                    print('  cmd: Stop teleop')
                    self._call_indy(MSG_TELE_STOP)
                # Gripper
                elif key == 'G' or key == 'g':
                    print('  gripper: GRASP')
                    self._call_trigger(self.gripper_grasp)
                    self._call_trigger(self.log_grasp)
                elif key == 'O' or key == 'o':
                    print('  gripper: OPEN')
                    self._call_trigger(self.gripper_open)
                    self._call_trigger(self.log_open)
                elif key == 'B' or key == 'b':
                    print('  gripper: PRESS')
                    self._call_trigger(self.gripper_press)
                    self._call_trigger(self.log_press)
                elif key == 'V' or key == 'v':
                    print('  gripper: RELEASE')
                    self._call_trigger(self.gripper_release)
                    self._call_trigger(self.log_release)
                # Quit
                elif key == 'Q' or key == 'q':
                    self.is_running = False
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.keyboard.restore()


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
