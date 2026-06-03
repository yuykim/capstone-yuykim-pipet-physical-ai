import pygame
import time
from neuromeka import IndyDCP3, TaskTeleopType

### 미완성 코드

# --- 설정값 ---
ROBOT_IP = "192.168.1.10"
XY_SENSITIVITY = 5.0  # 속도를 더 낮춰서 테스트 (안정성)
Z_SENSITIVITY = 5.0
DEADZONE = 0.15

indy = IndyDCP3(ROBOT_IP)
pygame.init()
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()

print(f"🎮 {joy.get_name()} 제어 모드 준비...")

def get_robot_detailed_state():
    status = indy.get_robot_data()
    teleop = indy.get_teleop_state()
    return status, teleop

try:
    # 1. 로봇 준비
    print("🧹 에러 복구 및 서보 온...")
    indy.stop_teleop()
    indy.recover()
    time.sleep(0.5)
    indy.set_servo_all(True)
    time.sleep(1.0)

    # 2. 텔레오퍼레이션 시작
    print("🚀 텔레오퍼레이션 모드 활성화...")
    indy.start_teleop(method=TaskTeleopType.RELATIVE)
    
    # 모드 안착 대기 및 확인
    success = False
    for _ in range(10):
        _, tele = get_robot_detailed_state()
        if tele.get('mode') == 10:
            print("✅ 모드 10 진입 성공!")
            success = True
            break
        time.sleep(0.5)

    if not success:
        print("❌ 모드 10 진입 실패. Conty 화면의 에러 메시지를 확인하세요.")
        exit()

    print("🕹️ 조종 시작 (종료: Option 버튼)")

    while True:
        pygame.event.pump()

        vx = (val if abs(val := joy.get_axis(1)) > DEADZONE else 0.0) * -XY_SENSITIVITY
        vy = (val if abs(val := joy.get_axis(0)) > DEADZONE else 0.0) * -XY_SENSITIVITY
        
        vz = 0.0
        if joy.get_button(5): vz = Z_SENSITIVITY
        elif joy.get_button(4): vz = -Z_SENSITIVITY

        # 현재 상태 상시 체크
        status, tele = get_robot_detailed_state()
        
        # 모드가 풀렸는지 감시
        if tele.get('mode') != 10:
            print(f"\n⚠️ 경고: 모드가 {tele.get('mode')}으로 변경됨! (제어 중단)")
            print(f"로봇 상태: {status}")
            # 만약 에러가 있다면 복구 시도 후 루프 탈출
            break

        # 이동 명령 (입력이 있을 때만)
        if vx != 0 or vy != 0 or vz != 0:
            try:
                # 관성을 줄이기 위해 acc_ratio를 조절
                indy.movetelel_rel(
                    tpos=[vx, vy, vz, 0, 0, 0], 
                    vel_ratio=0.2, 
                    acc_ratio=0.2
                )
                print(f"🟢 이동: X:{vx:>4.1f} Y:{vy:>4.1f} Z:{vz:>4.1f}", end='\r')
            except Exception as e:
                print(f"\n❌ 명령 전송 중 오류: {e}")
                break
        
        if joy.get_button(7): break
        time.sleep(0.05) # 20Hz

except Exception as e:
    print(f"\n❌ 루프 에러: {e}")

finally:
    indy.stop_teleop()
    pygame.quit()
    print("\n✅ 종료되었습니다.")