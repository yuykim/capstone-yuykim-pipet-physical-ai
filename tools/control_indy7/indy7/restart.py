import time
from neuromeka import IndyDCP3, TaskTeleopType

# 설정
ROBOT_IP = "192.168.1.10"
indy = IndyDCP3(ROBOT_IP)

def full_system_restart():
    print("🔄 로봇 제어 시스템 재시작을 시작합니다...")

    try:
        # 1. 기존 모든 동작 중지 및 초기화
        print("🛑 1단계: 모든 제어 모드 중단...")
        indy.stop_teleop()
        indy.stop_motion()
        time.sleep(1.0)

        # 2. 서보 전원 차단 (안전을 위해 잠시 전력 차단)
        print("🔌 2단계: 서보 전원 일시 차단...")
        indy.set_servo_all(False)
        time.sleep(1.5)

        # 3. 에러 복구 (깜박임 해결)
        print("🛠️ 3단계: 에러 상태 복구(Recover)...")
        indy.recover()
        time.sleep(1.5)

        # 4. 서보 전원 다시 켜기
        print("⚡ 4단계: 서보 전원 공급 (Servo ON)...")
        indy.set_servo_all(True)
        time.sleep(1.5)

        # 5. 상태 확인 (get_robot_data 사용)
        data = indy.get_robot_data()
        if not data.get('is_error') and data.get('is_servo_on'):
            print("✅ 5단계: 로봇 하드웨어 준비 완료.")
            
            # 6. 조이스틱 제어 모드 진입
            print("🚀 6단계: 텔레오퍼레이션(Mode 10) 진입...")
            indy.start_teleop(method=TaskTeleopType.RELATIVE)
            time.sleep(0.5)
            print("\n✨ 모든 재시작 프로세스가 완료되었습니다! 이제 조이스틱을 사용하세요.")
        else:
            print("\n❌ 재시작 실패: 로봇 상태를 확인하세요 (비상정지 버튼 등).")

    except Exception as e:
        print(f"\n❌ 재시작 중 오류 발생: {e}")

if __name__ == "__main__":
    full_system_restart()