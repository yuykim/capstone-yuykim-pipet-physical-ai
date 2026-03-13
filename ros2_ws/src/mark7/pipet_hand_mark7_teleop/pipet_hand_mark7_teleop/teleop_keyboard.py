#!/usr/bin/env python3
"""
Mark7 커맨드 입력 노드
사용법: 공백 구분 6개 숫자 입력 후 Enter
예)  100 100 100 100 0 0
조인트 순서: Thumb(0~187)  Index  Middle  Ring  Pinky  ThAb  (0~300)
"""
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

JOINT_DISPLAY = ['Thumb', 'Index', 'Middle', 'Ring ', 'Pinky', 'ThAb ']
JOINT_LIMITS  = [(0, 187), (0, 300), (0, 300), (0, 300), (0, 300), (0, 300)]

HELP_MSG = """\
=== Mark7 Command Input ===
조인트 순서: Thumb Index Middle Ring Pinky ThAb
범위: Thumb 0~187,  나머지 0~300

입력 예) 100 100 100 100 0 0
         0 0 0 0 0 0   ← 전체 초기화
Ctrl+C  종료
===========================
"""


class CommandInput(Node):
    def __init__(self):
        super().__init__('mark7_command_input')
        self._pub = self.create_publisher(
            Float64MultiArray,
            '/mark7/forward_position_controller/commands',
            10,
        )

    def send(self, values: list[float]):
        msg = Float64MultiArray()
        msg.data = values
        self._pub.publish(msg)
        status = '  '.join(
            f'{JOINT_DISPLAY[i]}:{v:.0f}' for i, v in enumerate(values)
        )
        print(f'  → {status}')


def parse_input(line: str):
    """공백 구분 숫자 6개 파싱. 실패 시 None 반환."""
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    try:
        values = [float(p) for p in parts]
    except ValueError:
        return None
    # 범위 클램핑
    for i, (lo, hi) in enumerate(JOINT_LIMITS):
        values[i] = float(max(lo, min(hi, values[i])))
    return values


def main(args=None):
    rclpy.init(args=args)
    node = CommandInput()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    print(HELP_MSG)

    try:
        while rclpy.ok():
            try:
                line = input('> ')
            except EOFError:
                break

            values = parse_input(line)
            if values is None:
                print('  오류: 숫자 6개를 공백으로 구분해서 입력하세요')
                continue

            node.send(values)

    except KeyboardInterrupt:
        pass
    finally:
        print('\n종료')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
