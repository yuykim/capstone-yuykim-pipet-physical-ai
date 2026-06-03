# 프로젝트 폴더 구조

Indy7 로봇팔 + Mark7 로봇손 + RealSense D435를 이용한 Physical AI 피펫 조작 프로젝트.

---

## 최상위 구조

```
capstone-yuykim-pipet-physical-ai/
│
├── ros2_ws/          # ROS2 워크스페이스 (핵심 로봇 소프트웨어)
├── ai/               # AI 학습 파이프라인 (데이터 변환 → 학습 → 평가)
├── mujoco_env/       # MuJoCo 시뮬레이션 환경
├── external/         # ROS2 외부에서 독립 실행되는 코드/패키지
├── run_scripts/      # 워크플로우별 실행 스크립트 모음
├── docs/             # 설계 문서, 의사결정 기록, 환경 사진
├── img/              # 카메라 뷰 등 프로젝트 이미지
│
├── README.md         # 프로젝트 소개 및 빠른 시작
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
│   ├── pipet_hand_mark7_description/ # URDF/메시
│   └── pipet_hand_mark7_teleop/  #   Mark7 단독 키보드 텔레옵
│
├── pipet_bringup/                # 통합 launch 파일 (data_collection, inference)
├── pipet_data_collector/         # 5토픽 동기화 + 그리퍼 캐시 → NPZ 저장
├── pipet_system_teleop/          # 통합 텔레옵 (Indy7 + Mark7 + 녹화 제어)
├── pipet_dagger_collection/      # DAgger 보정 데이터 수집 파이프라인
└── pipet_inference/              # 학습된 모델 → 자율 동작 노드
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
│   ├── check_preprocess_alignment.py  # 전처리 정합성 확인
│   └── offline_error_split.py         # 오프라인 오류 분류
│
├── lerobot/                      # LeRobot 학습 실행 스크립트
│   ├── run_lerobot_train.py      #   학습 진입점
│   ├── train_26_04_07.sh         #   학습 실험 설정 (4월 7일)
│   └── train_26_04_20_half_data.sh   #   학습 실험 설정 (4월 20일, 절반 데이터)
│
├── lerobot_source/               # LeRobot 소스코드 (커스텀 패치 포함)
│   └── lerobot/                  #   streaming_dataset.py 등 수정본
│
├── legacy/                       # 구버전 스크립트 (참고용 보존)
│   └── scripts/                  #   build_simple_lerobot_npz.py 등
│
└── logs/                         # 학습/추론 실험 기록
    ├── trainlog.md               #   전체 학습 실험 로그
    ├── train_26_04_20_half_data_summary.md
    └── inference_2026_05_11_grasp_focus_result.md
```

### `mujoco_env/` — MuJoCo 시뮬레이션 환경

실제 하드웨어 없이 데이터 수집/검증을 위한 시뮬레이션.

```
mujoco_env/
├── assets/
│   ├── indy7/                    # Indy7 STL 메시
│   └── mark7/                    # Mark7 STL 메시
├── models/
│   ├── indy7.urdf                # MuJoCo용 Indy7 모델
│   └── mark7_gripper.xacro       # Mark7 그리퍼 모델
├── generated/
│   └── indy7_mujoco.urdf         # xacro → urdf 변환 결과물
├── indy7_urdf/                   # Unity/URDF 에셋 (메시 + 머티리얼)
├── scripts/
│   ├── prepare_models.py         # URDF 전처리
│   ├── run_viewer.py             # 뷰어 실행
│   ├── keyboard_cartesian_teleop.py  # 키보드 카테시안 텔레옵
│   └── collect_dataset.py        # 시뮬 데이터 수집
└── README.md
```

### `external/` — 독립 실행 코드 및 외부 패키지

ROS2 워크스페이스 밖에서 독립적으로 실행하는 코드.

```
external/
├── control_indy7/                # ROS2 없이 IndyDCP3로 Indy7 직접 제어
│   ├── indy7/
│   │   ├── indy7_controller.py   #   메인 컨트롤러 클래스
│   │   ├── indy7_keyboard_control_v1.py  # 키보드 조작 (pygame)
│   │   ├── move_home.py          #   홈 포지션 이동
│   │   ├── read_joint_state.py   #   관절 상태 읽기
│   │   ├── indydcp3_example.ipynb #  IndyDCP3 API 예제 노트북
│   │   └── ...
│   ├── check_controller.py       #   컨트롤러 연결 확인
│   └── readme.md
│
└── pipet_gripper_Mark7/          # Mark7 그리퍼 ROS2 패키지 원본 (업스트림)
    └── src/pipet_hand_mark7_description/  # URDF/메시 (ros2_ws 버전과 xacro 일부 상이)
```

### `run_scripts/` — 워크플로우 실행 스크립트

번호 접두사로 실행 순서를 나타낸다.

```
run_scripts/
├── 00_env_ros.sh               # ROS2 환경변수 설정 (source 용)
├── 10_data_collection_backend.sh   # 데이터 수집 백엔드 (Indy7+Mark7+카메라)
├── 11_data_collection_teleop.sh    # 데이터 수집 텔레옵
├── 20_train_lerobot.sh         # LeRobot 학습 실행
├── 21_train_26_04_20_half_data.sh  # 절반 데이터 학습 실험
├── 22_train_mix_balanced_200.sh    # 균형 혼합 데이터 학습
├── 30_mujoco_prepare.sh        # MuJoCo 모델 준비
├── 31_mujoco_teleop.sh         # MuJoCo 텔레옵
├── 32_mujoco_collect.sh        # MuJoCo 데이터 수집
├── 40_inference_ros.sh         # ROS2 추론 실행
├── 41_operator_gui.sh          # 오퍼레이터 GUI
├── 50_mark7_preset_test.sh     # Mark7 프리셋 동작 테스트
├── 60_check_preprocess_alignment.sh  # 전처리 정합성 검사
├── 61_offline_error_split.sh   # 오프라인 오류 분류
└── README.md
```

### `docs/` — 문서

```
docs/
├── architecture.md             # 시스템 전체 아키텍처
├── interface_spec.md           # ROS2 토픽/서비스 인터페이스 명세
├── data_collection_decisions.md # 데이터 수집 설계 결정 기록
├── history.md                  # 프로젝트 히스토리 및 실험 기록
├── neuromeka_indydcp3_summary.md # IndyDCP3 API 요약
├── ai/                         # AI 관련 설계 문서
│   ├── ai_architecture.md
│   ├── lerobot_architecture.md
│   ├── lerobot_setup.md
│   └── pipette_localization_recovery.md
├── mark7/                      # Mark7 관련 문서 및 프로토콜
│   ├── architecture.md
│   ├── PRD.md
│   └── Interface_with_Mark7 Hand_Simpler Protocol_20260305.pdf
├── data_collect_env/           # 데이터 수집 환경 사진 (1~7.jpg)
├── progress/                   # 실험 진행 스크린샷/영상
│   ├── mujoco_execute.png
│   ├── mujoco_execute2.png
│   └── train_progress.webm
└── SirLab_publicLaptop/        # SIRLab 공용 노트북 환경 설정 가이드
```

### `img/` — 프로젝트 이미지

카메라 뷰 테스트 및 커버 비교 이미지.

```
img/
├── wrist_view*.png             # 손목 카메라 뷰 (RGB/Depth)
├── overhead_view*.png          # 오버헤드 카메라 뷰
├── wrist_no_cover.png          # 커버 없는 손목 뷰
├── wrist_perfect_cover.png     # 완벽한 커버 손목 뷰
├── wrist_with_cover_not_perfect.png
└── withCover_vs_noCover/       # 커버 유무 비교 이미지
```

---

## 워크플로우 흐름

```
[하드웨어]
Indy7 + Mark7 + RealSense
        ↓
[데이터 수집]  ros2_ws (pipet_data_collector + pipet_system_teleop)
              → episodes/success/*.npz
        ↓
[데이터 변환]  ai/data_conversion/npz_to_lerobot/
              → HuggingFace 데이터셋 포맷
        ↓
[AI 학습]     ai/lerobot/ + ai/lerobot_source/
              → 모델 체크포인트
        ↓
[배포/추론]   ros2_ws (pipet_inference)
              → 자율 피펫 조작
```
