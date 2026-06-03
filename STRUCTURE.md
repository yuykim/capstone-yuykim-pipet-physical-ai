# 프로젝트 폴더 구조

Indy7 로봇팔 + Mark7 로봇손 + RealSense D435를 이용한 Physical AI 피펫 조작 프로젝트.

> 설계 원칙: **의도(intent)별로 최상위 폴더를 나눈다.**
> 런타임 소프트웨어 / AI 파이프라인 / 시뮬레이션 / 우리가 만든 독립 툴 / 외부 vendored 코드 / 실행 스크립트 / 문서를 각각 분리한다.

---

## 최상위 구조

```
capstone-yuykim-pipet-physical-ai/
│
├── ros2_ws/          # ROS2 워크스페이스 (핵심 로봇 런타임 소프트웨어)
├── ai/               # AI 학습 파이프라인 (데이터 변환 → 학습 → 평가)
├── mujoco_env/       # MuJoCo 시뮬레이션 환경
├── tools/            # 1st-party 독립 실행 운용 툴 (ROS2 밖에서 동작)
├── vendor/           # 외부에서 가져온 vendored 코드 (수정 최소화)
├── run_scripts/      # 워크플로우별 실행 스크립트 (번호 순)
├── docs/             # 설계 문서, 의사결정 기록, 진행 기록, 환경 사진
├── img/              # 카메라 뷰 등 프로젝트 이미지
│
├── README.md         # 프로젝트 소개 및 빠른 시작
├── STRUCTURE.md      # (이 문서) 폴더 구조 및 역할
├── CLAUDE.md         # Claude Code용 프로젝트 컨텍스트
└── AGENTS.md         # AI 에이전트 작업 규칙
```

---

## 폴더별 상세 설명

### `ros2_ws/` — ROS2 워크스페이스

실제 로봇을 구동하는 ROS2 Humble 패키지들. `colcon build`로 빌드한다.

```
ros2_ws/src/
├── indy7_ros2/                   # Indy7 드라이버 서브모듈 (neuromeka-robotics/indy-ros2)
│   ├── indy_driver/              #   gRPC 기반 로봇 드라이버
│   ├── indy_interfaces/          #   커스텀 msg/srv 정의
│   ├── indy_description/         #   URDF/xacro
│   ├── indy_gazebo/              #   Gazebo 시뮬레이터 연동
│   └── indy_moveit/              #   MoveIt2 연동
│
├── mark7/                        # Mark7 로봇손 패키지
│   ├── pipet_hand_mark7_driver/  #   ros2_control 하드웨어 인터페이스 (USB Serial)
│   ├── pipet_hand_mark7_msgs/    #   GripperStatus, FingerState 메시지
│   ├── pipet_hand_mark7_description/ # URDF/메시 (시뮬 변환의 1순위 소스)
│   └── pipet_hand_mark7_teleop/  #   Mark7 단독 키보드 텔레옵
│
├── pipet_bringup/                # 통합 launch 파일 (data_collection, inference)
├── pipet_data_collector/         # 5토픽 동기화 + 그리퍼 캐시 → NPZ 저장
├── pipet_system_teleop/          # 통합 텔레옵 (Indy7 + Mark7 + 녹화 / 키보드·Xbox)
├── pipet_dagger_collection/      # DAgger 보정 데이터 수집 파이프라인
└── pipet_inference/              # 학습된 모델 → 자율 동작 노드 + operator GUI
```

### `ai/` — AI 학습 파이프라인

데이터 수집 후 학습까지의 전체 오프라인 파이프라인.

```
ai/
├── data_conversion/
│   ├── npz_to_lerobot/           # NPZ → LeRobot HuggingFace 데이터셋 변환
│   │   ├── convert.py            #   메인 변환 스크립트
│   │   └── indy7_tcp_fk.py       #   Indy7 FK 계산 (TCP 좌표 추출용)
│   └── make_grasp_focus_episodes.py  # grasp 집중 에피소드 추출
│
├── diagnostics/
│   ├── check_preprocess_alignment.py  # 학습/추론 전처리 정합 확인
│   └── offline_error_split.py         # action scale / clipping 오프라인 점검
│
├── lerobot/                      # LeRobot 학습 실행 스크립트
│   ├── run_lerobot_train.py      #   학습 진입점
│   └── train_*.sh                #   실험별 고정 레시피
│
├── lerobot_source/               # vendored LeRobot 라이브러리 (커스텀 패치 포함)
│   └── lerobot/                  #   PYTHONPATH로 직접 import (run_scripts 참고)
│
├── legacy/                       # 구버전 스크립트 (참고용 보존, 미사용)
│
└── logs/                         # 학습/추론 실험 기록 (md)
    ├── trainlog.md
    ├── train_26_04_20_half_data_summary.md
    └── inference_2026_05_11_grasp_focus_result.md
```

> 참고: `ai/models/`, `ai/datasets/`, `ai/.cache/`는 용량이 커서 `.gitignore` 처리됨 (추적 안 함).
> `ai/lerobot_source/`도 vendored 외부 코드지만, `PYTHONPATH`/bashrc 참조가 많아 `ai/` 안에 둔다.

### `mujoco_env/` — MuJoCo 시뮬레이션 환경

실제 하드웨어 없이 데이터 수집/검증을 위한 시뮬레이션.

```
mujoco_env/
├── models/
│   ├── indy7.urdf                # MuJoCo용 Indy7 모델
│   └── mark7_gripper.xacro       # Mark7 그리퍼 모델
├── indy7_urdf/                   # Indy7 원본 URDF + visual STL (시뮬 빌드 소스)
│   ├── indy.urdf                 #   prepare_models.py 입력
│   └── meshes/indy7/visual/      #   Indy7_0~6.stl (실제 사용분만 보존)
├── assets/                       # prepare_models.py 가 복사하는 mesh (indy7/, mark7/)
├── generated/
│   └── indy7_mujoco.urdf         # Indy7+Mark7 결합 결과물 (학습 FK에도 사용)
├── scripts/
│   ├── prepare_models.py         # indy7_urdf + vendor Mark7 xacro → generated URDF
│   ├── run_viewer.py             # 뷰어 실행
│   ├── keyboard_cartesian_teleop.py  # 키보드 카테시안 텔레옵
│   └── collect_dataset.py        # 시뮬 데이터 수집
└── README.md
```

> `indy7_urdf/`는 원래 Unity 에셋 export 전체(타 로봇 모델·.meta·Materials·collision 포함, ~580파일)였으나,
> `prepare_models.py`가 실제 쓰는 `indy.urdf` + `indy7 visual STL`만 남기고 정리했다. (필요 시 Neuromeka 원본에서 재생성)

### `tools/` — 1st-party 독립 실행 운용 툴

ROS2 워크스페이스 밖에서 독립적으로 실행하는 **우리가 만든** 운용 코드.

```
tools/
└── control_indy7/                # ROS2 없이 IndyDCP3로 Indy7 직접 제어
    ├── indy7/
    │   ├── indy7_controller.py   #   메인 컨트롤러 클래스
    │   ├── indy7_keyboard_control_v1.py  # 키보드 조작 (pygame)
    │   ├── move_home.py          #   홈 복귀 (operator GUI / bashrc home alias 에서 호출)
    │   ├── read_joint_state.py   #   관절 상태 읽기
    │   ├── indydcp3_example.ipynb #  IndyDCP3 API 예제 노트북
    │   └── ...
    ├── check_controller.py       #   컨트롤러 연결 확인
    └── readme.md
```

> `move_home.py`는 [operator_gui.py](ros2_ws/src/pipet_inference/pipet_inference/operator_gui.py)의 HOME 버튼이 런타임에 직접 실행한다. 경로 이동 시 함께 수정 필요.

### `vendor/` — 외부 vendored 코드

외부에서 가져와 그대로(또는 최소 수정으로) 두는 3rd-party 코드.

```
vendor/
└── pipet_gripper_Mark7/          # Mark7 그리퍼 description 업스트림 원본
    └── src/pipet_hand_mark7_description/  # URDF/메시
```

> `prepare_models.py`는 Mark7 description을 ① `ros2_ws/src/mark7/...`(1순위) ② `vendor/pipet_gripper_Mark7/...`(폴백) 순으로 찾는다.

### `run_scripts/` — 워크플로우 실행 스크립트

번호 접두사로 실행 순서를 나타낸다. 모든 예시는 레포 루트 기준.

```
run_scripts/
├── 00_env_ros.sh               # ROS2 Humble + install/setup + Cyclone DDS 로드 (source)
├── 10_data_collection_backend.sh   # 데이터 수집 backend (Indy7+Mark7+카메라+collector)
├── 11_data_collection_teleop.sh    # 데이터 수집 텔레옵
├── 20_train_lerobot.sh         # LeRobot 학습 (run_lerobot_train.py wrapper)
├── 21_train_26_04_20_half_data.sh  # 고정 레시피 실행
├── 22_train_mix_balanced_200.sh    # 균형 혼합 데이터 학습
├── 30_mujoco_prepare.sh        # MuJoCo 결합 URDF 생성
├── 31_mujoco_teleop.sh         # MuJoCo 키보드 텔레옵
├── 32_mujoco_collect.sh        # MuJoCo 데이터 수집
├── 40_inference_ros.sh         # 실기 추론 launch
├── 41_operator_gui.sh          # 오퍼레이터 GUI
├── 50_mark7_preset_test.sh     # Mark7 preset 동작 테스트
├── 60_check_preprocess_alignment.sh  # 전처리 정합 검사
├── 61_offline_error_split.sh   # 오프라인 오류 분류
└── README.md
```

### `docs/` — 문서

```
docs/
├── architecture.md             # 시스템 전체 아키텍처
├── interface_spec.md           # ROS2 토픽/서비스 인터페이스 명세
├── data_collection_decisions.md # 데이터 수집 설계 결정 기록
├── history.md                  # 프로젝트 변경 로그 (append-only)
├── neuromeka_indydcp3_summary.md # IndyDCP3 API 요약
├── ai/                         # AI 설계 문서 (architecture, lerobot_setup 등)
├── mark7/                      # Mark7 문서 및 프로토콜 PDF
├── data_collect_env/           # 데이터 수집 환경 사진 (1~7.jpg)
├── progress/                   # 실험 진행 스크린샷/영상
└── SirLab_publicLaptop/        # SIRLab 공용 노트북 환경 설정 가이드
```

### `img/` — 프로젝트 이미지

카메라 뷰 테스트 및 커버 비교 이미지 (README에서 참조).

```
img/
├── wrist_view*.png / overhead_view*.png  # 카메라 뷰 (RGB/Depth)
├── wrist_no_cover.png / wrist_perfect_cover.png / wrist_with_cover_not_perfect.png
└── withCover_vs_noCover/                  # 커버 유무 비교 이미지
```

---

## 데이터 흐름

```
[하드웨어]  Indy7 + Mark7 + RealSense
        ↓
[데이터 수집]  ros2_ws (pipet_data_collector + pipet_system_teleop)
              → ros2_ws/episodes/success/*.npz
        ↓
[데이터 변환]  ai/data_conversion/npz_to_lerobot/  (FK URDF: mujoco_env/generated)
              → ai/datasets/ (HuggingFace 포맷)
        ↓
[AI 학습]     ai/lerobot/ + ai/lerobot_source/
              → ai/models/ 체크포인트
        ↓
[배포/추론]   ros2_ws (pipet_inference, ZMQ sidecar)
              → 자율 피펫 조작
```

## 빌드/실행 의존 관계 (경로 참조 주의)

리팩토링 시 아래 경로 참조가 깨지지 않도록 함께 수정한다.

| 참조원 | 참조 대상 |
|--------|-----------|
| `ros2_ws/.../operator_gui.py` | `tools/control_indy7/indy7/move_home.py` |
| `mujoco_env/scripts/prepare_models.py` | `vendor/pipet_gripper_Mark7/...`, `mujoco_env/indy7_urdf/indy.urdf` |
| `run_scripts/*` (학습) | `ai/lerobot_source/lerobot/src` (PYTHONPATH) |
| bashrc alias `home` | `tools/control_indy7/indy7/move_home.py` |
