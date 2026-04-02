https://prod.danawa.com/info/?pcode=16804667

# Development Environment

## System Information

| Item | Specification |
|---|---|
| OS | Ubuntu 22.04.5 LTS (Jammy Jellyfish) |
| Kernel | 6.8.0-106-generic |
| Architecture | x86_64 |
| CPU | AMD Ryzen 9 6900HX with Radeon Graphics |
| Cores / Threads | 8 Cores / 16 Threads |
| RAM | 14 GiB |
| Swap | 2.0 GiB |
| GPU | NVIDIA GeForce RTX 3080 Laptop GPU |
| VRAM | 8 GiB |
| NVIDIA Driver | 580.95.05 |
| CUDA Driver Version | 13.0 |
| CUDA Toolkit | 13.0 (nvcc V13.0.88) |
| Storage | NVMe SSD 953.9 GiB |
| Root Partition | 97.7 GiB (`/`) |

## ROS 2 Environment

| Item | Specification |
|---|---|
| ROS 2 Distribution | Humble |
| ROS Installation Path | `/opt/ros/humble` |
| RMW Middleware | `rmw_cyclonedds_cpp` |

## Hardware Summary

- **CPU**: AMD Ryzen 9 6900HX with Radeon Graphics  
- **GPU**: NVIDIA GeForce RTX 3080 Laptop GPU (8 GB VRAM)  
- **Memory**: 14 GiB RAM  
- **Storage**: 953.9 GiB NVMe SSD  

## Software Summary

- **Operating System**: Ubuntu 22.04.5 LTS  
- **Kernel Version**: 6.8.0-106-generic  
- **ROS 2 Version**: Humble  
- **CUDA Toolkit**: 13.0  
- **NVIDIA Driver**: 580.95.05  

## Verification Commands

```bash
# OS
lsb_release -a
cat /etc/os-release
uname -r

# ROS 2
echo $ROS_DISTRO
ls /opt/ros
ros2 doctor --report

# Memory
free -h

# GPU / Driver
nvidia-smi

# CUDA
nvcc --version

# CPU
lscpu

# Storage
lsblk

---

```markdown
## Environment Overview

This project was developed and tested on the following environment:

- Ubuntu 22.04.5 LTS
- ROS 2 Humble
- AMD Ryzen 9 6900HX
- NVIDIA GeForce RTX 3080 Laptop GPU
- CUDA 13.0
```

---

## 현재 Python / 패키지 환경 (ROS 빌드 기준)

### 파이썬 경로 및 버전
- 기본 `python3` (현재 쉘에서 호출되는 경로): `/home/sirlab-pwd-0000/miniconda3/bin/python3` / `Python 3.13.12`
- 시스템 `python3.10`: `/usr/bin/python3.10` / `Python 3.10.12`

### ROS2 Humble 빌드 성공에 필요한 파이썬 패키지(현재 확인된 버전)
아래 패키지들은 `colcon build` 중 `rosidl_*` 단계에서 필요한 모듈들이며, **빌드 로그에 찍히는 파이썬 경로**에 맞춰 설치해야 합니다.

- `catkin_pkg` `1.1.0`
  - 설치 위치: `/home/sirlab-pwd-0000/.local/lib/python3.13/site-packages`
- `empy`(import는 `em`) `3.3.4`
  - 설치 위치: `/home/sirlab-pwd-0000/.local/lib/python3.13/site-packages`
  - 참고: ROS2 Humble은 `em.BUFFERED_OPT`를 기대하는데, `empy==4.x`에서는 해당 속성이 달라 빌드가 실패할 수 있음
- `numpy` `2.4.4`
  - 설치 위치: `/home/sirlab-pwd-0000/.local/lib/python3.13/site-packages`
- `lark-parser` `0.12.0`
  - 설치 위치: `/home/sirlab-pwd-0000/miniconda3/lib/python3.13/site-packages`

### 현재 환경에서 확인한 빌드 의존 파이썬(중요)
- `colcon build` 중 에러 로그에서 종종 `/home/sirlab-pwd-0000/miniconda3/bin/python3` 가 호출됨
- 따라서 위 패키지들은 최소한 **해당 파이썬 경로**에서 import 가능해야 함

---

## ROS2 / 네트워크 설정 현황

### Indy7(로봇) 고정 IP 설정 성공
- 인터페이스: `enx00e04c360046`
- PC 고정 IP: `192.168.1.100/24`
- 테스트: `ping 192.168.1.10` 성공

메모:
- 처음엔 `nmcli con mod enx00e04c360046 ...` 형태로 시도했지만 `unknown connection` 오류가 났음
- `nmcli con mod`는 **인터페이스명(ifname)이 아니라 connection name**을 대상으로 하므로,
  `nmcli con add type ethernet ifname enx00e04c360046 con-name indy7-static ...`로 connection을 새로 만들어 고정 IP를 적용했음

---

## 문서화/검증용 자주 쓰는 명령
```bash
echo $ROS_DISTRO
echo $RMW_IMPLEMENTATION

python3 --version
/home/sirlab-pwd-0000/miniconda3/bin/python3 --version

python3 -c "import catkin_pkg, em, numpy, lark; print('pydeps ok')"

ip addr show enx00e04c360046 | grep inet
ping -c 2 192.168.1.10
```