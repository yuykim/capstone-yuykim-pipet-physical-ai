# Pipet Physical AI

Indy7 로봇팔과 Mand.ro Mark7 로봇손을 이용해 파이펫(pipette)을 조작하는 Physical AI 프로젝트.

## 시스템 구성

| 항목 | 내용 |
|------|------|
| 로봇팔 | Neuromeka Indy7 |
| 로봇손 | Mand.ro Mark7 |
| 카메라 | Intel RealSense D435 |
| OS / ROS | Ubuntu 22.04 / ROS2 Humble |

---

## 빠른 시작

### 1. 워크스페이스 빌드

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

### 2. Mark7 단독 실행 (하드웨어 연결 시)

```bash
# 시리얼 포트 권한 부여 (최초 1회)
sudo chmod 777 /dev/ttyACM0

# 드라이버 런치
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py port:=/dev/ttyACM0

# 별도 터미널: 명령 입력
ros2 run pipet_hand_mark7_teleop teleop_keyboard
```

### 3. Mark7 가상 모드 (하드웨어 없이)

```bash
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py use_mock_hardware:=true use_rviz:=true
```

---

## Mark7 명령 입력 방법

`teleop_keyboard` 실행 후 공백으로 구분한 6개 숫자를 입력하고 Enter:

```
> 100 100 100 100 0 0
  → Thumb:100  Index:100  Middle:100  Ring :100  Pinky:0  ThAb :0
```

조인트 순서: `Thumb Flex | Index | Middle | Ring | Pinky | Thumb Ab`

| 조인트 | 범위 (steps) | 설명 |
|--------|-------------|------|
| Thumb Flex | 0 ~ 187 | 엄지 굽힘 |
| Index | 0 ~ 300 | 검지 굽힘 |
| Middle | 0 ~ 300 | 중지 굽힘 |
| Ring | 0 ~ 300 | 약지 굽힘 |
| Pinky | 0 ~ 300 | 소지 굽힘 |
| Thumb Ab | 0 ~ 300 | 엄지 외전 |

전체 초기화: `0 0 0 0 0 0`

> **주의**: 명령을 보내면 하드웨어가 해당 위치로 이동합니다. 관절이 물리적 한계에 걸리지 않도록 주의하세요.

---

## 상태 모니터링

```bash
# 관절 현재 위치 (Rx 수신 시 ~0.5Hz 업데이트)
ros2 topic echo /mark7/joint_states --once

# 그리퍼 전체 상태 (position / current / temperature)
ros2 topic echo /gripper/status --once

# 직접 명령 전송 (teleop 없이)
ros2 topic pub --once /mark7/forward_position_controller/commands \
  std_msgs/msg/Float64MultiArray "{data: [0.0, 150.0, 150.0, 150.0, 150.0, 0.0]}"
```

---

## 통신 특성

| 항목 | 값 |
|------|-----|
| 인터페이스 | USB Serial `/dev/ttyACM0`, 115200 bps |
| Tx (PC → Hand) | 11바이트 바이너리, 명령 변경 시 1회 전송 |
| Rx (Hand → PC) | 가변 텍스트 CSV, ~0.5Hz (1.5~2초 간격) |
| 연속 Tx 금지 | 하드웨어가 연속 수신 시 처리 불가 |

---

## 디렉터리 구조

```
ros2_ws/src/
  mark7/
    pipet_hand_mark7_msgs/         # 커스텀 메시지 (GripperStatus, FingerState)
    pipet_hand_mark7_description/  # URDF, 메시
    pipet_hand_mark7_driver/       # ros2_control 드라이버 (시리얼 통신)
    pipet_hand_mark7_teleop/       # 단독 테스트용 명령 입력 노드
  indy7_ros2/                      # Indy7 드라이버 (서브모듈)
docs/
  architecture.md                  # 전체 시스템 설계
  interface_spec.md                # ROS2 인터페이스 명세
  mark7/architecture.md            # Mark7 모듈 상세 설계
```

---

## 문서

| 문서 | 설명 |
|------|------|
| [docs/architecture.md](docs/architecture.md) | 전체 시스템 설계 및 데이터 흐름 |
| [docs/interface_spec.md](docs/interface_spec.md) | ROS2 토픽/서비스 인터페이스 명세 |
| [docs/mark7/architecture.md](docs/mark7/architecture.md) | Mark7 모듈 상세 설계 및 통신 프로토콜 |
