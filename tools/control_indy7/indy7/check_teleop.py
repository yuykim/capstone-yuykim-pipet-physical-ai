import pygame
import time
from neuromeka import IndyDCP3, JointTeleopType, TaskTeleopType, control_msgs

ROBOT_IP = "192.168.1.10"
indy = IndyDCP3(ROBOT_IP)

print("🔍 Indy7 상세 상태 진단 시작...")

try:
    indy.start_teleop(method=JointTeleopType.RELATIVE)

    teleop_device_info = indy.get_teleop_device()  
    print(teleop_device_info)

    teleop_state = indy.get_teleop_state()  
    print(teleop_state)

except Exception as e:
    print(f"❌ 진단 중 오류 발생: {e}")
finally:
    indy.stop_teleop()
    print("🔚 진단 종료.")