# Pipet Physical AI (ROS2 + AI)

이 문서는 프로젝트 전체 흐름을 한 번에 이해하기 위한 통합 README다.

```text
직접교시(ROS2) 수집 -> NPZ 저장 -> LeRobotDataset 변환 -> LeRobot 학습 -> 실제 로봇 추론 배포
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

### 2-0. 네트워크 설정 (최초 1회)

Indy7(IP: `192.168.1.10`)과 통신하려면 PC에 같은 대역의 IP를 설정해야 한다.

**방법 A: USB 이더넷 어댑터 직접 연결 (권장)**
```bash
# 영구 설정 (재부팅 후에도 유지)
sudo nmcli con mod enx00e04c360046 ipv4.addresses 192.168.1.100/24 ipv4.method manual
sudo nmcli con up enx00e04c360046

# 확인
ping 192.168.1.10
```

**방법 B: 공유기 경유 연결**

로봇과 PC를 같은 공유기에 연결한 후, PC 내장 이더넷에 로봇 대역 IP를 추가한다.
```bash
# 임시 설정 (재부팅 시 사라짐)
sudo ip addr add 192.168.1.100/24 dev enp0s31f6

# 영구 설정
sudo nmcli con mod enp0s31f6 +ipv4.addresses 192.168.1.100/24

# 확인
ping 192.168.1.10
```

> **트러블슈팅:** ping 실패 → ① 로봇 컨트롤러 전원 확인 ② 케이블 확인 ③ `ip addr show`에서 IP 할당 확인. gRPC 포트 실패(`nc -zv 192.168.1.10 20001`) → 컨트롤러 재부팅 후 2~3분 대기.

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
  --dataset_output_dir <lerobot_dataset_dir> \
  --dataset_repo_id pipet_dataset \
  --output_dir outputs/train/act_pipet \
  --device cuda
```

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
