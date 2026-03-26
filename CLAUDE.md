# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Indy7 로봇팔 + Mand.ro Mark7 로봇손 + RealSense D435 카메라를 이용한 Physical AI 피펫 조작 프로젝트.
직접 교시로 데이터 수집 → AI 학습 → 자율 동작 배포.

**ROS2 Distribution:** Humble (Ubuntu 22.04)
**DDS:** Cyclone DDS (`export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`)

## Network Setup (필수, 최초 1회)

Indy7은 USB 이더넷 어댑터(`enx00e04c360046`)를 통해 연결된다.
PC에 고정 IP를 설정해야 로봇과 통신할 수 있다.

```bash
# 영구 고정 IP 설정 (재부팅 후에도 유지)
sudo nmcli con mod enx00e04c360046 ipv4.addresses 192.168.1.100/24 ipv4.method manual
sudo nmcli con up enx00e04c360046

# 확인
ip addr show enx00e04c360046 | grep inet
# → inet 192.168.1.100/24 가 보여야 함

# 로봇 연결 테스트
ping 192.168.1.10
```

> **트러블슈팅:** `ping 192.168.1.10` 실패 시 → ① 로봇 컨트롤러 전원 확인 ② 이더넷 케이블 확인 ③ `ip addr show enx00e04c360046`에서 IP 할당 확인.
> gRPC 포트 연결 실패(`nc -zv 192.168.1.10 20001`) → 로봇 컨트롤러 재부팅 후 2~3분 대기.

## Common Commands

### Build

```bash
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build                              # 전체 빌드
colcon build --packages-select <pkg>      # 특정 패키지
colcon build --symlink-install            # Python 개발 시 (수정 즉시 반영)
source install/setup.bash                 # 빌드 후 반드시 source
```

### Build Order

`indy_interfaces` → `pipet_hand_mark7_msgs` → 나머지 (colcon이 자동 해결)

### Data Collection (전체 시스템)

> **사전 조건:** `ping 192.168.1.10` 성공 확인 (Network Setup 참고)

```bash
# 터미널 1: 백엔드 서비스 (Indy7 + Mark7 + RealSense + DataCollector)
ros2 launch pipet_bringup data_collection.launch.py \
  indy_ip:=192.168.1.10

# 터미널 2: 키보드 텔레옵 (TTY 필요)
ros2 run pipet_system_teleop system_teleop_node
```

**텔레옵 키 매핑 (D/d 외 대소문자 무관):**
| 키 | 동작 |
|----|------|
| SPACE | 녹화 시작/중지 (중지 시 Y/N으로 성공/실패 라벨링) |
| H | Indy7 홈 포지션 |
| D / d | 직접 교시 ON / OFF |
| G | Mark7 잡기 (Grasp) |
| O | Mark7 펴기 (Open) |
| P | Mark7 누르기 (Press) — 잡은 상태 유지하며 엄지만 누름 |
| R | Mark7 엄지 펴기 (Release) — 잡은 상태 유지하며 엄지만 펴기 |
| E | 에러 복구 + 교시 재개 |
| S | 상태 표시 |
| Q | 종료 |

**녹화 워크플로우:**
1. `D`로 직접 교시 ON
2. `SPACE`로 녹화 시작
3. 로봇 팔을 움직이며 G/O/P/R로 그리퍼 조작
4. `SPACE`로 녹화 중지 → `Y`(성공) 또는 `N`(실패) 입력
5. NPZ 저장 완료 후 경로 표시 (대용량이므로 저장에 시간이 걸릴 수 있음)

**데이터 수집 성능:** ~20Hz (5토픽 동기화), 640x480 원본 해상도, 에피소드당 ~1GB/분

### Indy7 단독 테스트

```bash
# 터미널 1
ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10

# 터미널 2
ros2 run pipet_system_teleop system_teleop_node
```

### Mark7 단독 테스트

```bash
# 터미널 1
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py

# 터미널 2
ros2 run pipet_hand_mark7_teleop mark7_keyboard_teleop
```

### Inference (추론/배포)

```bash
ros2 launch pipet_bringup inference.launch.py \
  indy_ip:=192.168.1.10 \
  model_path:=/path/to/model
```

## Architecture

### 계층 구조

```
오케스트레이터 레이어 (토픽/서비스 조합)
  pipet_data_collector    - 5토픽 동기화 + 그리퍼 캐시 → NPZ 저장
  pipet_system_teleop     - 키보드 → 모듈 서비스 호출
  pipet_inference         - 학습된 모델 → 자율 동작 (스텁)
    │
모듈 레이어 (장치별 토픽/서비스 노출)
  indy7_ros2              - /joint_states, indy_srv
  pipet_hand_mark7_driver - /gripper/status, /gripper/grasp|open|press|release
  realsense2_camera       - wrist_camera + overhead_camera (RGB/Depth)
```

### 패키지 구조

```
ros2_ws/src/
├── indy7_ros2/                   # Indy7 서브모듈 (5개 패키지)
│   ├── indy_driver/              #   로봇 드라이버 (IndyDCP3/gRPC)
│   ├── indy_interfaces/          #   커스텀 msg/srv
│   ├── indy_description/         #   URDF/xacro
│   ├── indy_gazebo/              #   Gazebo 시뮬
│   └── indy_moveit/              #   MoveIt2
├── mark7/                        # Mark7 패키지 (4개)
│   ├── pipet_hand_mark7_driver/  #   ros2_control 하드웨어 인터페이스
│   ├── pipet_hand_mark7_msgs/    #   커스텀 msg (GripperStatus, FingerState)
│   ├── pipet_hand_mark7_description/ # URDF/메시
│   └── pipet_hand_mark7_teleop/  #   단독 키보드 텔레옵
├── pipet_data_collector/         # 통합 데이터 수집 (5토픽 동기화 + 그리퍼 캐시, 2카메라)
├── pipet_system_teleop/          # 통합 텔레옵 (Indy7 + Mark7 + 녹화)
├── pipet_inference/              # 추론 노드 (스텁)
└── pipet_bringup/                # 통합 Launch 파일
```

### 주요 토픽/서비스

| 이름 | 타입 | 설명 |
|------|------|------|
| `/joint_states` | sensor_msgs/JointState | Indy7 관절 상태 (20Hz) |
| `/gripper/status` | GripperStatus | Mark7 손가락 상태 (~0.7Hz, 동기화 제외 캐시) |
| `/mark7/joint_states` | sensor_msgs/JointState | Mark7 관절 (rad) |
| `indy_srv` | IndyService | Indy7 명령 (홈, 교시, 복구 등) |
| `/gripper/grasp\|open\|press\|release` | std_srvs/Trigger | Mark7 프리셋 |
| `/wrist_camera/camera/color/image_raw` | sensor_msgs/Image | 손목 카메라 RGB |
| `/wrist_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 손목 카메라 Depth |
| `/overhead_camera/camera/color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 RGB |
| `/overhead_camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | 오버헤드 카메라 Depth |
| `/data_collector/start\|stop` | std_srvs/Trigger | 녹화 제어 |
| `/data_collector/is_recording` | std_msgs/Bool | 녹화 상태 |

### NPZ 저장 형식

| 키 | Shape | dtype |
|----|-------|-------|
| timestamps | (N,) | float64 |
| joint_positions | (N, 6) | float32 |
| joint_velocities | (N, 6) | float32 |
| joint_efforts | (N, 6) | float32 |
| wrist_rgb_images | (N, 480, 640, 3) | uint8 |
| wrist_depth_images | (N, 480, 640) | uint16 |
| overhead_rgb_images | (N, 480, 640, 3) | uint8 |
| overhead_depth_images | (N, 480, 640) | uint16 |
| gripper_actions | (N,) | int8 |
| success | () | bool |

**gripper_actions 값:** 0=hold, 1=grasp, 2=open, 3=press, 4=release

**파일명 형식:** `episode_YYYYMMDD_HHMMSS_success.npz` 또는 `episode_YYYYMMDD_HHMMSS_fail.npz`

**동기화 구조:** joint_states + wrist RGB/Depth + overhead RGB/Depth (5토픽)를 `ApproximateTimeSynchronizer`로 동기화. `/gripper/status`는 시리얼 통신 속도 제약(~0.7Hz)으로 동기화 제외, 최신값 캐시 방식.

## Dependencies

### System

```bash
sudo apt install ros-humble-rmw-cyclonedds-cpp ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gazebo-ros ros-humble-gazebo-ros2-control \
  ros-humble-rosidl-default-generators \
  ros-humble-cv-bridge ros-humble-image-transport \
  ros-humble-realsense2-camera
```

### Python

```bash
pip3 install neuromeka numpy opencv-python
```

## Submodule

`ros2_ws/src/indy7_ros2/`는 `neuromeka-robotics/indy-ros2` git 서브모듈.
로컬 커밋 `b4df14b` (direct teaching 지원)에 핀 고정.

```bash
# 서브모듈 초기화 (최초 1회)
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
git submodule update --init --recursive
```

## Hardware

| 장치 | 연결 | 주소 |
|------|------|------|
| Indy7 | 이더넷 | 192.168.1.10 |
| Mark7 RF 동글 | USB Serial | /dev/ttyACM0, 115200 bps |
| RealSense D435 (손목) | USB 3.0 | S/N: 844212071939 |
| RealSense D435 (오버헤드) | USB 3.0 | S/N: 317222074298 |

## Design Docs

- [docs/architecture.md](docs/architecture.md) — 전체 시스템 설계
- [docs/interface_spec.md](docs/interface_spec.md) — ROS2 인터페이스 명세
- [docs/mark7/architecture.md](docs/mark7/architecture.md) — Mark7 상세 설계
