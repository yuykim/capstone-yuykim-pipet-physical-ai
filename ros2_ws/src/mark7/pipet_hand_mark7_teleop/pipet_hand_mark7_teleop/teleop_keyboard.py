#!/usr/bin/env python3
import sys
import termios
import tty
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


# 조인트 순서: mark7_controllers.yaml의 forward_position_controller와 동일
JOINT_NAMES = [
    'thumb_bottom_middle_rev', # 0  B2 Thumb Flex (실제 굽힘)
    'base_index',              # 1  B3 Index
    'base_middle',             # 2  B4 Middle
    'base_ringer',             # 3  B5 Ring
    'base_pinky',              # 4  B6 Little
    'base_thumb',              # 5  B7 Thumb Ab (실제 외전)
]

JOINT_DISPLAY = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'ThAb']

# steps 범위: 0~300 = 0~80° (가정), thumb_flex는 0~187 ≈ 0~50°
# 실제 하드웨어 연결 후 캘리브레이션 필요
JOINT_LIMITS = [
    (0, 187), # thumb_bottom_middle_rev (Thumb Flex, ~50°)
    (0, 300), # base_index
    (0, 300), # base_middle
    (0, 300), # base_ringer
    (0, 300), # base_pinky
    (0, 300), # base_thumb (Thumb Ab)
]

# steps는 항상 양수 증가
FLEX_DIR = [+1, +1, +1, +1, +1, +1]

# 키 → 조인트 인덱스
# q/a = Thumb Flex (thumb_bottom_middle_rev, index 0)
# y/h = Thumb Ab   (base_thumb, index 5)
FLEX_KEYS   = {'q': 0, 'w': 1, 'e': 2, 'r': 3, 't': 4, 'y': 5}
EXTEND_KEYS = {'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 4, 'h': 5}

# 속도 단계 (steps/키입력)
SPEED_LEVELS = [5, 10, 20, 30, 50]
DEFAULT_SPEED_IDX = 1  # 10 steps

HELP_MSG = """
=== Mark7 Keyboard Teleop ===
굽히기 (Flex):    q  w  e  r  t  y
펼치기 (Extend):  a  s  d  f  g  h
                  |  |  |  |  |  |
                 Th  In  Mi  Ri  Pi ThAb

속도 조절:
  z : 느리게  x : 빠르게
  단계: 5 / 10 / 20 / 30 / 50 steps

기타:
  0      : 전체 초기화
  Ctrl+C : 종료
==============================
"""


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('mark7_keyboard_teleop')
        self._pub = self.create_publisher(
            Float64MultiArray,
            '/mark7/forward_position_controller/commands',
            10,
        )
        self._current_pos = [0.0] * 6
        self.speed_idx = DEFAULT_SPEED_IDX

    @property
    def step(self):
        return SPEED_LEVELS[self.speed_idx]

    def move(self, joint_idx: int, delta: float):
        lo, hi = JOINT_LIMITS[joint_idx]
        target = float(max(lo, min(hi, round(self._current_pos[joint_idx] + delta))))
        self._current_pos[joint_idx] = target
        msg = Float64MultiArray()
        msg.data = list(self._current_pos)
        self._pub.publish(msg)

    def reset(self):
        self._current_pos = [0.0] * 6
        msg = Float64MultiArray()
        msg.data = list(self._current_pos)
        self._pub.publish(msg)

    def print_status(self):
        pos_str = '  '.join(
            f'{JOINT_DISPLAY[i]}:{p:+.0f}' for i, p in enumerate(self._current_pos)
        )
        print(f'\r[step={self.step}]  {pos_str}    ', end='', flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    settings = termios.tcgetattr(sys.stdin)

    print(HELP_MSG)
    node.print_status()

    try:
        while rclpy.ok():
            key = get_key(settings)

            if key == '\x03':  # Ctrl+C
                break
            elif key in FLEX_KEYS:
                idx = FLEX_KEYS[key]
                node.move(idx, +node.step)
            elif key in EXTEND_KEYS:
                idx = EXTEND_KEYS[key]
                node.move(idx, -node.step)
            elif key == 'z':
                node.speed_idx = max(0, node.speed_idx - 1)
                print(f'\n속도: {node.step} steps')
            elif key == 'x':
                node.speed_idx = min(len(SPEED_LEVELS) - 1, node.speed_idx + 1)
                print(f'\n속도: {node.step} steps')
            elif key == '0':
                node.reset()
                print('\n전체 초기화')

            node.print_status()

    except Exception as e:
        print(f'\nError: {e}')
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        print('\nTeleop 종료')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
