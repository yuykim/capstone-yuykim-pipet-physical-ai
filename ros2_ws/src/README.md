# Pipet Physical AI

Indy7 로봇팔 + Mand.ro Mark7 로봇손 + RealSense D435 카메라 2대를 이용한 Physical AI 피펫 조작 프로젝트.
직접 교시로 데이터 수집 → AI 학습 → 자율 동작 배포.

## 시스템 구성

| 항목 | 내용 |
|------|------|
| 로봇팔 | Neuromeka Indy7 (이더넷, 192.168.1.10) |
| 로봇손 | Mand.ro Mark7 (USB Serial, /dev/ttyACM0) |
| 카메라 (손목) | Intel RealSense D435 (S/N: 844212071939) |
| 카메라 (오버헤드) | Intel RealSense D435 (S/N: 317222074298) |
| OS / ROS | Ubuntu 22.04 / ROS2 Humble |
| DDS | Cyclone DDS |

---

## 빠른 시작

### 0. 네트워크 설정 (최초 1회)

Indy7은 USB 이더넷 어댑터(`enx00e04c360046`)를 통해 연결된다. PC에 고정 IP를 설정해야 로봇과 통신할 수 있다.

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

> **sirlab public laptop 네트워크 설정 메모 (이번에 성공한 방법)**
>
> 로봇 이더넷 인터페이스는 `enx00e04c360046` 였지만, `nmcli con mod enx00e04c360046 ...` 는 “unknown connection” 오류가 났습니다.
> 원인은 `nmcli con mod`가 받는 값이 “인터페이스 이름(ifname)”이 아니라 “NetworkManager connection name”이기 때문입니다.
>
> 그래서 기존 connection을 수정하기보다, 해당 인터페이스에 새 connection을 만들어 고정 IP를 할당했습니다.
>
> ```bash
> # (1) connection 생성: con-name은 아무 이름으로 해도 되지만, 여기서는 indy7-static으로 지정
> sudo nmcli con add type ethernet ifname enx00e04c360046 con-name indy7-static \
>   ipv4.addresses 192.168.1.100/24 ipv4.method manual \
>   ipv6.method ignore autoconnect yes
>
> # (2) 연결 적용
> sudo nmcli con up indy7-static
>
> # (3) IPv4 확인
> ip addr show enx00e04c360046 | grep inet
> # -> inet 192.168.1.100/24 가 보여야 함
>
> # (4) 로봇 통신 확인
> ping 192.168.1.10
> ```

### 1. 의존성 설치

```bash
# ROS2 패키지
sudo apt install ros-humble-rmw-cyclonedds-cpp ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gazebo-ros ros-humble-gazebo-ros2-control \
  ros-humble-rosidl-default-generators \
  ros-humble-cv-bridge ros-humble-image-transport \
  ros-humble-realsense2-camera

# Python
pip3 install neuromeka numpy opencv-python

# 서브모듈 초기화 (최초 1회)
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
git submodule update --init --recursive
```

### 2. 빌드

```bash
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build
source install/setup.bash
```

### 3. 데이터 수집 (전체 시스템)

> **사전 조건:** `ping 192.168.1.10` 성공 확인

```bash
# 터미널 1: 백엔드 서비스 (Indy7 + Mark7 + RealSense 2대 + DataCollector)
cd ~/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10

# 터미널 2: 키보드 텔레옵
cd ~/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
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

**데이터 수집 성능:** ~20Hz, 640x480 원본 해상도, 에피소드당 ~1GB/분

---

## 단독 테스트

### Indy7 단독

```bash
# 터미널 1
ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10

# 터미널 2
ros2 run pipet_system_teleop system_teleop_node
```

### Mark7 단독

```bash
# 터미널 1
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py

# 터미널 2
ros2 run pipet_hand_mark7_teleop mark7_keyboard_teleop
```

### Mark7 가상 모드 (하드웨어 없이)

```bash
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py use_mock_hardware:=true use_rviz:=true
```

---

## 저장 데이터 형식 (NPZ)

파일명: `episodes/episode_YYYYMMDD_HHMMSS_success.npz` 또는 `_fail.npz`

| 키 | Shape | dtype | 설명 |
|----|-------|-------|------|
| timestamps | (N,) | float64 | 녹화 시작 기준 상대 시간 |
| joint_positions | (N, 6) | float32 | Indy7 관절 각도 (rad) |
| joint_velocities | (N, 6) | float32 | Indy7 관절 속도 (rad/s) |
| joint_efforts | (N, 6) | float32 | Indy7 관절 토크 (N·m) |
| wrist_rgb_images | (N, 480, 640, 3) | uint8 | 손목 카메라 RGB |
| wrist_depth_images | (N, 480, 640) | uint16 | 손목 카메라 Depth (mm) |
| overhead_rgb_images | (N, 480, 640, 3) | uint8 | 오버헤드 카메라 RGB |
| overhead_depth_images | (N, 480, 640) | uint16 | 오버헤드 카메라 Depth (mm) |
| gripper_actions | (N,) | int8 | 0=유지, 1=잡기, 2=펴기, 3=누르기, 4=엄지 펴기 |
| success | () | bool | 에피소드 성공 여부 |

---

## 디렉토리 구조

```
ros2_ws/src/
├── indy7_ros2/                       # Indy7 서브모듈 (5개 패키지)
│   ├── indy_driver/                  #   로봇 드라이버 (IndyDCP3/gRPC)
│   ├── indy_interfaces/              #   커스텀 msg/srv
│   ├── indy_description/             #   URDF/xacro
│   ├── indy_gazebo/                  #   Gazebo 시뮬
│   └── indy_moveit/                  #   MoveIt2
├── mark7/                            # Mark7 패키지 (4개)
│   ├── pipet_hand_mark7_driver/      #   ros2_control 하드웨어 인터페이스
│   ├── pipet_hand_mark7_msgs/        #   커스텀 msg (GripperStatus, FingerState)
│   ├── pipet_hand_mark7_description/ #   URDF/메시
│   └── pipet_hand_mark7_teleop/      #   단독 키보드 텔레옵
├── pipet_data_collector/             # 통합 데이터 수집 (5토픽 동기화 + 그리퍼 캐시)
├── pipet_system_teleop/              # 통합 텔레옵 (Indy7 + Mark7 + 녹화)
├── pipet_inference/                  # 추론 노드 (스텁)
└── pipet_bringup/                    # 통합 Launch 파일
```

---

## 문서

| 문서 | 설명 |
|------|------|
| [docs/architecture.md](docs/architecture.md) | 전체 시스템 설계 및 데이터 흐름 |
| [docs/interface_spec.md](docs/interface_spec.md) | ROS2 토픽/서비스 인터페이스 명세 |
| [docs/ai_architecture.md](docs/ai_architecture.md) | AI 학습/추론 설계 (관측·행동 공간, 모델 구조) |
| [docs/mark7/architecture.md](docs/mark7/architecture.md) | Mark7 모듈 상세 설계 및 통신 프로토콜 |