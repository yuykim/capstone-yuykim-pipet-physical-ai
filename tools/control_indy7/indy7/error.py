import time
from neuromeka import IndyDCP3

# 로봇 IP 설정
ROBOT_IP = "192.168.1.10"
indy = IndyDCP3(ROBOT_IP)

def reset_robot_error():
    print("🚀 로봇 상태 복구 시퀀스를 시작합니다...")
    
    try:
        # 1. 기존에 실행 중일 수 있는 텔레오퍼레이션 중단
        indy.stop_teleop()
        time.sleep(0.5)

        # 2. 에러 상태 해제 (깜박임 멈춤 핵심 명령)
        print("1️⃣ 에러 해제 중 (Recovering)...")
        indy.recover()
        time.sleep(1.5) # 하드웨어 초기화 대기 시간

        # 3. 서보 전원 다시 켜기
        print("2️⃣ 서보 활성화 중 (Servo On)...")
        indy.set_servo_all(True)
        time.sleep(1.0)

        # 4. 결과 확인 (get_robot_data 사용)
        robot_data = indy.get_robot_data()
        is_error = robot_data.get('is_error')
        is_servo_on = robot_data.get('is_servo_on')

        print("\n--- 복구 결과 보고 ---")
        print(f"✅ 에러 상태 해제: {'성공' if not is_error else '실패 (여전히 에러)'}")
        print(f"✅ 서보 전원 상태: {'켜짐' if is_servo_on else '꺼짐'}")
        
        if not is_error and is_servo_on:
            print("\n🎉 이제 로봇을 다시 조작할 수 있습니다!")
        else:
            print("\n⚠️ 복구 실패. 로봇이 물리적으로 충돌해 있거나 비상 정지가 눌려있는지 확인하세요.")

    except Exception as e:
        print(f"\n❌ 통신 오류 발생: {e}")

if __name__ == "__main__":
    reset_robot_error()