# CLAUDE.md

Claude Code용 프로젝트 가이드.

## Overview

Indy7 로봇팔 + Mand.ro Mark7 로봇손 + RealSense D435 카메라 2대를 이용한 Physical AI 피펫 조작 프로젝트.
**직접 교시 또는 키보드(movetelel)** 로 데이터 수집 → AI 학습 → 자율 동작 배포.

| 항목 | 값 |
|------|-----|
| ROS2 | Humble (Ubuntu 22.04) |
| DDS | Cyclone DDS (`export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`) |
| 로봇팔 | Indy7 — 이더넷 192.168.1.10 |
| 로봇손 | Mark7 — USB Serial /dev/ttyACM0 |
| 카메라 (손목) | RealSense D435, S/N 844212071939 |
| 카메라 (오버헤드) | RealSense D435, S/N 317222074298 |

---

## 1. 최초 1회 셋업

### 1-1. 서브모듈 + 의존성

```bash
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
git submodule update --init --recursive

sudo apt install ros-humble-rmw-cyclonedds-cpp ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gazebo-ros ros-humble-gazebo-ros2-control \
  ros-humble-rosidl-default-generators \
  ros-humble-cv-bridge ros-humble-image-transport \
  ros-humble-realsense2-camera

pip3 install neuromeka numpy opencv-python
```

### 1-2. 네트워크 (PC ↔ Indy7)

**방법 A — USB 이더넷 어댑터 직접 연결 (권장)**
```bash
sudo nmcli con mod enx00e04c360046 ipv4.addresses 192.168.1.100/24 ipv4.method manual
sudo nmcli con up enx00e04c360046
```

**방법 B — 공유기 경유 연결**
```bash
sudo nmcli con mod enp0s31f6 +ipv4.addresses 192.168.1.100/24
```

**확인:**
```bash
ping 192.168.1.10        # 응답 와야 함
nc -zv 192.168.1.10 20001  # gRPC 포트 OK여야 함
```

> ping 실패 시 → 로봇 컨트롤러 전원 / 케이블 / `ip addr show`에서 IP 할당 확인.
> gRPC 포트 실패 시 → 로봇 컨트롤러 재부팅 후 2~3분 대기.

---

## 2. 빌드

```bash
cd /home/sirlab/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build
source install/setup.bash
```

> 빌드 충돌 시: `rm -rf build install log` 후 다시 빌드.

---

## 3. 실행 — 데이터 수집

> **사전 조건:** `ping 192.168.1.10` 성공 + 로봇 IDLE 상태

### 터미널 1 — 백엔드 (필수)

```bash
cd ~/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
```

→ Indy7 + Mark7 + 카메라 2대 + 데이터 수집 노드 시작. **로봇은 가만히 있어야 정상.**

### 터미널 2 — 마스터 텔레옵 (필수, TTY)

```bash
cd ~/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 run pipet_system_teleop system_teleop_node
```

→ 모드 전환, 그리퍼 조작, 녹화 제어를 담당.

### 터미널 3 — 키보드 서보 (키보드 모드 사용 시만, TTY)

```bash
cd ~/Dev/ROS2/pipet-physical-ai
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

ros2 run pipet_system_teleop keyboard_servo_node
```

→ 키보드로 EE pose / joint를 직접 제어 (movetelel/movetelej).

---

## 4. 키 매핑

### 마스터 텔레옵 (터미널 2)

| 키 | 동작 |
|----|------|
| **1** | 직접 교시 모드 (Hand) — 손으로 로봇 잡고 움직임 |
| **2** | 키보드 모드 — 터미널 3에서 키보드 서보 사용 |
| **SPACE** | 녹화 시작/중지 (중지 시 `Y/N/X` — 성공/실패/폐기) |
| **D** / **d** | 직접 교시 ON / OFF (수동, 보통 1/2로 자동 처리됨) |
| **H** | Indy7 홈 포지션 |
| **G** / **O** / **P** / **R** | Mark7: Grasp / Open / Press / Release |
| **E** | 에러 복구 + 교시 재개 |
| **S** | 상태 표시 |
| **Q** | 종료 |

### 키보드 서보 (터미널 3, 키보드 모드 활성 시)

Neuromeka 표준 키 + 그리퍼.

**Cartesian (작업공간):**
| 키 | 동작 |
|----|------|
| ↑ / ↓ | x +/− (mm) |
| ← / → | y +/− (mm) |
| `.` / `;` | z +/− (mm) |
| N / M / `,` | rx / ry / rz 회전 (방향은 R) |

**조인트:**
| 키 | 동작 |
|----|------|
| 1 ~ 7 | 조인트 i 조그 (방향은 R) |

**기타:**
| 키 | 동작 |
|----|------|
| W / E | base / tool 좌표계 토글 |
| R | 조그 방향 토글 (+ ↔ −) |
| `−` / `+` | 조인트 step size 증감 |
| 9 / 0 | Cartesian step size 증감 |
| H / Z / S / P | Home / Zero / Recover / Stop teleop |
| **G / O / B / V** | 그리퍼 Grasp / Open / Press / Release |
| Q | 종료 |

> 키보드 노드에서는 **G/O/B/V**로 그리퍼 (P는 "Stop teleop"으로 사용 중이라 Press는 B로 매핑).

---

## 5. 워크플로우

### 직접 교시 (가장 안전, 권장 시작점)

1. 터미널 2에서 **`1`** → 직접 교시 ON
2. **`SPACE`** → 녹화 시작
3. 손으로 로봇 움직이며 **G / O / P / R** 로 그리퍼 조작
4. **`SPACE`** → **`Y`(성공)** / **`N`(실패)** / **`X`(폐기)**
5. NPZ 자동 저장 (대용량이라 수 초 걸림)

### 키보드 (movetelel 학습용)

1. 터미널 3 실행 (위 3번 명령)
2. 터미널 2에서 **`2`** → 키보드 모드 (직접 교시 자동 OFF)
3. **`SPACE`** → 녹화 시작
4. 터미널 3에서 화살표 / `.;` / `NM,` / `1-7` 등으로 로봇 조작
5. 터미널 2에서 **`SPACE`** → 라벨링

---

## 6. 단독 테스트

### Indy7 단독
```bash
ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10
ros2 run pipet_system_teleop system_teleop_node   # 다른 터미널
```

### Mark7 단독
```bash
ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py
ros2 run pipet_hand_mark7_teleop mark7_keyboard_teleop   # 다른 터미널
```

### 카메라 미리보기
```bash
realsense-viewer
```

---

## 7. 데이터 형식

### NPZ 저장 위치
```
episodes/
├── success/   # Y 입력 시
├── fail/      # N 입력 시
└── unlabeled/ # 라벨 미입력
```

파일명: `episode_YYYYMMDD_HHMMSS_<success|fail>.npz`

### NPZ 키

| 키 | Shape | dtype | 설명 |
|----|-------|-------|------|
| `timestamps` | (N,) | float64 | 녹화 시작 기준 상대 시간 (s) |
| `joint_positions` | (N, 6) | float32 | Indy7 관절 (rad) |
| `joint_velocities` | (N, 6) | float32 | Indy7 관절 속도 |
| `joint_efforts` | (N, 6) | float32 | Indy7 관절 토크 |
| `ee_poses` | (N, 6) | float32 | EE pose [x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg] (movetelel용) |
| `wrist_rgb_images` | (N, 480, 640, 3) | uint8 | 손목 카메라 RGB |
| `overhead_rgb_images` | (N, 480, 640, 3) | uint8 | 오버헤드 카메라 RGB |
| `gripper_actions` | (N,) | int8 | 0=hold 1=grasp 2=open 3=press 4=release |
| `success` | () | bool | 에피소드 성공 여부 |

> Depth는 수집하지 않음. 동기화: joint_states + wrist RGB + overhead RGB (3토픽). gripper_status / ee_pose는 캐시 방식.

---

## 8. 트러블슈팅

| 증상 | 원인/해결 |
|------|-----------|
| launch 직후 로봇이 멋대로 움직임 | 좀비 노드. `killall -9 ros2 python3 ros2_control_node` 후 재실행 |
| `Failed to enter TELE_OP state` | 로봇이 TEACHING/VIOLATE 상태. `E` 또는 `S`(키보드)로 복구 |
| `Failed to stop recording` | 큰 NPZ 저장 중 timeout — 실제 저장은 성공한 경우 많음. `episodes/` 확인 |
| `No data collected` | 카메라 토픽 미발행. wrist/overhead 카메라 USB 연결 확인 |
| 키 입력 안 먹힘 | 터미널 2/3에 포커스 두고 입력. TTY 필요 |
| ping 실패 | 로봇 전원 / 케이블 / `nc -zv 192.168.1.10 20001` |

---

## 9. 패키지 구조

```
ros2_ws/src/
├── indy7_ros2/                       # Indy7 서브모듈 (5개)
│   ├── indy_driver/                  #   gRPC 드라이버 (IndyDCP3)
│   ├── indy_interfaces/              #   IndyService.srv 등
│   ├── indy_description/             #   URDF
│   ├── indy_gazebo/                  #   (미사용)
│   └── indy_moveit/                  #   (미사용)
├── mark7/                            # Mark7 (4개)
│   ├── pipet_hand_mark7_driver/
│   ├── pipet_hand_mark7_msgs/
│   ├── pipet_hand_mark7_description/
│   └── pipet_hand_mark7_teleop/      #   그리퍼 프리셋 노드 등
├── pipet_data_collector/             # 3토픽 동기화 + EE pose/그리퍼 캐시 → NPZ
├── pipet_system_teleop/              # system_teleop_node + keyboard_servo_node
├── pipet_inference/                  # 추론 노드 (스텁)
└── pipet_bringup/                    # 통합 launch
```

### 주요 토픽/서비스

| 이름 | 타입 | 비고 |
|------|------|------|
| `/joint_states` | JointState | Indy7 관절 (20Hz) |
| `/indy/ee_pose` | Float64MultiArray | EE 현재 pose (20Hz) |
| `/indy/teleop_pose` | Float64MultiArray | EE 목표 pose → `movetelel_abs` |
| `/indy/teleop_joint` | Float64MultiArray | 관절 목표 → `movetelej_abs` (키보드 1~7) |
| `indy_srv` | IndyService | 홈/교시/복구/teleop 정지 등 |
| `/gripper/status` | GripperStatus | Mark7 손가락 상태 (~0.7Hz) |
| `/gripper/grasp\|open\|press\|release` | Trigger | Mark7 프리셋 |
| `/wrist_camera/camera/color/image_raw` | Image | 손목 RGB |
| `/overhead_camera/camera/color/image_raw` | Image | 오버헤드 RGB |
| `/data_collector/start\|stop\|discard\|mark_success\|mark_fail` | Trigger | 녹화 제어 |
| `/data_collector/log_grasp\|open\|press\|release` | Trigger | 그리퍼 액션 로깅 |

---

## 10. 참고 문서

- [README.md](README.md) — 사용자용 README (실행 흐름)
- [docs/architecture.md](docs/architecture.md) — 시스템 설계
- [docs/interface_spec.md](docs/interface_spec.md) — ROS2 인터페이스 명세
- [docs/mark7/architecture.md](docs/mark7/architecture.md) — Mark7 상세 설계
