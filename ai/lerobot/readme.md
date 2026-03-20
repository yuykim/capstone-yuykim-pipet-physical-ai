> [LeRobot 공식 페이지](https://huggingface.co/docs/lerobot/en/index)
> [LeRobot 설치 방법](https://huggingface.co/docs/lerobot/en/installation)
> [LeRobotDataset v3.0 관련 문서](/docs/ai/lerobot_architecture.md)

###  참고사항
- **설치 날짜**: 2026.03.20
- **LeRobot 버전**: 0.5.1
- 현재 LeRobot 소스는 프로젝트 내부에 직접 포함되어 있어 자동 업데이트되지 않습니다.
- 향후 상위 버전의 LeRobot을 반영할 경우, 수동으로 변경 사항을 확인하고 필요한 수정 작업을 진행해야 합니다.

## LeRobot 설치

### Linux / WSL 환경을 사용한 이유

Windows 환경에서는 Conda로 `ffmpeg`를 설치하는 과정에서  
`gdk-pixbuf` / `UnicodeDecodeError('cp949', ...)` 관련 오류가 발생했다.  
따라서 LeRobot는 Linux 환경(WSL)에서 다시 설치하였다.

---

### 1. Conda 가상환경 생성

Python 3.12 기반의 새로운 Conda 가상환경을 생성한다.

```bash
conda create -y -n lerobot python=3.12 --override-channels -c conda-forge
conda activate lerobot
````

---

### 2. FFmpeg 설치

LeRobot는 비디오 데이터를 처리하기 위해 `ffmpeg`가 필요하다.

```bash
conda install -y ffmpeg=7.1.1 evdev --override-channels -c conda-forge
```

`ffmpeg`가 정상적으로 설치되었는지 확인한다.

```bash
ffmpeg -version
```

---

### 3. LeRobot 설치

`pip`를 사용하여 LeRobot를 설치한다.

```bash
pip install lerobot
```

설치된 버전을 확인한다.

```bash
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
```

---

### 4. 설치 확인

아래 명령어를 실행하여 LeRobot가 정상적으로 설치되었는지 확인한다.

```bash
lerobot-info
```

설치가 정상적으로 완료되었다면 다음과 같은 정보가 출력된다.

* LeRobot 버전
* Python 버전
* FFmpeg 버전
* PyTorch 버전
* CUDA 지원 여부
* 사용 가능한 `lerobot-*` 명령어 목록

---

### 5. 전체 설치 명령어

```bash
conda create -y -n lerobot python=3.12 --override-channels -c conda-forge
conda activate lerobot
conda install -y ffmpeg=7.1.1 evdev --override-channels -c conda-forge
pip install lerobot
ffmpeg -version
python -c "import importlib.metadata as m; print(m.version('lerobot'))"
lerobot-info
```

---

### 설치 확인 환경

현재 확인된 환경은 다음과 같다.

* LeRobot `0.5.0`
* FFmpeg `7.1.1`
* Python `3.12`
* CUDA 사용 가능
* GPU 정상 인식

````
