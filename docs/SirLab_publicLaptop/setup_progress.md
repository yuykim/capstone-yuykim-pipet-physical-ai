- 작성자 : 김유영
- 작성 날짜 : 26.03.20

````markdown
# 환경 세팅 가이드

## 1. 개요
이 문서는 현재 노트북에서 프로젝트 개발 환경을 설정한 과정과,
설치 중 발생했던 문제 및 해결 방법을 기록한 문서이다.

- 노트북: ASUS ROG Strix G17 G713RS
- 운영체제: Ubuntu 22.04.5 LTS
- 커널: 6.8.0-106-generic
- ROS 2: Humble
- GPU: NVIDIA GeForce RTX 3080 Laptop GPU
- CUDA: 13.0

---

## 2. 초기 환경 확인

기본 시스템 정보를 확인하기 위해 아래 명령어들을 사용하였다.

```bash
lsb_release -a
cat /etc/os-release
uname -r
echo $ROS_DISTRO
free -h
lscpu
nvidia-smi
nvcc --version
lsblk
````

확인한 주요 정보는 다음과 같다.

* Ubuntu 22.04.5 LTS
* Kernel 6.8.0-106-generic
* ROS 2 Humble
* AMD Ryzen 9 6900HX
* RAM 14 GiB
* NVIDIA GeForce RTX 3080 Laptop GPU
* CUDA Toolkit 13.0

---

## 3. NVIDIA 드라이버 설치 과정

### 3.1 문제 상황

NVIDIA 드라이버 설치 중 DKMS 빌드 오류가 발생하였다.

주요 증상:

* `nvidia-dkms-580-open` 설치 실패
* `nvidia-driver-580-open` 설정 실패
* 커널 모듈 빌드 중 에러 발생

### 3.2 원인

현재 사용 중인 커널은 **GCC 12.3.0** 으로 빌드되어 있었는데,
시스템 기본 컴파일러는 **GCC 11.4.0** 으로 설정되어 있었다.

즉,

* 커널 빌드 컴파일러: GCC 12
* 현재 시스템 기본 컴파일러: GCC 11

이 컴파일러 버전 불일치 때문에 NVIDIA DKMS 모듈 빌드가 실패하였다.

### 3.3 해결 방법

GCC 12를 설치하고, 시스템 기본 `gcc` / `cc`를 GCC 12로 변경하였다.

```bash
sudo apt install gcc-12 g++-12

sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110 || true
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 120
sudo update-alternatives --set gcc /usr/bin/gcc-12

sudo update-alternatives --install /usr/bin/cc cc /usr/bin/gcc-11 110 || true
sudo update-alternatives --install /usr/bin/cc cc /usr/bin/gcc-12 120
sudo update-alternatives --set cc /usr/bin/gcc-12
```

### 3.4 결과

컴파일러를 GCC 12로 맞춘 뒤 NVIDIA DKMS 모듈이 정상적으로 빌드되었고,
드라이버 설치도 성공적으로 완료되었다.

확인 명령어:

```bash
gcc --version
cc --version
nvidia-smi
nvcc --version
```

---

## 4. 최종 확인 결과

### 4.1 드라이버 확인

```bash
nvidia-smi
```

확인 결과:

* NVIDIA Driver Version: 580.95.05
* CUDA Version: 13.0
* GPU 정상 인식
* NVIDIA 커널 모듈 정상 로드

### 4.2 CUDA 확인

```bash
nvcc --version
```

확인 결과:

* CUDA compilation tools, release 13.0
* nvcc V13.0.88

---

## 5. 현재 개발 환경

| 항목            | 내용                                 |
| ------------- | ---------------------------------- |
| 운영체제          | Ubuntu 22.04.5 LTS                 |
| 커널            | 6.8.0-106-generic                  |
| ROS 2         | Humble                             |
| CPU           | AMD Ryzen 9 6900HX                 |
| RAM           | 14 GiB                             |
| GPU           | NVIDIA GeForce RTX 3080 Laptop GPU |
| NVIDIA Driver | 580.95.05                          |
| CUDA Toolkit  | 13.0                               |
| RMW           | rmw_cyclonedds_cpp                 |

---

## 6. 참고 사항

* ROS 2는 `/opt/ros/humble` 경로에 설치되어 있다.
* 현재 ROS 2 미들웨어는 `rmw_cyclonedds_cpp`를 사용 중이다.
* NVIDIA 드라이버 설치 문제는 커널과 컴파일러 버전 불일치로 인해 발생했다.
* 동일한 문제 발생 시, 커널을 빌드한 GCC 버전과 현재 시스템 기본 GCC 버전을 먼저 확인해야 한다.

---

## 7. 자주 사용하는 확인 명령어

```bash
# OS / Kernel
lsb_release -a
uname -r

# ROS 2
echo $ROS_DISTRO
ros2 doctor --report

# GPU / CUDA
nvidia-smi
nvcc --version

# CPU / Memory / Storage
lscpu
free -h
lsblk
```