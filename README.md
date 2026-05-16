# Pipet Physical AI (ROS2 + AI)

Indy7 로봇팔 + Mark7 로봇손 + RealSense D435 카메라 2대로 피펫 조작을 학습/배포하는 Physical AI 프로젝트.

```
직접교시 또는 키보드(movetelel) 수집  →  NPZ 저장
   →  LeRobotDataset 변환  →  ACT 등 학습  →  실제 로봇 추론
```

| 항목 | 내용 |
|------|------|
| 로봇팔 | Neuromeka Indy7 (이더넷, 192.168.1.10) |
| 로봇손 | Mand.ro Mark7 (USB Serial, /dev/ttyACM0) |
| 카메라 | RealSense D435 × 2 (wrist S/N 844212071939, overhead S/N 317222074298) |
| OS / ROS | Ubuntu 22.04 / ROS2 Humble + Cyclone DDS |

---

## 1. 최초 1회 셋업

### 1-1. 의존성 설치

```bash
cd <repo_root>

sudo apt install ros-humble-rmw-cyclonedds-cpp ros-humble-moveit \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-realsense2-camera ros-humble-cv-bridge \
  ros-humble-image-transport ros-humble-rosidl-default-generators

pip3 install neuromeka numpy opencv-python pygame
```

### 1-2. 네트워크 설정 (PC ↔ Indy7)

Indy7(`192.168.1.10`)과 통신하려면 PC에 같은 대역 IP를 설정해야 합니다.

**방법 A — USB 이더넷 어댑터 직접 연결 (권장)**
```bash
sudo nmcli con mod enx00e04c360046 ipv4.addresses 192.168.1.100/24 ipv4.method manual
sudo nmcli con up enx00e04c360046
ping 192.168.1.10   # 응답 와야 함
```
> `unknown connection` 오류 → 새 connection 생성:
> ```bash
> sudo nmcli con add type ethernet ifname enx00e04c360046 con-name indy7-static \
>   ipv4.addresses 192.168.1.100/24 ipv4.method manual ipv6.method ignore autoconnect yes
> sudo nmcli con up indy7-static
> ```

**방법 B — 공유기 경유 (PC 내장 이더넷 사용)**
```bash
sudo nmcli con mod enp0s31f6 +ipv4.addresses 192.168.1.100/24
ping 192.168.1.10
```

> ping 실패 → 로봇 컨트롤러 전원 / 이더넷 케이블 / `ip addr show` 확인.
> gRPC 실패 (`nc -zv 192.168.1.10 20001`) → 로봇 재부팅 후 2~3분 대기.

### 1-3. 빌드

```bash
cd <repo_root>
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build
source install/setup.bash
```

> 충돌 시 `rm -rf build install log` 후 재빌드.

---

## 2. 데이터 수집 실행

### 사전 점검
```bash
ping 192.168.1.10                # 로봇 응답 확인
rs-enumerate-devices | grep "Serial Number"   # 카메라 2대 확인
```

### 터미널 1 — 백엔드 (필수)

```bash
cd <repo_root>
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
```

→ Indy7 + Mark7 + 카메라 2대 + 데이터 수집 노드 시작. **로봇은 가만히 있어야 정상.**

### 터미널 2 — 키보드 텔레옵 / 녹화 제어 (키보드 수집)

```bash
cd <repo_root>
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 run pipet_system_teleop keyboard_servo_node
```

→ Pygame 창에서 Indy7 상대 텔레옵, Mark7 그리퍼, 녹화 시작/중지/라벨링을 모두 제어.

### 카메라 노드 확인
```bash
conda deactivate
source /opt/ros/humble/setup.bash
source ~/2026capstone2_ws/pipet-physical-ai/ros2_ws/install/setup.bash
ros2 run rqt_image_view rqt_image_view /wrist_camera/camera/color/image_raw
```

### 터미널 3 — 마스터 텔레옵 (직접 교시 사용 시만, TTY)

```bash
cd <repo_root>
source /opt/ros/humble/setup.bash && source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 run pipet_system_teleop system_teleop_node
```

→ 직접 교시 모드 전환, 그리퍼, 녹화 제어.

---

## 3. 키 매핑

### 마스터 텔레옵 (터미널 2)

| 키 | 동작 |
|---|---|
| **1** | 직접 교시 모드 (Hand) |
| **2** | 키보드 모드 (직접 교시 자동 OFF) |
| **SPACE** | 녹화 시작/중지 (중지 시 `Y/N/X` — 성공/실패/폐기) |
| **D** / **d** | 직접 교시 ON / OFF (수동) |
| **H** | Indy7 홈 |
| **G/O/P/R** | Mark7 Grasp / Open / Press / Release |
| **E** | 에러 복구 + 교시 재개 |
| **S** | 상태 표시 |
| **Q** | 종료 |

### 키보드 텔레옵 (Pygame 창)

| 키 | 동작 |
|---|---|
| W / S | x +/− |
| A / D | y +/− |
| Q / E | z +/− |
| U / O | rx +/− |
| I / K | ry +/− |
| J / L | rz +/− |
| `[` / `]` | Cartesian step 감소/증가 |
| H / Z / Ctrl+S / P | Home / Zero / Recover / Stop teleop |
| G / F / B / V | Grasp / Open / Press / Release |
| SPACE | 녹화 시작, 녹화 중이면 라벨 입력 대기 |
| Y / N / X | 성공 저장 / 실패 저장 / 폐기 |
| ESC | 종료 |

---

## 4. 워크플로우

### 직접 교시 (가장 안전, 권장 시작점)

1. 터미널 2에서 **`1`** → 직접 교시 ON
2. **`SPACE`** → 녹화 시작
3. 손으로 로봇 움직이기 + **G/O/P/R** 그리퍼
4. **`SPACE`** → **`Y`(성공) / `N`(실패) / `X`(폐기)**

### 키보드 (movetelel 학습용)

1. 터미널 2에서 `keyboard_servo_node` 실행
2. Pygame 창을 활성화
3. **`SPACE`** → 녹화 시작
4. W/S/A/D/Q/E/U/O/I/K/J/L로 Indy7 조작 + G/F/B/V로 그리퍼 조작
5. **`SPACE`** → **`Y`(성공) / `N`(실패) / `X`(폐기)**

---

## 5. 데이터 형식 (NPZ)

저장 위치: `episodes/<success|fail|unlabeled>/episode_YYYYMMDD_HHMMSS_<label>.npz`

| 키 | Shape | 설명 |
|---|---|---|
| `timestamps` | (N,) | 녹화 시작 기준 상대 시간 |
| `joint_positions/velocities/efforts` | (N, 6) | Indy7 관절 (rad) |
| `ee_poses` | (N, 6) | EE pose `[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]` (movetelel용) |
| `wrist_rgb_images` | (N, 480, 640, 3) | 손목 카메라 RGB |
| `overhead_rgb_images` | (N, 480, 640, 3) | 오버헤드 카메라 RGB |
| `gripper_actions` | (N,) | 0=hold 1=grasp 2=open 3=press 4=release |
| `success` | () | True/False |

> Depth는 수집 안 함. 동기화: joint + wrist RGB + overhead RGB (3토픽). gripper/ee_pose는 캐시.

---

## 6. 학습 (LeRobot)

### 6-1. NPZ → LeRobotDataset 변환

```bash
python ai/data_conversion/npz_to_lerobot/convert.py \
  --episodes_dir <episodes_dir> \
  --output_dir <lerobot_dataset_dir> \
  --output_repo_id pipet_dataset \
  --fps 15 \
  --task "Pick up the pipette" \
  --camera wrist \
  --action_space cartesian
```

- `--camera`: `wrist` | `overhead` | `both`
- `--action_space`: `cartesian` (movetelel) | `joint` (movetelej)

### 6-2. ACT baseline 학습

```bash
python ai/lerobot/run_lerobot_train.py \
  --episodes_dir <episodes_dir> \
  --dataset_output_dir <lerobot_dataset_dir> \
  --dataset_repo_id pipet_dataset \
  --output_dir outputs/train/act_pipet \
  --device cuda
```

`--skip_convert` 옵션으로 변환 건너뛰고 학습만 수행 가능.

---

## 7. 추론 (실제 로봇 배포)

```bash
ros2 launch pipet_bringup inference.launch.py \
  indy_ip:=192.168.1.10 \
  model_path:=<trained_policy_dir>
```

추론 노드는 모델 출력을 `/indy/teleop_pose`로 발행 → Indy7이 `movetelel_abs`로 실행.

---

## 8. 단독 테스트

| 대상 | 명령 |
|------|------|
| Indy7만 | `ros2 launch pipet_bringup indy7_only.launch.py indy_ip:=192.168.1.10` |
| Mark7만 | `ros2 launch pipet_hand_mark7_driver mark7_hardware.launch.py` |
| 카메라만 | `realsense-viewer` |

---

## 9. 트러블슈팅

| 증상 | 해결 |
|------|------|
| launch 직후 로봇이 멋대로 움직임 | 좀비 노드. `killall -9 ros2 python3 ros2_control_node` 후 재실행 |
| `Failed to enter TELE_OP state` | 로봇이 TEACHING/VIOLATE 상태. 마스터 노드의 `E`(복구) 또는 비상정지 풀기 |
| `Failed to stop recording` | NPZ 저장 timeout — 실제로는 저장된 경우 많음. `episodes/` 확인 |
| `No data collected` | 카메라 토픽 미발행. wrist/overhead USB 연결 확인 |
| ping 실패 | 로봇 전원 / 케이블 / IP 할당 확인 |
| 키 입력 안 먹힘 | 터미널 2/3 창에 포커스 두고 입력 (TTY 필요) |
| 빌드 충돌 / 좀비 install | `rm -rf build install log` 후 재빌드 |

---

## 10. 가상환경 리플레이 (시뮬 검증)

`pipet_inference/virtual_episode_replay_node.py` — 기존 NPZ를 재생해서 토픽 계약 검증.

```bash
ros2 run pipet_inference virtual_episode_replay_node \
  --ros-args -p episode_npz_path:=<episode_npz_path> -p auto_record:=true
```

---

## 11. 파일 구조

```
pipet-physical-ai/
├── README.md                           # 이 파일
├── CLAUDE.md                           # Claude Code용 가이드
├── docs/
│   ├── architecture.md
│   ├── interface_spec.md
│   ├── mark7/architecture.md
│   └── ai/
│      ├── ai_architecture.md
│      └── lerobot_architecture.md
├── ai/
│   ├── data_conversion/npz_to_lerobot/convert.py
│   ├── lerobot/run_lerobot_train.py
│   └── lerobot_source/lerobot/
└── ros2_ws/src/
    ├── indy7_ros2/                     # Indy7 서브모듈
    ├── mark7/                          # Mark7 패키지들
    ├── pipet_data_collector/
    ├── pipet_system_teleop/            # system + keyboard_servo nodes
    ├── pipet_inference/
    └── pipet_bringup/                  # 통합 launch
```

---

## 12. 추가 문서

- [docs/architecture.md](docs/architecture.md) — 전체 시스템 설계
- [docs/interface_spec.md](docs/interface_spec.md) — ROS2 인터페이스 명세
- [docs/ai/ai_architecture.md](docs/ai/ai_architecture.md) — AI 학습 전략
- [docs/ai/lerobot_architecture.md](docs/ai/lerobot_architecture.md) — LeRobot 매핑
- [docs/mark7/architecture.md](docs/mark7/architecture.md) — Mark7 상세 설계
- [ai/README.md](ai/README.md) — AI 폴더 가이드
