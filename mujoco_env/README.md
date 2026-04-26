# MuJoCo 디지털 트윈 환경 사용 가이드

이 문서는 `mujoco_env` 폴더에서 **Indy7 기반 디지털 트윈 시뮬레이션**과
**데이터 수집(NPZ 저장)**을 수행하는 방법을 자세히 설명합니다.

현재 기준:
- Indy7: MuJoCo 로드/뷰어/데이터 수집 동작
- Mark7: `pipet_gripper_Mark7`의 `pipet_hand_mark7.xacro`를 변환해 결합
- 결합 상태: `prepare_models.py`가 Indy7 `link6`에 실제 Mark7 링크/조인트(간이 프리셋 제어) 자동 추가

---

## 1. 폴더 구조

- `indy7_urdf/`
  - 원본 Indy7 URDF/mesh 소스
- `models/`
  - 사용자 확인용 모델 파일/링크
- `scripts/`
  - 모델 준비, 뷰어 실행, 데이터 수집 스크립트
- `assets/indy7/`
  - MuJoCo에서 읽기 쉬운 Indy7 mesh(STL) 복사본
- `generated/`
  - MuJoCo 로딩용으로 가공된 URDF 출력
- `data/`
  - 수집된 에피소드 `.npz` 저장 폴더

---

## 2. 사전 준비

### 2-1) Conda 환경 활성화

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mujoco
```

### 2-2) MuJoCo 설치 확인(선택)

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

버전이 출력되면 정상입니다.

---

## 3. 첫 실행 순서(권장)

아래 3단계를 순서대로 실행하면 됩니다.

### 3-1) MuJoCo용 모델 준비

```bash
python mujoco_env/scripts/prepare_models.py
```

이 스크립트가 하는 일:
1. `indy7_urdf/indy.urdf`를 읽음
2. URDF에서 참조하는 STL 파일 목록을 파싱
3. 필요한 STL을 `assets/indy7/`로 복사
4. URDF의 mesh 경로를 MuJoCo 친화적으로 정리
5. `<mujoco><compiler .../></mujoco>` 블록 삽입
   - `meshdir="../assets/indy7"`
   - `balanceinertia="true"`
6. 결과를 `generated/indy7_mujoco.urdf`로 저장
7. `pipet_gripper_Mark7`의 xacro를 URDF로 변환해 `link6`에 고정 결합

즉, 원본 URDF를 직접 수정하지 않고 MuJoCo 전용 URDF를 생성합니다.
그리퍼 제어 키(`G/O/P/R`)는 현재 실제 Mark7 관절들에 대한 프리셋(열기/잡기/누르기/릴리즈)로 동작합니다.

### 3-2) 뷰어로 동작 확인

```bash
python mujoco_env/scripts/run_viewer.py
```

설명:
- `generated/indy7_mujoco.urdf`를 로드
- 간단한 사인 궤적을 관절에 적용
- MuJoCo viewer 창에서 로봇 움직임 확인

### 3-3) 데이터 수집

```bash
python mujoco_env/scripts/collect_dataset.py --seconds 10 --hz 20 --success
```

설명:
- 10초 동안 20Hz로 샘플링 (`N=200`)
- 시뮬레이션 관절 상태를 배열로 수집
- `data/episode_YYYYMMDD_HHMMSS_success.npz` 형식으로 저장

`--success`를 빼면 파일명이 `_fail.npz`로 저장됩니다.

---

## 4. 데이터 포맷

저장 키:
- `timestamps`: `(N,)` float64
- `joint_positions`: `(N, nq)` float32
- `joint_velocities`: `(N, nv)` float32
- `joint_efforts`: `(N, nv)` float32
- `gripper_actions`: `(N,)` int8 (현재 기본값 `0=hold`)
- `success`: `()` bool

현재는 Indy7 중심 수집이며, 카메라 이미지 항목은 포함하지 않습니다.

---

## 5. 자주 쓰는 실행 예시

### 5-1) 모델 준비 + 짧은 테스트 수집(2초, 10Hz)

```bash
python mujoco_env/scripts/prepare_models.py
python mujoco_env/scripts/collect_dataset.py --seconds 2 --hz 10 --success
```

### 5-2) Indy7 키보드 Cartesian 조작 (X/Y/Z)

Neuromeka 쪽 Cartesian 조작 흐름(축 jog + 속도/프레임 전환)을 MuJoCo용으로 맞춘 스크립트:

```bash
python mujoco_env/scripts/keyboard_cartesian_teleop.py
```

키 매핑:

- `Arrow Up/Down` 또는 `W/S`: `+X / -X`
- `Arrow Left/Right` 또는 `A/D`: `+Y / -Y`
- `;` / `.` 또는 `Q/E`: `+Z / -Z`
- `8/2/4/6`: `+X/-X/+Y/-Y` (화살표 대체)
- `[` / `]`: 속도 감소/증가
- `-` / `=`: 관절 속도 게인 감소/증가
- `H`: 컨트롤러 home 자세로 즉시 복귀
- `Shift+H`: 텔레옵 시작 자세로 이동
- `G` / `O`: `grasp` / `open` (실제 Mark7 preset)
- `P` / `R`: `press` / `release` (실제 Mark7 preset)
- `B` / `T`: World/Tool frame 전환
- `Space`: 정지
- `Q`: 종료

옵션 예시:

```bash
python mujoco_env/scripts/keyboard_cartesian_teleop.py \
  --model mujoco_env/generated/indy7_mujoco.urdf \
  --linear-speed 0.16 \
  --damping 1e-4 \
  --qvel-gain 3.0 \
  --max-qvel 2.5 \
  --home-qpos "0,-0.436,2.007,0,1.571,0" \
  --teleop-start-qpos "0,0.611,-2.618,0,0.436,0"
```

기본은 **kinematic 모드**(정지 시 처짐 방지)로 동작합니다.  
동역학(`mj_step`)으로 보고 싶으면 `--dynamic`을 추가하세요.

### 5-3) 수집 파일 확인

```bash
python - <<'PY'
import numpy as np
p = "mujoco_env/data"
import os
files = sorted([f for f in os.listdir(p) if f.endswith(".npz")])
print("latest:", files[-1] if files else "none")
if files:
    d = np.load(os.path.join(p, files[-1]))
    print("keys:", d.files)
    print("qpos shape:", d["joint_positions"].shape)
PY
```

---

## 6. 트러블슈팅

### 문제 1) `Error opening file '...stl'`

원인:
- URDF의 mesh 경로와 실제 파일 위치가 맞지 않음

해결:
1. `python mujoco_env/scripts/prepare_models.py` 재실행
2. `mujoco_env/assets/indy7/`에 STL이 복사되었는지 확인
3. `mujoco_env/generated/indy7_mujoco.urdf`를 사용 중인지 확인

### 문제 2) `ModuleNotFoundError: No module named 'mujoco'`

원인:
- conda 환경 미활성화 또는 설치 누락

해결:
```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mujoco
pip install mujoco
```

### 문제 3) viewer 창이 뜨지 않음

가능 원인:
- 원격/헤드리스 환경에서 GUI 표시 불가

해결:
- 로컬 GUI 세션에서 실행
- viewer 없이 `collect_dataset.py`로 수집만 먼저 검증

---

## 7. Mark7 그리퍼 관련 메모

현재 파일:
- `mujoco_env/models/mark7_gripper.xacro`

주의:
- MuJoCo는 `xacro`를 직접 로드하지 못함
- `xacro -> urdf` 변환 후 `package://...` mesh 경로를 실제 경로로 치환해야 함

권장 다음 단계:
1. Mark7 xacro를 URDF로 변환
2. mesh를 `mujoco_env/assets/mark7/`로 정리
3. Indy7 + Mark7 결합 URDF/MJCF 생성
4. `gripper_actions`를 실제 시뮬레이션 제어 입력과 연결

---

## 8. 빠른 시작(복붙용)

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mujoco
python mujoco_env/scripts/prepare_models.py
python mujoco_env/scripts/run_viewer.py
# 새 터미널에서:
python mujoco_env/scripts/collect_dataset.py --seconds 10 --hz 20 --success
```
