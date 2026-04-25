# Pipet Physical AI (ROS2 + AI)

이 문서는 프로젝트 전체 흐름을 한 번에 이해하기 위한 통합 README다.

```text
직접교시(ROS2) 수집 -> NPZ 저장 -> LeRobotDataset 변환 -> LeRobot 학습 -> 실제 로봇 추론 배포
```

---

## 빠른 실행 코드

아래 명령은 레포 루트에서 실행한다. 새 터미널을 열 때마다 먼저 ROS2 환경을 로드한다.

```bash
cd <repo_root>
source /opt/ros/humble/setup.bash
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

### 1. 학습 실행

```bash
python ai/lerobot/run_lerobot_train.py \
  --episodes_dir episodes \
  --dataset_output_dir ai/datasets/pipet_dataset \
  --dataset_repo_id pipet_dataset \
  --job_name act_pipet \
  --device cuda
```

### 2. 데이터 수집 실행

터미널 1에서 전체 하드웨어와 데이터 수집 노드를 띄운다.

```bash
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
```

터미널 2에서 통합 조작 노드를 실행한다.

```bash
ros2 run pipet_system_teleop system_teleop_node
```

`SPACE`로 녹화를 시작/종료하고, 종료 시 `Y` 성공, `N` 실패, `X` 폐기를 선택한다.

### 3. 그리퍼 조작 테스트

터미널 1에서 Mark7 드라이버를 실행한다.

```bash
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py port:=/dev/ttyACM0
```

터미널 2에서 손가락 목표값을 직접 입력하는 테스트 노드를 실행한다.

```bash
ros2 run pipet_hand_mark7_teleop teleop_keyboard
```

프리셋 서비스로 테스트하려면 터미널 2에서 프리셋 노드를 띄운 뒤, 터미널 3에서 원하는 서비스를 호출한다.

```bash
ros2 run pipet_hand_mark7_teleop grip_preset_node
```

```bash
ros2 service call /gripper/open std_srvs/srv/Trigger {}
ros2 service call /gripper/grasp std_srvs/srv/Trigger {}
ros2 service call /gripper/press std_srvs/srv/Trigger {}
ros2 service call /gripper/release std_srvs/srv/Trigger {}
```

### 4. Indy7 조작

터미널 1에서 Indy7 드라이버를 실행한다. Cartesian X/Y/Z 조작까지 쓰려면 `enable_cartesian_servo:=true`를 켠다.

```bash
ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10 enable_cartesian_servo:=true
```

터미널 2에서 텔레옵 노드를 실행한다.

```bash
ros2 run pipet_system_teleop system_teleop_node
```

주요 키는 `H` home, `D/d` direct teaching ON/OFF, 방향키 X/Y, `;`/`.` Z up/down, `B/T` base/TCP frame, `9/0` 속도 조절이다.

### 5. 카메라 2개 화면 확인

데이터 수집 launch를 이미 실행 중이면 카메라 노드는 떠 있으므로 화면만 띄우면 된다.

```bash
ros2 run rqt_image_view rqt_image_view /wrist_camera/camera/color/image_raw
```

```bash
ros2 run rqt_image_view rqt_image_view /overhead_camera/camera/color/image_raw
```

카메라만 단독으로 띄울 때는 두 터미널에서 각각 RealSense 노드를 실행한 뒤 위의 `rqt_image_view` 명령을 실행한다.

```bash
ros2 run realsense2_camera realsense2_camera_node --ros-args \
  -r __ns:=/wrist_camera \
  -r __node:=camera \
  -p serial_no:="_844212071939" \
  -p enable_color:=true \
  -p enable_depth:=true \
  -p align_depth.enable:=true
```

```bash
ros2 run realsense2_camera realsense2_camera_node --ros-args \
  -r __ns:=/overhead_camera \
  -r __node:=camera \
  -p serial_no:="_317222074298" \
  -p enable_color:=true \
  -p enable_depth:=true \
  -p align_depth.enable:=true
```

---

## 1. 프로젝트 개요

Indy7 로봇팔 + Mark7 로봇손 + RealSense D435(손목/오버헤드) 2대를 사용해
피펫 조작을 학습/배포하는 Physical AI 프로젝트다.

### 시스템 구성
| 항목 | 내용 |
|---|---|
| 로봇팔 | Neuromeka Indy7 |
| 로봇손 | Mand.ro Mark7 |
| 카메라 | RealSense D435 x 2 (wrist, overhead) |
| OS/ROS | Ubuntu 22.04 / ROS2 Humble |
| DDS | Cyclone DDS |

---

## 2. 데이터 수집은 어떻게 하나?

데이터 수집은 ROS2에서 수행하고, 결과는 `episodes/episode_*.npz`로 저장된다.

### 2-1. 빌드
```bash
cd <repo_root>
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build
source install/setup.bash
```

### 2-2. 통합 수집 실행
터미널 1 (백엔드):
```bash
cd <repo_root>
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
```

터미널 2 (텔레옵):
```bash
cd <repo_root>
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 run pipet_system_teleop system_teleop_node
```

### 2-3. 텔레옵 키
| 키 | 동작 |
|---|---|
| SPACE | 녹화 시작/중지 (중지 시 Y/N 라벨링) |
| D / d | direct teaching ON/OFF |
| H | Indy7 홈 이동 |
| G / O / P / R | Mark7 grasp/open/press/release |
| E | 에러 복구 |
| S | 상태 확인 |
| Q | 종료 |

### 2-4. NPZ 저장 형식
파일명: `episode_YYYYMMDD_HHMMSS_success.npz` 또는 `_fail.npz`

주요 키:
- `timestamps` `(N,)`
- `joint_positions`, `joint_velocities`, `joint_efforts` `(N,6)`
- `wrist_rgb_images`, `wrist_depth_images`
- `overhead_rgb_images`, `overhead_depth_images`
- `gripper_actions` `(N,)` (`0 hold`, `1 grasp`, `2 open`, `3 press`, `4 release`)
- `success` `()`

---

## 3. 학습은 어디서 일어나나?

학습 엔진은 LeRobot(`lerobot-train`)이고, 이 레포는 변환/실행 스크립트를 제공한다.

### 3-1. NPZ -> LeRobotDataset 변환
```bash
python ai/data_conversion/npz_to_lerobot/convert.py \
  --episodes_dir <episodes_dir> \
  --output_dir <lerobot_dataset_dir> \
  --output_repo_id pipet_dataset \
  --fps 15 \
  --task "Pick up the pipette"
```

### 3-2. 학습 실행 (ACT baseline)
```bash
python ai/lerobot/run_lerobot_train.py \
  --episodes_dir <episodes_dir> \
  --dataset_output_dir ai/datasets/<lerobot_dataset_name> \
  --dataset_repo_id pipet_dataset \
  --job_name act_pipet \
  --device cuda
```
(`--output_dir`를 생략하면 `ai/models/<job_name>`에 체크포인트가 저장된다.)

`--skip_convert`를 주면 기존 변환 데이터셋으로 학습만 수행할 수 있다.

---

## 4. 학습 후 실제 로봇 적용(추론)

추론 노드는 `pipet_inference` 패키지에서 동작한다.

```bash
ros2 launch pipet_bringup inference.launch.py \
  policy_path:=<trained_policy_dir> \
  dataset_root:=<lerobot_dataset_dir> \
  dataset_repo_id:=pipet_dataset \
  task:="Pick up the pipette" \
  inference_hz:=15.0
```

현재 구현:
- 입력: `joint_states`, 손목 RGB, 오버헤드 RGB
- 출력: Indy7 trajectory 토픽 + Mark7 프리셋 서비스 호출

---

## 5. 가상환경에서도 동일 데이터 수집 시도

현재 레포에는 시뮬레이터 완전 통합 대신, 동일 토픽 계약 검증용 리플레이 노드가 있다.

- `pipet_inference/virtual_episode_replay_node.py`
  - 기존 `episode_*.npz`를 읽어 `joint_states`/카메라 토픽 재생
  - `data_collector/log_*` 서비스도 호출해 collector와 동일 파이프라인 검증

실행:
```bash
ros2 run pipet_inference virtual_episode_replay_node \
  --ros-args -p episode_npz_path:=<episode_npz_path> -p auto_record:=true
```

---

## 6. 파일 구조

```text
pipet-physical-ai/
├── docs/
│   ├── architecture.md
│   ├── interface_spec.md
│   └── ai/
│      ├── ai_architecture.md
│      └── lerobot_architecture.md
├── ai/
│   ├── README.md
│   ├── data_conversion/npz_to_lerobot/convert.py
│   ├── lerobot/run_lerobot_train.py
│   ├── lerobot_source/lerobot/
│   └── indy7_lerobot/            # 참고/레거시 스크립트
└── ros2_ws/
   ├── README.md
   └── src/
      ├── pipet_bringup/
      ├── pipet_data_collector/
      ├── pipet_system_teleop/
      ├── pipet_inference/
      ├── indy7_ros2/
      └── mark7/
```

---

## 7. 상세 문서

- 전체 시스템: `docs/architecture.md`
- ROS2 인터페이스: `docs/interface_spec.md`
- AI raw 데이터/학습 전략: `docs/ai/ai_architecture.md`
- LeRobot 전용 매핑/학습: `docs/ai/lerobot_architecture.md`
- AI 폴더 설명: `ai/README.md`
