# Pipet Physical AI

Indy7 로봇팔과 Mand.ro Mark7 로봇손을 이용해 파이펫(pipette)을 조작하는 Physical AI 프로젝트.

## 시스템 구성

- **로봇팔**: Neuromeka Indy7
- **로봇손**: Mand.ro Mark7
- **카메라**: Intel RealSense D435
- **OS / ROS**: Ubuntu 22.04 / ROS2 Humble

## 아키텍처

계층형 구조:
- **모듈 레이어**: Indy7, Mark7, RealSense — 각 장치를 토픽/서비스로 노출
- **오케스트레이터 레이어**: 데이터 수집, 텔레오프, 추론 — 모듈 인터페이스를 조합하여 동작

## 문서

| 문서 | 설명 |
|------|------|
| `docs/architecture.md` | 전체 시스템 설계 |
| `docs/interface_spec.md` | ROS2 노드 인터페이스 명세 |
| `docs/mark7/architecture.md` | Mark7 모듈 상세 설계 |

## 디렉터리 구조

```
ros2_ws/src/
  indy7_ros2/                      # Indy7 서브모듈 (드라이버, URDF, MoveIt, Gazebo)
  mark7/                           # Mark7 패키지
    pipet_hand_mark7_driver/       #   ros2_control 하드웨어 인터페이스
    pipet_hand_mark7_msgs/         #   커스텀 메시지
    pipet_hand_mark7_description/  #   URDF/메시
    pipet_hand_mark7_teleop/       #   단독 키보드 텔레옵
  indy7_gripper_teleop/            # Indy7 단독 직접 교시 + 데이터 수집
  pipet_data_collector/            # 통합 데이터 수집 (4토픽 동기화 → NPZ)
  pipet_system_teleop/             # 통합 텔레옵 (Indy7 + Mark7 + 녹화 제어)
  pipet_inference/                 # 추론 노드 (스텁)
  pipet_bringup/                   # 통합 Launch 파일
docs/                              # 설계 문서
```

## 빠른 시작

```bash
# 빌드
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build && source install/setup.bash

# 데이터 수집 (터미널 1: 백엔드, 터미널 2: 텔레옵)
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.100
ros2 run pipet_system_teleop system_teleop_node
```
