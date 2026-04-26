import pygame
import time
from neuromeka import IndyDCP3, TaskTeleopType

# --- [설정값] ---
ROBOT_IP = "192.168.1.10" 
STEP = 0.5        # 이동 간격 (mm 또는 degree)
ROT_STEP = 0.5    # 회전은 이동보다 민감할 수 있어 따로 관리 가능

indy = IndyDCP3(ROBOT_IP)

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Indy7 Full 6-DOF Control")

def start_robot_teleop():
    print("🧹 시스템 초기화 및 6축 텔레옵 활성화...")
    indy.stop_teleop()
    indy.recover()
    time.sleep(0.5)
    indy.set_servo_all(True)
    time.sleep(1.0)
    indy.start_teleop(method=TaskTeleopType.RELATIVE)
    print("🚀 준비 완료!")
    print("  [이동] W/S(X), A/D(Y), Q/E(Z)")
    print("  [회전] U/O(RX), I/K(RY), J/L(RZ)")
    print("  [설정] [ / ] (STEP 조절), ESC(종료)")

try:
    # 초기 위치 이동
    target_pos = [0, 35, -150, 0, 25, 0]
    indy.movej(jtarget=target_pos)
    time.sleep(1.0)

    start_robot_teleop()

    clock = pygame.time.Clock()
    running = True

    dx = dy = dz = drx = dry = drz = 0.0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    STEP = max(0.1, STEP - 0.1)
                    print(f"➖ STEP 감소: {STEP:.1f}")
                elif event.key == pygame.K_RIGHTBRACKET:
                    STEP = STEP + 0.1
                    print(f"➕ STEP 증가: {STEP:.1f}")
                elif event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_SPACE: # 스페이스바: 홈 이동
                    print("🏠 홈 위치로 복귀 중...")
                    indy.stop_teleop()
                    indy.movej(jtarget=target_pos)
                    time.sleep(0.5)
                    indy.start_teleop(method=TaskTeleopType.RELATIVE)
        
        keys = pygame.key.get_pressed()
        moved = False

        # 2. 이동 매핑 (X, Y, Z)
        if keys[pygame.K_w]: dx += STEP; moved = True
        if keys[pygame.K_s]: dx += -STEP; moved = True
        if keys[pygame.K_a]: dy += STEP; moved = True
        if keys[pygame.K_d]: dy += -STEP; moved = True
        if keys[pygame.K_q]: dz += STEP; moved = True
        if keys[pygame.K_e]: dz += -STEP; moved = True

        # 3. 회전 매핑 (RX, RY, RZ) - 회전은 ROT_STEP 사용 가능
        if keys[pygame.K_u]: drx += STEP; moved = True
        if keys[pygame.K_o]: drx += -STEP; moved = True
        if keys[pygame.K_i]: dry += STEP; moved = True
        if keys[pygame.K_k]: dry += -STEP; moved = True
        if keys[pygame.K_j]: drz += STEP; moved = True
        if keys[pygame.K_l]: drz += -STEP; moved = True

        # 4. 명령 전송
        if moved:
            try:
                tpos = [dx, dy, dz, drx, dry, drz]
                # 연속 제어에서는 vel/acc를 낮게 잡아야 부드럽습니다.
                indy.movetelel_rel(tpos=tpos, vel_ratio=0.1, acc_ratio=0.1)
            except Exception as e:
                print(f"❌ 이동 에러: {e}")

        # 30Hz: 초당 30번 명령 (부드러운 움직임의 핵심)
        clock.tick(30) 

except Exception as e:
    print(f"\n❌ 루프 에러: {e}")

finally:
    indy.stop_teleop()
    pygame.quit()
    print("\n✅ 안전하게 종료되었습니다.")