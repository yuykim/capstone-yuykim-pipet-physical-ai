# ROS2 인터페이스 명세

**최종 수정:** 2026-03-06
**참조:** [전체 시스템 설계](architecture.md)

---

## 1. 개요

이 문서는 팀 분업을 위한 ROS2 노드 간 인터페이스 계약서이다.
각 패키지의 담당자는 다른 패키지의 내부 구현을 알 필요 없이 이 문서만으로 자신의 패키지를 개발할 수 있어야 한다.

### 패키지 목록

**모듈 레이어** — 각 장치의 기능을 토픽/서비스로 노출

| 패키지 | 설명 |
|--------|------|
| `indy7_ros2` | Indy7 로봇팔 드라이버 (서브모듈, 기존 패키지 사용) |
| `pipet_hand_mark7_driver` | Mark7 로봇손 드라이버 (자체 개발, ros2_control 기반) |
| `realsense2_camera` | RealSense D435 드라이버 (공식 패키지 사용) |

**오케스트레이터 레이어** — 모듈 인터페이스를 조합하여 시스템 동작 수행

| 패키지 | 설명 |
|--------|------|
| `pipet_data_collector` | 세 모듈의 데이터를 시간 동기화하여 NPZ로 저장 |
| `pipet_system_teleop` | 키보드 입력을 받아 모듈 서비스를 호출, 녹화 제어 |
| `pipet_inference` | 학습된 모델을 로드하여 모듈 서비스를 호출 |

**보조 패키지**

| 패키지 | 설명 |
|--------|------|
| `pipet_hand_mark7_teleop` | Mark7 단독 테스트용 (개별 손가락 키보드 제어) |
| `pipet_hand_mark7_gazebo` | Mark7 Gazebo 시뮬 + 실제 로봇 미러링 |
| `pipet_system_description` | 통합 URDF (Indy7 + Mark7 + RealSense) |

### 노드 간 의존 관계

```
                    [pipet_system_teleop]   [pipet_inference]
                           │                      │
              서비스 호출   │                      │  서비스 호출
                           │                      │
          ┌────────────────┴──────────────────────┘
          │
          ▼
[indy7_ros2]          [pipet_hand_mark7_driver]    [realsense2_camera]
/joint_states         /gripper/status              /camera/.../image_raw
move_to_joint         /gripper/grasp|open|press
set_direct_teaching
          │                      │                        │
          └──────────────────────┴────────────────────────┘
                                 │
                                 ▼
                      [pipet_data_collector]
                        (토픽 구독 → NPZ 저장)
                                 │
                                 │ NPZ 파일 (episodes/*.npz)
                                 ▼
                        [ai/ 학습 파이프라인]
                  ├── npz_to_hdf5    → Isaac Lab + Robomimic
                  ├── npz_to_lerobot → LeRobot
                  └── npz_to_unity   → Unity ML-Agents
```

---

## 2. 패키지별 인터페이스 명세

### 2.1 Indy7 모듈 (`indy7_ros2`)

**역할**: Indy7 로봇팔과 통신하는 드라이버. 기존 패키지(neuromeka-robotics/indy-ros2)를 서브모듈로 사용.

#### 발행 토픽

| 토픽 | 타입 | QoS | 설명 |
|------|------|-----|------|
| `/joint_states` | sensor_msgs/JointState | RELIABLE, depth 10 | 관절 위치/속도/토크, 20Hz |

#### 구독 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/joint_trajectory_controller/joint_trajectory` | trajectory_msgs/JointTrajectory | 관절 궤적 명령 (토픽 방식, 피드백 없음) |

#### 제공 액션

| 액션 | 타입 | 설명 |
|------|------|------|
| `/joint_trajectory_controller/follow_joint_trajectory` | control_msgs/FollowJointTrajectory | 관절 궤적 실행 (완료 피드백, 취소 가능) |

> **사용 지침**: `pipet_inference`처럼 연속적으로 목표값을 보낼 때는 토픽 방식, 단일 목표 이동(홈 복귀 등)은 액션 방식을 권장.

#### 제공 서비스

| 서비스 | 타입 | 설명 |
|--------|------|------|
| `indy_srv` | indy_interfaces/IndyService | 단일 서비스로 모든 로봇 명령 처리 |

**IndyService 정의:**
```
int32 data      # 명령 코드
---
bool success
string message
```

**주요 명령 코드:**

| 코드 | 상수명 | 설명 |
|------|--------|------|
| 1 | MSG_RECOVER | 에러 상태 복구 |
| 2 | MSG_MOVE_HOME | 홈 포지션으로 이동 |
| 9 | MSG_DIRECT_TEACHING_ON | 직접 교시 모드 활성화 (중력 보상) |
| 10 | MSG_DIRECT_TEACHING_OFF | 직접 교시 모드 비활성화 |
| 11 | MSG_MOVE_SAFE | 관절 한계 근처 조인트만 안전 위치로 이동 |

#### 런치 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `indy_ip` | string | `"192.168.1.10"` | 로봇 IP 주소 |
| `indy_type` | string | `"indy7"` | 로봇 모델 종류 |

---

### 2.2 RealSense 모듈 (`realsense2_camera`)

**역할**: Intel RealSense D435 카메라 드라이버. 공식 패키지(IntelRealSense/realsense-ros)를 사용.

#### 발행 토픽

듀얼 카메라 구성: 손목 카메라(wrist)와 오버헤드 카메라(overhead). 토픽 이름은 `/{camera_namespace}/{camera_name}/` 접두사를 가진다.

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | 손목 카메라 RGB 이미지, 기본 30Hz |
| `/wrist_camera/camera/color/camera_info` | sensor_msgs/CameraInfo | 손목 카메라 RGB 내부 파라미터 |
| `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 손목 카메라 Color에 정렬된 Depth 이미지 |
| `/wrist_camera/camera/aligned_depth_to_color/camera_info` | sensor_msgs/CameraInfo | 손목 카메라 Depth 내부 파라미터 |
| `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 RGB 이미지, 기본 30Hz |
| `/overhead_camera/camera/color/camera_info` | sensor_msgs/CameraInfo | 오버헤드 카메라 RGB 내부 파라미터 |
| `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 Color에 정렬된 Depth 이미지 |
| `/overhead_camera/camera/aligned_depth_to_color/camera_info` | sensor_msgs/CameraInfo | 오버헤드 카메라 Depth 내부 파라미터 |

#### 런치 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `camera_name` | string | `"camera"` | 노드 이름 (토픽 접두사에 영향) |
| `camera_namespace` | string | `"camera"` | 네임스페이스 (토픽 접두사에 영향) |
| `enable_color` | bool | `true` | RGB 스트림 활성화 |
| `enable_depth` | bool | `true` | Depth 스트림 활성화 |
| `align_depth.enable` | bool | `false` | **aligned_depth 토픽 사용 시 반드시 `true`로 설정** |
| `rgb_camera.color_profile` | string | `"0,0,0"` | RGB 해상도/FPS (0=자동) |
| `depth_module.depth_profile` | string | `"0,0,0"` | Depth 해상도/FPS (0=자동) |

---

### 2.3 Mark7 모듈 (`pipet_hand_mark7_driver`)

**역할**: Mand.ro Mark7 로봇손 드라이버. ros2_control 기반 자체 개발.
ForwardCommandController로 개별 손가락 제어, GripPresetNode로 프리셋 서비스 제공.

> **네임스페이스**: Mark7 드라이버는 `/mark7` 네임스페이스로 실행된다. Indy7의 `/joint_states`와 충돌 방지.

#### 발행 토픽

| 토픽 | 타입 | QoS | 설명 |
|------|------|-----|------|
| `/gripper/status` | pipet_hand_mark7_msgs/GripperStatus | RELIABLE | 손가락 6개 현재 상태. Rx 수신 시에만 발행 (~0.5Hz) |
| `/mark7/joint_states` | sensor_msgs/JointState | RELIABLE | 손가락 6개 관절 위치 (steps). Rx 수신 시에만 발행 (~0.5Hz) |

**GripperStatus 메시지 정의 (자체 정의):**
```
# pipet_hand_mark7_msgs/GripperStatus
std_msgs/Header header
FingerState[6] fingers   # 손가락 6개 상태 배열
```
```
# FingerState
float32 position    # 현재 위치 (steps, Rx에서 직접 수신)
float32 current     # 전류 (mA, Rx에서 직접 수신)
float32 temperature # 온도 (°C)
```

손가락 인덱스 순서: `[0]Thumb, [1]Index, [2]Middle, [3]Ring, [4]Little, [5]Thumb Ab`

#### 구독 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/mark7/forward_position_controller/commands` | std_msgs/Float64MultiArray | 손가락 6개 목표 위치 (steps). 명령 변경 시 Tx 패킷 1회 전송. 연속 전송 시 하드웨어 처리 불가. |

#### 제공 서비스

| 서비스 | 타입 | 설명 |
|--------|------|------|
| `/gripper/grasp` | std_srvs/Trigger | 파이펫 잡기 프리셋 실행 |
| `/gripper/open` | std_srvs/Trigger | 손 펴기 프리셋 실행 |
| `/gripper/press` | std_srvs/Trigger | 파이펫 누르기 프리셋 실행 |
| `/gripper/release` | std_srvs/Trigger | 엄지 펴기 프리셋 실행 (잡은 상태 유지) |

#### 런치 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `use_mock_hardware` | bool | `false` | `true`: 하드웨어 없이 소프트웨어만 동작 |
| `port` | string | `"/dev/ttyACM0"` | RF 동글 시리얼 포트 |
| `use_rviz` | bool | `false` | RViz2 시각화 실행 여부 |

---

### 2.4 데이터 수집 모듈 (`pipet_data_collector`)

**역할**: 세 모듈의 데이터를 시간 동기화하여 에피소드 단위 NPZ 파일로 저장.

#### 구독 토픽

| 토픽 | 타입 | 출처 |
|------|------|------|
| `/joint_states` | sensor_msgs/JointState | Indy7 모듈 |
| `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | 손목 카메라 (RealSense) |
| `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 손목 카메라 (RealSense) |
| `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 (RealSense) |
| `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 (RealSense) |
| `/gripper/status` | pipet_hand_mark7_msgs/GripperStatus | Mark7 모듈 |

동기화 방식: 5토픽 동기화 + 그리퍼 캐시, ~20Hz

#### 제공 서비스

| 서비스 | 타입 | 설명 |
|--------|------|------|
| `/data_collector/start` | std_srvs/Trigger | 녹화 시작. 이미 녹화 중이면 실패 반환. |
| `/data_collector/stop` | std_srvs/Trigger | 녹화 중지 및 NPZ 저장. 녹화 중이 아니면 실패 반환. |

#### 발행 토픽

| 토픽 | 타입 | QoS | 설명 |
|------|------|-----|------|
| `/data_collector/is_recording` | std_msgs/Bool | RELIABLE, depth 1 | 현재 녹화 상태 (모니터링용) |

#### NPZ 저장 형식

저장 경로: `episodes/<success|fail|unlabeled>/episode_<YYYYMMDD_HHMMSS>_<label>.npz`

| 키 | Shape | dtype | 설명 |
|----|-------|-------|------|
| `timestamps` | (N,) | float64 | 녹화 시작 기준 상대 시간 (초) |
| `home_joint_deg` | (6,) | float32 | 수집 당시 홈 포지션 metadata, 학습 변환 제외 |
| `camera_setup` | () | str | 카메라 구성 metadata, 학습 변환 제외 |
| `joint_positions` | (N, 6) | float32 | Indy7 관절 각도 (rad) |
| `joint_velocities` | (N, 6) | float32 | Indy7 관절 속도 (rad/s) |
| `joint_efforts` | (N, 6) | float32 | Indy7 관절 토크 (N·m) |
| `wrist_rgb_images` | (N, 480, 640, 3) | uint8 | 손목 카메라 RGB 이미지 |
| `wrist_depth_images` | (N, 480, 640) | uint16 | 손목 카메라 Depth 이미지 (mm) |
| `overhead_rgb_images` | (N, 480, 640, 3) | uint8 | 오버헤드 카메라 RGB 이미지 |
| `overhead_depth_images` | (N, 480, 640) | uint16 | 오버헤드 카메라 Depth 이미지 (mm) |
| `gripper_actions` | (N,) | int8 | 그리퍼 모드: 0=유지 / 1=잡기 / 2=펴기 / 3=파이펫 누르기 / 4=엄지 펴기(release) |

#### 런치 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `output_dir` | string | `"episodes"` | NPZ 저장 디렉터리 경로 |
| `image_size` | int | `224` | 저장할 이미지 한 변 크기 (px) |
| `sync_slop` | float | `0.1` | ApproximateTimeSynchronizer 허용 시간 오차 (초) |

---

### 2.5 통합 텔레오프 (`pipet_system_teleop`)

**역할**: 키보드 입력으로 모듈 서비스를 호출하고, 데이터 수집 노드의 녹화를 제어.

#### 호출하는 서비스 (클라이언트)

| 키 | 동작 | 호출 서비스 | 타입 |
|----|------|------------|------|
| `SPACE` | 녹화 시작/중지 토글 | `/data_collector/start` 또는 `/data_collector/stop` | std_srvs/Trigger |
| `H` | Indy7 홈 포지션 이동 | `indy_srv` (MSG_MOVE_HOME) | indy_interfaces/IndyService |
| `D` | 직접 교시 모드 ON | `indy_srv` (MSG_DIRECT_TEACHING_ON) | indy_interfaces/IndyService |
| `d` | 직접 교시 모드 OFF | `indy_srv` (MSG_DIRECT_TEACHING_OFF) | indy_interfaces/IndyService |
| `G` | Mark7 잡기 | `/gripper/grasp` | std_srvs/Trigger |
| `O` | Mark7 펴기 | `/gripper/open` | std_srvs/Trigger |
| `P` | Mark7 파이펫 누르기 | `/gripper/press` | std_srvs/Trigger |
| `R` | Mark7 엄지 펴기 (release) | `/gripper/release` | std_srvs/Trigger |
| `Q` | 노드 종료 | — | — |

> **참고**: `D`/`d`는 대소문자를 구분한다 (대문자=교시 ON, 소문자=교시 OFF). 나머지 키는 대소문자 구분 없이 동작한다.

#### 구독 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/data_collector/is_recording` | std_msgs/Bool | 현재 녹화 상태 표시용 (터미널 UI) |

---

### 2.6 추론 모듈 (`pipet_inference`)

**역할**: 학습된 모델을 로드하여 센서 데이터를 입력받고, 모듈 서비스를 호출해 로봇을 자율 동작시킴.

#### 구독 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/joint_states` | sensor_msgs/JointState | Indy7 관절 상태 |
| `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | 손목 카메라 RGB 이미지 |
| `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 손목 카메라 Depth 이미지 |
| `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 RGB 이미지 |
| `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 Depth 이미지 |

#### 호출하는 서비스 (클라이언트)

| 서비스 | 타입 | 설명 |
|--------|------|------|
| `/joint_trajectory_controller/follow_joint_trajectory` | control_msgs/FollowJointTrajectory (액션) | Indy7 관절 이동 |
| `/gripper/grasp` | std_srvs/Trigger | Mark7 잡기 |
| `/gripper/open` | std_srvs/Trigger | Mark7 펴기 |
| `/gripper/press` | std_srvs/Trigger | Mark7 파이펫 누르기 |

#### 런치 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `model_path` | string | `""` | 학습된 모델 파일 경로 (필수) |
| `model_type` | string | `"lerobot"` | 모델 종류: `lerobot` / `robomimic` |
| `inference_hz` | float | `15.0` | 추론 주기 (Hz) |

---

### 2.7 Mark7 단독 텔레오프 (`pipet_hand_mark7_teleop`)

**역할**: Mark7 단독 테스트용. 공백 구분 6개 숫자를 입력받아 절대 위치 명령 전송.

**입력 방식**: `100 100 100 100 0 0` 형태로 Enter 입력 → 1회 전송

조인트 순서: `[0]Thumb Flex [1]Index [2]Middle [3]Ring [4]Pinky [5]Thumb Ab`
범위: Thumb Flex 0~187, 나머지 0~300 (steps)

#### 발행 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/mark7/forward_position_controller/commands` | std_msgs/Float64MultiArray | 손가락 6개 목표 위치 (steps). Enter 입력 시 1회 발행. |

---

## 3. 노드 실행 순서 및 의존 관계

오케스트레이터 레이어는 모듈 레이어가 모두 준비된 후 실행해야 한다.

### 3.1 데이터 수집 시나리오

```
1. indy7_ros2            → /joint_states, indy_srv 준비
2. realsense2_camera     → /camera/.../image_raw 준비
3. pipet_hand_mark7_driver → /gripper/status, /gripper/grasp|open|press 준비
        (모듈 레이어 준비 완료)
4. pipet_data_collector  → 모듈 토픽 구독 시작, /data_collector/start|stop 준비
5. pipet_system_teleop   → 키보드 입력 수신 시작
```

### 3.2 추론(배포) 시나리오

```
1. indy7_ros2
2. realsense2_camera
3. pipet_hand_mark7_driver
        (모듈 레이어 준비 완료)
4. pipet_inference       → 모델 로드 후 추론 시작
```

### 3.3 Mark7 단독 테스트 시나리오

```
1. pipet_hand_mark7_driver
2. pipet_hand_mark7_teleop
```

### 3.4 의존 관계 요약

| 패키지 | 실행 전 준비되어야 할 패키지 |
|--------|--------------------------|
| `pipet_data_collector` | `indy7_ros2`, `realsense2_camera`, `pipet_hand_mark7_driver` |
| `pipet_system_teleop` | `indy7_ros2`, `pipet_hand_mark7_driver`, `pipet_data_collector` |
| `pipet_inference` | `indy7_ros2`, `realsense2_camera`, `pipet_hand_mark7_driver` |
| `pipet_hand_mark7_teleop` | `pipet_hand_mark7_driver` |

---

## 4. 커스텀 메시지/서비스 정의 목록

자체 정의가 필요한 항목 (`pipet_hand_mark7_msgs` 패키지에 위치):

| 이름 | 종류 | 정의 위치 |
|------|------|-----------|
| `GripperStatus` | msg | `pipet_hand_mark7_msgs/msg/GripperStatus.msg` |
| `FingerState` | msg | `pipet_hand_mark7_msgs/msg/FingerState.msg` |

나머지는 모두 ROS2 표준 타입 (`std_srvs`, `sensor_msgs`, `std_msgs`, `control_msgs`) 사용.

---
