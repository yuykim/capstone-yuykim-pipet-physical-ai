
> [LeRobot 공식 페이지](https://huggingface.co/docs/lerobot/en/index)  
> [LeRobot 설치 방법](https://huggingface.co/docs/lerobot/en/installation)  
> [LeRobotDataset v3.0 관련 문서](/docs/ai/lerobot_architecture.md)

## 참고사항

- **설치 날짜**: 2026.03.20
- **LeRobot 버전**: 0.5.1
- 현재 LeRobot 소스는 프로젝트 내부에 직접 포함되어 있어 자동 업데이트되지 않습니다.
- 향후 상위 버전의 LeRobot을 반영할 경우, 수동으로 변경 사항을 확인하고 필요한 수정 작업을 진행해야 합니다.

## LeRobot 설치

### Linux 환경을 사용한 이유

Windows 환경에서는 Conda로 `ffmpeg`를 설치하는 과정에서  
`gdk-pixbuf` 및 `UnicodeDecodeError('cp949', ...)` 관련 오류가 발생하였다.  
따라서 LeRobot는 Ubuntu Linux 환경에서 설치하였다.

---

### 1. Conda 가상환경 생성

Python 3.12 기반의 새로운 Conda 가상환경을 생성한다.

```bash
conda create -y -n lerobot python=3.12 --override-channels -c conda-forge
conda activate lerobot
````

생성 후 Python 버전을 확인한다.

```bash
python --version
```

---

### 2. FFmpeg 및 evdev 설치

LeRobot는 비디오 데이터 처리를 위해 `ffmpeg`가 필요하며,
입력 장치 관련 의존성을 위해 `evdev`도 함께 설치하였다.

```bash
conda install -y ffmpeg=7.1.1 evdev --override-channels -c conda-forge
```

설치가 정상적으로 완료되었는지 확인한다.

```bash
ffmpeg -version
```

---

### 3. LeRobot 소스 코드 배치

LeRobot는 프로젝트 메인 리포지토리 하위 경로에 직접 배치하였다.

```text
pipet-physical-ai/ai/lerobot/lerobot
```

초기에는 별도 Git 리포지토리 형태로 clone한 뒤,
메인 프로젝트에서 직접 관리할 수 있도록 내부 `.git` 디렉토리를 제거하였다.

---

### 4. LeRobot 설치

프로젝트 내부에 포함된 LeRobot 소스 경로에서 `editable` 모드로 설치한다.

```bash
cd ~/2026capstone2_ws/pipet-physical-ai/ai/lerobot/lerobot
pip install -e .
```

---

### 5. 설치 확인

아래 명령어를 실행하여 LeRobot가 정상적으로 설치되었는지 확인한다.

```bash
python -c "import lerobot; print('lerobot import ok')"
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
```

필요하면 설치된 패키지 버전도 확인할 수 있다.

```bash
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
```

---

### 6. 전체 설치 명령어

```bash
conda create -y -n lerobot python=3.12 --override-channels -c conda-forge
conda activate lerobot

conda install -y ffmpeg=7.1.1 evdev --override-channels -c conda-forge

cd ~/2026capstone2_ws/pipet-physical-ai/ai/lerobot/lerobot
pip install -e .

ffmpeg -version
python --version
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
python -c "import lerobot; print('lerobot import ok')"
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
```

---

## 설치 확인 환경

현재 확인된 환경은 다음과 같다.

* LeRobot `0.5.1`
* FFmpeg `7.1.1`
* Python `3.12.13`
* PyTorch `2.10.0+cu128`
* CUDA 사용 가능
* GPU: `NVIDIA GeForce RTX 3080 Laptop GPU`
* `lerobot import ok` 확인 완료

## 출력 예시

```bash
(lerobot) sirlab-pwd-0000@sirlabpwd0000-ROG-Strix-G713RS-G713RS:~/2026capstone2_ws/pipet-physical-ai$ ffmpeg -version
python --version
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
python -c "import lerobot; print('lerobot import ok')"
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"

ffmpeg version 7.1.1 Copyright (c) 2000-2025 the FFmpeg developers
built with gcc 14.3.0 (conda-forge gcc 14.3.0-5)
configuration: --prefix=/home/sirlab-pwd-0000/miniconda3/envs/lerobot --cc=/home/conda/feedstock_root/build_artifacts/ffmpeg_1758923917305/_build_env/bin/x86_64-conda-linux-gnu-cc --cxx=/home/conda/feedstock_root/build_artifacts/ffmpeg_1758923917305/_build_env/bin/x86_64-conda-linux-gnu-c++ --nm=/home/conda/feedstock_root/build_artifacts/ffmpeg_1758923917305/_build_env/bin/x86_64-conda-linux-gnu-nm --ar=/home/conda/feedstock_root/build_artifacts/ffmpeg_1758923917305/_build_env/bin/x86_64-conda-linux-gnu-ar --disable-doc --enable-openssl --enable-demuxer=dash --enable-hardcoded-tables --enable-libfreetype --enable-libharfbuzz --enable-libfontconfig --enable-libopenh264 --enable-libdav1d --disable-gnutls --enable-libvpx --enable-libass --enable-pthreads --enable-alsa --enable-libpulse --enable-vaapi --enable-libvpl --enable-libopenvino --enable-gpl --enable-libx264 --enable-libx265 --enable-libmp3lame --enable-libaom --enable-libsvtav1 --enable-libxml2 --enable-pic --enable-shared --disable-static --enable-version3 --enable-zlib --enable-libvorbis --enable-libopus --enable-librsvg --enable-ffplay --pkg-config=/home/conda/feedstock_root/build_artifacts/ffmpeg_1758923917305/_build_env/bin/pkg-config
libavutil      59. 39.100 / 59. 39.100
libavcodec     61. 19.101 / 61. 19.101
libavformat    61.  7.100 / 61.  7.100
libavdevice    61.  3.100 / 61.  3.100
libavfilter    10.  4.100 / 10.  4.100
libswscale      8.  3.100 /  8.  3.100
libswresample   5.  3.100 /  5.  3.100
libpostproc    58.  3.100 / 58.  3.100
Python 3.12.13
0.5.1
lerobot import ok
2.10.0+cu128
True
NVIDIA GeForce RTX 3080 Laptop GPU
```

