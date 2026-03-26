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