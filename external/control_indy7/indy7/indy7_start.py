from neuromeka import IndyDCP3
import time

# 로봇 연결
indy = IndyDCP3(robot_ip="192.168.1.10")

try:
    # 1. 에러 상태 복구 (문서에 있는 recover 함수)
    print("로봇 상태 복구 시도...")
    # indy.recover() 
    time.sleep(1)

    # 2. 모든 관절 서보 활성화 (문서 6페이지 '유틸리티 함수' 섹션 참고)
    # 실행 시 로봇에서 "딸깍" 소리가 나야 합니다.
    print("서보 활성화 중 (set_servo_all)...")
    indy.set_servo_all(True) 
    time.sleep(2)

    # 3. 상태 확인
    data = indy.get_robot_data()
    print(f"현재 로봇 상태(op_state): {data['op_state']}")
    
    # op_state가 5(IDLE)이거나 6(MOVING)이면 성공입니다.
    if data['op_state'] >= 5:
        print("✅ 로봇이 성공적으로 활성화되었습니다!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")