# Mark7 모듈 설계 문서

**최종 수정:** 2026-03-06
**참조:** [전체 시스템 설계](architecture.md)

---

## 1. 개요

**Mand.ro Mark7**는 6 DoF 와이어 구동 방식의 로봇 핸드이다.
이 문서는 Mark7를 ROS2 Humble 환경에서 제어하기 위한 `pipet_hand_mark7_driver` 패키지 및 관련 패키지의 설계를 기술한다.

### 주요 기능

| 기능 | 설명 |
|------|------|
| 실제 로봇 제어 | USB RF 동글을 통해 실제 Mark7 하드웨어 제어 |
| 가상 모드 | 하드웨어 없이 소프트웨어만으로 동작 확인 |
| Gazebo 시뮬레이션 | 마우스로 가상 Mark7 조작 → 실제 로봇 미러링 |
| 키보드 조작 | 터미널에서 키보드로 손가락 직접 제어 (단독 테스트용) |
| 그립 프리셋 | grasp / open / press / release 서비스 호출 하나로 실행 |
| 안전 모니터링 | 온도/전류 이상 감지 및 경고 |

---

## 2. 하드웨어 구성

```
PC (ROS2 Humble)
  └── Dongle (USB, /dev/ttyACM0, Arduino Pro Micro)
        ├── Tx: 2.4GHz RF ───────────────► Mark7 Hand (6 DoF)
        └── Rx: 2.4GHz RF ◄────────────── Mark7 Hand (6 DoF)
```

- **통신 방식**: 2.4GHz RF 무선 통신
- **인터페이스**: USB Serial 단일 포트 `/dev/ttyACM0` (Tx/Rx 공용, 115200 bps, 8-N-1)
- **DoF 구성**: Thumb Flexion, Index, Middle, Ring, Little, Thumb Ab/Adduction
- **현황**: 통신 프로토콜 공식 문서 확보 (2026-03-05, Mand.ro)
- **Rx 주기**: ~0.5Hz (하드웨어 특성, 1.5~2초 간격으로 수신)
- **Tx 제약**: 연속 전송 시 하드웨어 처리 불가 → 명령 변경 시 1회만 전송

---

## 3. 통신 프로토콜

### PC → Hand (Tx, 11 bytes)

| 바이트 | 항목 | 값 / 계산식 |
|--------|------|------------|
| B0 | Hand 선택 | 0xFD=Left, 0xFE=Right, 0xFF=Both |
| B1 | Finger 비트마스크 | 1=Thumb, 2=Index, 4=Middle, 8=Ring, 16=Little, 32=ThumbAbd |
| B2 | Speed | 0=skip, 실제 RPM = Data × 200 (범위 30~150) |
| B3 | Current Limit | 0=skip, 실제 mA = 600 + Data × 3 |
| B4 | Thumb Flexion 목표 위치 | 0=skip, 실제 steps = -21 + Data × 2 |
| B5 | Index Flexion 목표 위치 | 동일 |
| B6 | Middle Flexion 목표 위치 | 동일 |
| B7 | Ring Flexion 목표 위치 | 동일 |
| B8 | Little Flexion 목표 위치 | 동일 |
| B9 | Thumb Abduction 목표 위치 | 동일 |
| B10 | Direction | 0=Idle, 1=Forward, 2=Reverse, 3=Reset |

헤더 및 XOR 체크섬 **없음**.

### Hand → PC (Rx, 가변 길이 텍스트)

쉼표(`,`) 구분 plain text 문자열, 줄바꿈(`\n`) 종료.

```
L|R, pos,cur,temp, pos,cur,temp, pos,cur,temp, pos,cur,temp, pos,cur,temp, pos,cur,temp
```

필드 순서: `Hand(L/R)`, `[Thumb Flex] Position, Current, Temperature`, `[Index]`, `[Middle]`, `[Ring]`, `[Little]`, `[Thumb Abd]`

예시: `R,139,1140,35, 171,1140,34, 203,1140,34, 235,1140,34, 267,1140,34, 299,1140,34`

### 주의사항

- **Position=0 (B4~B9)** 은 "목표 위치 변경 없음"을 의미 (0으로 이동이 아님)
- Direction=**Forward** 하나로 양방향 이동 가능 — 목표값이 현재보다 작으면 자동 역방향
- Hall effect 센서 슬립 존재 → 완전 개방 시마다 **Reset(Direction=3)** 권장
- RF 통신 특성상 신호 손실 가능 → 중요한 명령은 2~3회 반복 전송 권장

---

## 4. 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│              외부 인터페이스 (오케스트레이터/테스트 도구)          │
│                                                              │
│  pipet_system_teleop        pipet_hand_mark7_teleop          │
│  (통합 운용 - 서비스 호출)   ├ Command Input (단독 테스트)        │
│                             └ GripPresetNode (프리셋 서비스)     │
│  pipet_hand_mark7_gazebo                                     │
│  (Gazebo 시뮬 → 실제 미러링)                                   │
└──────┬───────────────────────────────┬───────────────────────┘
       │ /gripper/grasp|open|press|release │ /forward_position_controller/commands
       │ (서비스→GripPresetNode→토픽)      │ (토픽, Float64MultiArray)
┌──────▼───────────────────────────────▼───────────────────────┐
│                  pipet_hand_mark7_driver                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ForwardCommandController (ros2_control 기성 컨트롤러)  │    │
│  │  관절 각도 직접 명령 수신                               │    │
│  └────────────────────────┬───────────────────────────┘    │
│                           │                                │
│  ┌─────────────────────────────▼────────────────────────┐    │
│  │            Hardware Interface (ros2_control)          │    │
│  │   use_mock_hardware=false → 실제 Dongle 시리얼 통신   │    │
│  │   use_mock_hardware=true  → 내부 시뮬레이션           │    │
│  │   read()  : Rx 수신 시에만 /gripper/status 퍼블리시 (~0.5Hz)│
│  │   write() : command 변경 시에만 Tx 1회 전송          │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │            Safety Monitor Node                        │    │
│  │   온도/전류 이상 감지, 경고 퍼블리시, 긴급 정지        │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
            │ Serial (115200 bps, /dev/ttyACM0)
    [Dongle] ──── 2.4GHz RF Tx ───► [Mark7 Hand]
    [Dongle] ◄─── 2.4GHz RF Rx ─── [Mark7 Hand]
```

### 인터페이스 요약

| 종류 | 이름 | 타입 | 제공 주체 | 설명 |
|------|------|------|-----------|------|
| 토픽 (발행) | `/gripper/status` | (자체 정의) | Hardware Interface | 그리퍼 현재 상태, Rx 수신 시에만 (~0.5Hz) |
| 서비스 | `/gripper/grasp` | std_srvs/Trigger | GripPresetNode (teleop 패키지) | 피펫 잡기 |
| 서비스 | `/gripper/open` | std_srvs/Trigger | GripPresetNode (teleop 패키지) | 손 펴기 |
| 서비스 | `/gripper/press` | std_srvs/Trigger | GripPresetNode (teleop 패키지) | 피펫 누르기 |
| 서비스 | `/gripper/release` | std_srvs/Trigger | GripPresetNode (teleop 패키지) | 엄지 펴기 (잡은 상태 유지) |
| 토픽 (구독) | `/forward_position_controller/commands` | std_msgs/Float64MultiArray | ForwardCommandController | 관절 각도 직접 명령 |

---

## 5. 패키지 구성

```
mark7/
├── pipet_hand_mark7_description/     # URDF, 메시, RViz 설정
├── pipet_hand_mark7_driver/          # 핵심 드라이버 패키지
│   ├── Hardware Interface            # ros2_control 하드웨어 인터페이스
│   ├── 통신 프로토콜 구현             # 11바이트 Tx / 텍스트 CSV Rx 파싱
│   ├── GripPresetNode                # grasp/open/press 서비스 제공
│   ├── 안전 모니터링 노드            # 온도/전류 감시
│   └── 통합 런치 파일               # real/mock 모드 선택
├── pipet_hand_mark7_teleop/          # Mark7 단독 테스트 + 프리셋 서비스
│   ├── Keyboard Teleop 노드          # 개별 손가락 키보드 제어
│   │                                 # → /forward_position_controller/commands 직접 발행
│   └── GripPresetNode                # grasp/open/press/release 서비스 제공
│                                     # → /forward_position_controller/commands 프리셋 발행
└── pipet_hand_mark7_gazebo/          # Gazebo 시뮬레이션
    ├── Gazebo 환경 설정
    └── Mirror Bridge 노드            # Gazebo joint_states → 실제 로봇
```

---

## 6. 가상/실제 모드 전환

하드웨어 연결 없이도 소프트웨어를 완전히 테스트할 수 있도록 단일 파라미터로 모드를 전환한다.

```bash
# 실제 로봇 모드
ros2 launch pipet_hand_mark7_driver mark7.launch.py use_mock_hardware:=false port:=/dev/ttyACM0

# 가상 모드 (하드웨어 불필요)
ros2 launch pipet_hand_mark7_driver mark7.launch.py use_mock_hardware:=true

# 가상 모드 + RViz 시각화
ros2 launch pipet_hand_mark7_driver mark7.launch.py use_mock_hardware:=true use_rviz:=true
```

| 동작 | 실제 모드 | 가상 모드 |
|------|-----------|-----------|
| `on_activate()` | 시리얼 포트 열기 | 통과 |
| `read()` | Rx Dongle 수신 | command값을 state로 복사 |
| `write()` | Tx Dongle 송신 | 로그 출력 후 통과 |

---

## 7. 작업 단계

| 단계 | 패키지 | 내용 | 상태 |
|------|--------|------|------|
| 1 | `pipet_hand_mark7_driver` | 통신 프로토콜 (11바이트 Tx / 텍스트 CSV Rx), Serial 레이어 | ✅ 완료 |
| 2 | `pipet_hand_mark7_driver` | ros2_control Hardware Interface (real + mock) | ✅ 완료 |
| 3 | `pipet_hand_mark7_teleop` | GripPresetNode (grasp/open/press/release 서비스) | ✅ 완료 |
| 4 | `pipet_hand_mark7_driver` | 캘리브레이션 (URDF rad ↔ position count 매핑) | 🔲 보류 (실측 필요) |
| 5 | `pipet_hand_mark7_driver` | 안전 모니터링 노드 (온도/전류 감시) | 🔲 미착수 |
| 6 | `pipet_hand_mark7_driver` | 런치/컨트롤러 설정 | ✅ 완료 |
| 7 | `pipet_hand_mark7_teleop` | Command Input 노드 (절대값 입력) | ✅ 완료 |
| 8 | `pipet_hand_mark7_gazebo` | Gazebo 시뮬 환경 구성, 마우스 조작 | 🔲 미착수 |
| 9 | `pipet_hand_mark7_gazebo` | Mirror Bridge 노드 (Gazebo → 실제) | 🔲 미착수 |
| - | - | 실제 하드웨어 통합 테스트 | 🔲 미착수 |

### 그립 프리셋 값

| 프리셋 | Thumb | Index | Middle | Ring | Pinky | ThumbAb | 용도 |
|--------|-------|-------|--------|------|-------|---------|------|
| grasp | 0 | 0 | 350 | 350 | 350 | 0 | 피펫 잡기 (중지~소지 닫힘) |
| open | 0 | 0 | 0 | 0 | 0 | 0 | 손 펴기 (전체 개방) |
| press | 150 | 0 | 350 | 350 | 350 | 0 | 피펫 버튼 누르기 (잡은 상태에서 엄지 누름) |
| release | 0 | 0 | 350 | 350 | 350 | 0 | 엄지 펴기 (잡은 상태 유지) |

설정 파일: `pipet_hand_mark7_driver/config/grip_presets.yaml`

---

## 8. 의존성

| 패키지 | 용도 |
|--------|------|
| `ros2_control` | 하드웨어 인터페이스 프레임워크 |
| `ros2_controllers` | ForwardCommandController 등 기성 컨트롤러 |
| `controller_manager` | 컨트롤러 생명주기 관리 |
| `gazebo_ros` | Gazebo-ROS2 브릿지 |
| `gazebo_ros2_control` | Gazebo ros2_control 플러그인 |
| `robot_state_publisher` | URDF → TF 퍼블리시 |
