from neuromeka import IndyDCP3
import time

indy = IndyDCP3(robot_ip="192.168.1.10")

def shutdown_robot():
    try:
        indy.move_home()

        print("🛑 로봇 정지 및 서보 해제 중...")
        # 1. 모든 모션 정지
        indy.stop_motion(2) # Category 2 Stop
        time.sleep(1)
        
        # 2. 모든 서보 비활성화 (브레이크 체결)
        # 실행 시 로봇 관절에서 "딸깍" 소리가 나며 고정됩니다.
        indy.set_servo_all(False) 
        
        print("✅ 소프트웨어 종료 완료. 이제 컨트롤 박스 전원을 끄셔도 됩니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def come_back_home():
    try:
        # 2. 로봇 활성화
        print("🔧 로봇 활성화 중...")
        indy.recover()
        time.sleep(1)
        indy.set_servo_all(True)
        
        time.sleep(6)

        indy.move_home()
        
        # 복귀 완료 대기
        time.sleep(6)
        print("home position으로 이동 완료")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    come_back_home()
    shutdown_robot()