import pygame
import os

# 1. Pygame 및 조이스틱 초기화
pygame.init()
pygame.joystick.init()

def monitor_controller():
    if pygame.joystick.get_count() == 0:
        print("❌ 연결된 컨트롤러가 없습니다. 연결을 확인해주세요.")
        return

    # 첫 번째 컨트롤러 선택
    joy = pygame.joystick.Joystick(0)
    joy.init()

    print(f"✅ 컨트롤러 연결됨: {joy.get_name()}")
    print("--- 테스트를 시작합니다. (종료하려면 Ctrl+C) ---")

    try:
        while True:
            # 화면 지우기 (윈도우: cls, 맥/리눅스: clear)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 이벤트 펌핑 (입력 값 업데이트)
            pygame.event.pump()

            print(f"[ 컨트롤러: {joy.get_name()} ]")
            print("-" * 40)

            # 2. 아날로그 스틱 및 트리거 (Axes)
            # 보통 0:LX, 1:LY, 2:LT, 3:RX, 4:RY, 5:RT
            num_axes = joy.get_numaxes()
            print(f"📍 스틱 및 트리거 (Axes: {num_axes}개):")
            for i in range(num_axes):
                axis_val = joy.get_axis(i)
                # 소수점 둘째자리까지 출력
                print(f"  Axis {i}: {axis_val:6.2f}", end=" | " if (i+1)%2 != 0 else "\n")

            print("\n" + "-" * 40)

            # 3. 버튼 상태 (Buttons)
            # 0:A, 1:B, 2:X, 3:Y, 4:LB, 5:RB ...
            num_buttons = joy.get_numbuttons()
            print(f"🔘 버튼 상태 (Buttons: {num_buttons}개):")
            active_buttons = [i for i in range(num_buttons) if joy.get_button(i)]
            print(f"  눌린 버튼 번호: {active_buttons}")

            print("-" * 40)

            # 4. 방향키 (Hats - D-pad)
            num_hats = joy.get_numhats()
            for i in range(num_hats):
                hat_val = joy.get_hat(i)
                print(f"🎮 D-pad(Hat) {i}: {hat_val}")

            print("\n[안내] 스틱을 끝까지 밀었을 때 1.0 혹은 -1.0이 나오는지 확인하세요.")
            
            # 너무 빠른 갱신 방지 (0.1초 간격)
            pygame.time.wait(100)

    except KeyboardInterrupt:
        print("\n👋 테스트를 종료합니다.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    monitor_controller()