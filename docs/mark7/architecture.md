# Mark7 모듈 설계 문서

**최종 수정:** 2026-03-05
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
| 그립 프리셋 | grasp / open / press 서비스 호출 하나로 실행 |
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
- **현황**: Tx 정상 동작 확인 / Rx 수신 미확인 (동글 Arduino 코드 미확보, 보류)

---

## 3. 통신 프로토콜

### PC → Hand (Tx, 15 bytes)

| 바이트 | 항목 | 값 |
|--------|------|----|
| B0-B1 | 헤더 | `0xAA 0x55` |
| B2-B7 | 손가락 선택 (Thumb~Thumb Ab) | 0 or 1 |
| B8-B9 | 속도 (RPM/10) | 300~3000 (0=무시) |
| B10-B11 | 전류 한계 (mA) | 600~1200 (0=무시) |
| B12-B13 | 목표 위치 | -50~400 (0=변경 없음) |
| B14 | 방향 | 0:Idle, 1:Forward, 2:Reverse, 3:Reset |

### Hand → PC (Rx, 19 bytes)

손가락 6개 × (Position÷4, Current÷10 mA, Temperature°C) + XOR Checksum

### 주의사항

- Position=0 은 "목표 위치 변경 없음"을 의미 (0으로 이동이 아님)
- Hall effect 센서 슬립이 있으므로 사용 중 완전 개방 시 Reset(Direction=3) 권장
- RF 통신 특성상 신호 손실 가능 → 중요한 명령은 2~3회 반복 전송 권장

---

## 4. 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│              외부 인터페이스 (오케스트레이터/테스트 도구)          │
│                                                              │
│  pipet_system_teleop        pipet_hand_mark7_teleop          │
│  (통합 운용 - 서비스 호출)   (단독 테스트 - 직접 관절 제어)        │
│                                                              │
│  pipet_hand_mark7_gazebo                                     │
│  (Gazebo 시뮬 → 실제 미러링)                                   │
└──────┬───────────────────────────────┬───────────────────────┘
       │ /gripper/grasp|open|press     │ /forward_position_controller/commands
       │ (서비스)                       │ (토픽, Float64MultiArray)
┌──────▼───────────────────────────────▼───────────────────────┐
│                  pipet_hand_mark7_driver                      │
│                                                              │
│  ┌─────────────────────────┐  ┌──────────────────────────┐   │
│  │     GripPresetNode      │  │  ForwardCommandController │   │
│  │  grasp / open / press   │  │  (ros2_control 기성 컨트롤러)│  │
│  │  서비스 → 관절 포즈 변환  │  │  관절 각도 직접 명령 수신   │  │
│  └────────────┬────────────┘  └────────────┬─────────────┘   │
│               │ /forward_position_controller/commands         │
│               └────────────────┬────────────┘                │
│  ┌─────────────────────────────▼────────────────────────┐    │
│  │            Hardware Interface (ros2_control)          │    │
│  │   use_mock_hardware=false → 실제 Dongle 시리얼 통신   │    │
│  │   use_mock_hardware=true  → 내부 시뮬레이션           │    │
│  │   read()  : Rx → /gripper/status 퍼블리시            │    │
│  │   write() : Tx → 15바이트 명령 패킷 전송             │    │
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
| 토픽 (발행) | `/gripper/status` | (자체 정의) | Hardware Interface | 그리퍼 현재 상태, 20Hz |
| 서비스 | `/gripper/grasp` | std_srvs/Trigger | GripPresetNode | 파이펫 잡기 |
| 서비스 | `/gripper/open` | std_srvs/Trigger | GripPresetNode | 손 펴기 |
| 서비스 | `/gripper/press` | std_srvs/Trigger | GripPresetNode | 파이펫 누르기 |
| 토픽 (구독) | `/forward_position_controller/commands` | std_msgs/Float64MultiArray | ForwardCommandController | 관절 각도 직접 명령 |

---

## 5. 패키지 구성

```
mark7/
├── pipet_hand_mark7_description/     # URDF, 메시, RViz 설정
├── pipet_hand_mark7_driver/          # 핵심 드라이버 패키지
│   ├── Hardware Interface            # ros2_control 하드웨어 인터페이스
│   ├── 통신 프로토콜 구현             # 15/19바이트 패킷 인코딩/디코딩
│   ├── GripPresetNode                # grasp/open/press 서비스 제공
│   ├── 안전 모니터링 노드            # 온도/전류 감시
│   └── 통합 런치 파일               # real/mock 모드 선택
├── pipet_hand_mark7_teleop/          # Mark7 단독 테스트용
│   └── Keyboard Teleop 노드          # 개별 손가락 키보드 제어
│                                     # → /forward_position_controller/commands 직접 발행
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
| 1 | `pipet_hand_mark7_driver` | 통신 프로토콜 (Tx/Rx 패킷), Serial 레이어 | ✅ 완료 |
| 2 | `pipet_hand_mark7_driver` | ros2_control Hardware Interface (real + mock) | ✅ 완료 |
| 3 | `pipet_hand_mark7_driver` | GripPresetNode (grasp/open/press 서비스) | 🔲 미착수 |
| 4 | `pipet_hand_mark7_driver` | 캘리브레이션 (URDF rad ↔ position count 매핑) | 🔲 보류 (실측 필요) |
| 5 | `pipet_hand_mark7_driver` | 안전 모니터링 노드 (온도/전류 감시) | 🔲 미착수 |
| 6 | `pipet_hand_mark7_driver` | 런치/컨트롤러 설정 | ✅ 완료 |
| 7 | `pipet_hand_mark7_teleop` | Keyboard Teleop 노드 | 🟡 구현 완료 (Thumb flex 이슈 미해결) |
| 8 | `pipet_hand_mark7_gazebo` | Gazebo 시뮬 환경 구성, 마우스 조작 | 🔲 미착수 |
| 9 | `pipet_hand_mark7_gazebo` | Mirror Bridge 노드 (Gazebo → 실제) | 🔲 미착수 |
| - | - | 실제 하드웨어 Rx 통신 디버깅 | 🔴 보류 (동글 코드 미확보) |

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
