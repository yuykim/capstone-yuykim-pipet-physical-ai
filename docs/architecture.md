# 설계 문서

**최종 수정:** 2026-03-05

---

## 1. 목표 / 범위

### 목표
Indy7 로봇팔 + Mand.ro Mark7 로봇손으로 Physical AI를 활용하여 파이펫(pipette)을 조작한다.

### 범위

**1단계 (핵심 목표)**
- 거치대에서 파이펫 잡기

**2단계 (확장 목표)**
- 파이펫을 들고 이동
- 흡입/배출 동작

**프로젝트 범위에 포함**
- Mark7 ROS2 지원 라이브러리 개발
- Indy7 + Mark7 통합
- Physical AI 학습 및 배포

---

## 2. 시스템 개요

### 전체 흐름

```
[하드웨어]
Indy7 (로봇팔) + Mark7 (로봇손) + RealSense D435 (카메라)
        ↓
[ROS2 통합 환경]
직접 교시(Indy7) + 키보드 조작(Mark7) + 카메라 스트림
        ↓
[데이터 수집]
관절값 + RGB/Depth 이미지 + 그리퍼 액션 → NPZ 파일
        ↓
[AI 학습]
LeRobot / Isaac Lab+Robomimic / Unity ML-Agents
        ↓
[배포]
RealSense로 파이펫 인식 → 학습된 모델 → Indy7 + Mark7 자율 동작
```

### ROS2 시스템 구조

계층형 아키텍처: 모듈 레이어는 각 장치의 기능을 서비스/토픽으로 노출하고, 오케스트레이터 레이어가 이를 조합하여 시스템 수준의 동작을 수행한다.

```
┌─────────────────────────────────────────────────────────────┐
│                     오케스트레이터 레이어                      │
│                                                             │
│  pipet_data_collector   pipet_system_teleop   pipet_inference│
│  (데이터 동기화/저장)    (키보드 → 서비스 호출)  (모델 → 서비스 호출)│
└──────────────────────────┬──────────────────────────────────┘
                           │ topics / services
┌──────────────────────────┼──────────────────────────────────┐
│                       모듈 레이어                             │
│                                                             │
│   Indy7 모듈              Mark7 모듈         RealSense 모듈   │
│   (indy-ros2)            (자체 개발)         (realsense2-camera)│
│   /joint_states          /gripper/status    /camera/color/.. │
│   move(), ...            grasp(), open(),   /camera/depth/.. │
│                          press()                            │
└─────────────────────────────────────────────────────────────┘
```

- **모듈 레이어**: 각 장치의 기능을 ROS2 토픽/서비스로 노출. 어떻게 트리거되는지는 알지 못함.
- **오케스트레이터 레이어**: 모듈의 인터페이스를 조합하여 데이터 수집 / 텔레오프 / 추론을 수행.

### 하드웨어 구성

| 장치 | 모델 | 역할 | 부착 위치 |
|------|------|------|-----------|
| 로봇팔 | Neuromeka Indy7 | 파이펫 위치 이동 | — |
| 로봇손 | Mand.ro Mark7 | 파이펫 파지 및 조작 | Indy7 엔드이펙터 |
| 카메라 | Intel RealSense D435 | RGB/Depth 이미지 수집, 배포 시 파이펫 인식 | Mark7와 함께 엔드이펙터에 부착 (전용 케이스 제작 필요) |

---

## 3. 컴포넌트 상세

### 3.1 모듈 레이어

각 장치의 기능을 ROS2 토픽/서비스로 노출한다. 오케스트레이터가 어떻게 사용하는지는 알지 못한다.

#### Indy7 모듈 (`indy-ros2`, 서브모듈)

| 종류 | 이름 | 타입 | 설명 |
|------|------|------|------|
| 토픽 (발행) | `/joint_states` | sensor_msgs/JointState | 관절 각도/속도/토크, 20Hz |
| 서비스 | `move_to_joint` | (indy-ros2 정의) | 관절 각도 목표 이동 |
| 서비스 | `set_direct_teaching` | (indy-ros2 정의) | 직접 교시 모드 on/off |

#### Mark7 모듈 (`pipet_hand_mark7_driver`, 자체 개발)

> 상세 설계: [docs/mark7/architecture.md](mark7/architecture.md)

| 종류 | 이름 | 타입 | 설명 |
|------|------|------|------|
| 토픽 (발행) | `/gripper/status` | (자체 정의) | 그리퍼 현재 상태, ~0.7Hz (시리얼 통신 제약) |
| 서비스 | `/gripper/grasp` | std_srvs/Trigger | 파이펫 잡기 |
| 서비스 | `/gripper/open` | std_srvs/Trigger | 손 펴기 |
| 서비스 | `/gripper/press` | std_srvs/Trigger | 파이펫 누르기 (잡은 상태 유지하며 엄지만 누름) |
| 서비스 | `/gripper/release` | std_srvs/Trigger | 엄지 펴기 (잡은 상태 유지하며 엄지만 펴기) |

#### RealSense 모듈 (`ros-humble-realsense2-camera`, 공식 패키지) — 2대

| 종류 | 이름 | 타입 | 설명 |
|------|------|------|------|
| 토픽 (발행) | `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | 손목 카메라 RGB, ~9.5Hz |
| 토픽 (발행) | `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 손목 카메라 Depth, ~9.5Hz |
| 토픽 (발행) | `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 RGB, ~9.5Hz |
| 토픽 (발행) | `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 Depth, ~9.5Hz |

---

### 3.2 오케스트레이터 레이어

모듈의 토픽/서비스를 조합하여 시스템 수준의 동작을 수행한다.

#### pipet_data_collector

**역할**: 세 모듈의 데이터를 시간 동기화하여 NPZ로 저장

**동기화 방식**: `ApproximateTimeSynchronizer` (~20Hz, 5토픽 동기화 + 그리퍼 캐시)

| 구독 토픽 | 타입 | 출처 | 동기화 |
|-----------|------|------|--------|
| `/joint_states` | sensor_msgs/JointState | Indy7 모듈 | 동기화 |
| `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | RealSense (손목) | 동기화 |
| `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | RealSense (손목) | 동기화 |
| `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | RealSense (오버헤드) | 동기화 |
| `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | RealSense (오버헤드) | 동기화 |
| `/gripper/status` | (자체 정의) | Mark7 모듈 | 최신값 캐시 (~0.7Hz) |

**저장 데이터 (NPZ)** — 파일명: `episode_YYYYMMDD_HHMMSS_success|fail.npz`

| 키 | Shape | 설명 |
|----|-------|------|
| `timestamps` | (N,) | 녹화 시작 기준 상대 시간 |
| `joint_positions` | (N, 6) | Indy7 관절 각도 (rad) |
| `joint_velocities` | (N, 6) | Indy7 관절 속도 (rad/s) |
| `joint_efforts` | (N, 6) | Indy7 관절 토크 (N·m) |
| `wrist_rgb_images` | (N, 480, 640, 3) | 손목 카메라 RGB 이미지 |
| `wrist_depth_images` | (N, 480, 640) | 손목 카메라 Depth 이미지 (mm) |
| `overhead_rgb_images` | (N, 480, 640, 3) | 오버헤드 카메라 RGB 이미지 |
| `overhead_depth_images` | (N, 480, 640) | 오버헤드 카메라 Depth 이미지 (mm) |
| `gripper_actions` | (N,) | 그리퍼 액션: 0=유지, 1=잡기, 2=펴기, 3=누르기, 4=엄지 펴기 |
| `success` | () | 에피소드 성공 여부 (True/False) |

**저장 경로:** 성공/실패에 따라 서브폴더로 분류
```
episodes/
├── success/   # 성공 에피소드
├── fail/      # 실패 에피소드
└── unlabeled/ # 라벨 없는 에피소드
```

> **메모**: 연속값(손가락 6개 관절 각도) 방식도 고려 가능. 더 자연스러운 동작이 가능하나 학습 복잡도가 올라감. 파이펫 조작은 동작이 고정적이라 현재는 이산값으로 충분하다고 판단.

#### pipet_system_teleop

**역할**: 키보드 입력을 받아 모듈 서비스를 호출. 녹화 제어.

| 키 | 동작 | 호출 서비스 |
|----|------|------------|
| `SPACE` | 에피소드 녹화 시작/중지 | — (data_collector 제어) |
| `H` | Indy7 홈 포지션 이동 | `move_to_joint` |
| `G` | Mark7 잡기 | `/gripper/grasp` |
| `O` | Mark7 펴기 | `/gripper/open` |
| `P` | Mark7 파이펫 누르기 | `/gripper/press` |
| `Q` | 종료 | — |

#### pipet_inference

**역할**: 학습된 모델을 로드하여 모듈 서비스를 호출

**흐름**:
```
RealSense 토픽 (RGB/Depth) + Indy7 토픽 (관절값)
        ↓
학습된 모델 (LeRobot / Isaac Lab / Unity)
        ↓
move_to_joint() + /gripper/grasp|open|press() 호출
```

### 3.5 데이터 수집 전략

#### 수집 방식
- Indy7: 직접 교시 (중력 보상 모드로 손으로 직접 조작)
- Mark7: 키보드로 조작 (잡기/펴기/파이펫 누르기)

#### AI 학습 방법 (3가지 병행 시도)
1. **Isaac Lab + Robomimic** — BC 모방학습 후 PPO 강화학습, GPU 병렬 시뮬레이션
2. **Hugging Face LeRobot** — ACT, Diffusion Policy 등 최신 알고리즘, 실제 로봇 배포 초점
* [LeRobotDataset v3.0 관련 문서](./ai/ai_architecture.md)
3. **Unity ML-Agents** — GAIL(적대적 모방학습) + PPO

#### 에피소드
- 에피소드 = 시연 1회 (홈 포지션 → 파이펫 잡기)
- 초기 목표: 50 에피소드
- 이후 결과를 보며 점진적으로 증가

#### 유의사항
- 쓰레기 데이터보다 깔끔한 시연이 중요 → 에피소드 검수 기준 필요
- 거치대 위치/각도/조명을 조금씩 다르게 수집 (다양성 확보)
- 에피소드마다 시작 상태(홈 포지션) 통일
- 팔 동작과 그리퍼 동작의 타이밍 싱크 주의

---

## 4. 데이터 흐름

### 4.1 데이터 수집 단계 (텔레오프)

```
Indy7 직접 교시 + Mark7 키보드 조작
        ↓
텔레오프 노드 (녹화 제어)
        ↓
데이터 수집 노드 (ApproximateTimeSynchronizer ~15Hz)
관절값 + RGB/Depth + 그리퍼 액션 동기화
        ↓
NPZ 파일 저장 (에피소드 단위)
```

### 4.2 AI 학습 단계

```
NPZ 파일 (에피소드 묶음)
        ↓
포맷 변환 (학습 프레임워크별)
├── Isaac Lab + Robomimic → HDF5
├── LeRobot              → LeRobot 데이터셋 포맷
└── Unity ML-Agents      → Unity 데모 포맷
        ↓
모델 학습
├── Isaac Lab + Robomimic: BC(모방학습) → PPO(강화학습)
├── LeRobot: ACT / Diffusion Policy
└── Unity ML-Agents: GAIL + PPO
        ↓
학습된 모델 파일
```

### 4.3 모델 테스트/배포 단계

```
RealSense (RGB/Depth) + Indy7 관절값
        ↓
추론 노드 (학습된 모델 로드)
        ↓
Indy7 관절 명령 + Mark7 그리퍼 명령
        ↓
실제 로봇 동작
```

---

## 5. 하드웨어 인터페이스

### 5.1 PC 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 |
| ROS | ROS2 Humble |

### 5.2 장치 연결

| 장치 | 연결 방식 | 인터페이스 |
|------|----------|------------|
| Indy7 | 이더넷 (기본) / WiFi (대안) | TCP/IP — 고정 IP `192.168.1.10` |
| Mark7 RF 동글 | USB Serial | `/dev/ttyACM0`, 115200 bps |
| RealSense D435 | USB | USB 3.0 |

### 5.3 네트워크 구성

```
PC (192.168.1.100)
  ├── [이더넷] ──────────── Indy7 (192.168.1.10)
  ├── [USB Serial] ──────── RF 동글 (/dev/ttyACM0)
  │                              └── 2.4GHz RF ── Mark7
  └── [USB 3.0] ─────────── RealSense D435
```

---

## 6. 제약 조건 / 미결 사항

### 6.1 제약 조건

| 항목 | 내용 |
|------|------|
| 최소 성공 기준 | 파이펫 잡기 성공. Physical AI 적용이 어려울 수 있으나 시도한다. |
| 컴퓨팅 자원 | GPU 학습용 서버 미확보 — 추후 보충 예정 |
| RF 통신 안정성 | 2.4GHz RF 특성상 신호 손실 가능 → 중요 명령 반복 전송 필요 |

### 6.2 미결 사항

| 항목 | 내용 |
|------|------|
| AI 학습 방법 | 3가지 방법(Isaac Lab, LeRobot, Unity) 중 어느 것이 성공할지 미지수 |
| 필요 에피소드 수 | 50개로 학습 가능한지 불명확 — 결과 보며 점진적으로 증가 |
| 파이펫 인식 방법 | 배포 시 RealSense로 파이펫 위치 추정 방법 미결정 |
| Mark7 캘리브레이션 | URDF 관절 각도 ↔ Mark7 position count 매핑 실측 필요 |

---

## 7. 워크스페이스 구조

```
pipet_physical_ai/
├── docs/                               # 설계 문서
├── ai/                                 # AI 학습
│   ├── data_conversion/                # NPZ → 각 프레임워크 포맷 변환 스크립트
│   │   ├── npz_to_hdf5/               # Isaac Lab + Robomimic용
│   │   ├── npz_to_lerobot/            # LeRobot용
│   │   └── npz_to_unity/              # Unity ML-Agents용
│   ├── isaac_lab_robomimic/            # Isaac Lab + Robomimic 학습
│   ├── lerobot/                        # LeRobot 학습
│   └── unity_ml_agents/               # Unity ML-Agents 학습
└── ros2_ws/                            # ROS2 워크스페이스
    └── src/
        │
        │  # ── 모듈 레이어 ──────────────────────────────────────
        ├── indy7_ros2/                    # Indy7 모듈 (서브모듈, 기존 드라이버 그대로 사용)
        ├── realsense-ros/                 # RealSense 모듈 (공식 패키지 그대로 사용)
        ├── mark7/                         # Mark7 관련 패키지 묶음
        │   ├── pipet_hand_mark7_description/  # Mark7 URDF/메시/RViz
        │   ├── pipet_hand_mark7_driver/       # Mark7 모듈 (ros2_control)
        │   │                                  #   ForwardCommandController (관절 직접 제어)
        │   │                                  #   GripPresetNode (grasp/open/press 서비스)
        │   │                                  #   → /gripper/status, grasp(), open(), press()
        │   ├── pipet_hand_mark7_teleop/       # Mark7 단독 테스트용 (개별 손가락 키보드 제어)
        │   └── pipet_hand_mark7_gazebo/       # Gazebo 시뮬 + 실제 미러링
        │
        │  # ── 오케스트레이터 레이어 ──────────────────────────────
        ├── pipet_data_collector/          # 데이터 수집 (동기화 + NPZ 저장)
        ├── pipet_system_teleop/           # 통합 텔레오프 (키보드 → 모듈 서비스 호출)
        ├── pipet_inference/               # 추론 (학습된 모델 → 모듈 서비스 호출)
        │
        │  # ── Description ────────────────────────────────────
        └── pipet_system_description/      # 통합 URDF (Indy7 + Mark7 + RealSense)
```
