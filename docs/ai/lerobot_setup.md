

## 1. `LEROBOT_SETUP.md`에 들어갈 내용

이 문서는 **설치 로그 + 재현 가능한 명령어** 중심으로 적으면 돼. LeRobot 공식 설치 문서는 **Conda 환경에서 Python 3.12**를 만들고, Conda를 쓸 때는 **`ffmpeg`를 conda-forge로 설치**하라고 안내하며, **ffmpeg 8.x는 아직 지원되지 않는다**고 적고 있다. 설치는 PyPI로 바로 가능하지만, 커스텀 하드웨어를 붙일 계획이면 **소스 설치(`pip install -e .`)**가 더 적합하다. ([Hugging Face][2])

추천 내용은 이렇게:

````markdown
# LeRobot 설치 가이드

## 1. 목표
- Conda 환경에 LeRobot 설치
- Indy7 연동을 위한 개발 기반 준비
- 추후 custom robot plugin 개발 가능하도록 source install 사용

## 2. Conda 환경 생성
```bash
conda create -y -n lerobot_indy7 python=3.12
conda activate lerobot_indy7
conda install -y -c conda-forge ffmpeg
ffmpeg -version
````

## 3. LeRobot 설치

```bash
git clone https://github.com/huggingface/lerobot.git
cd lerobot
pip install -e .
lerobot-info
```

## 4. 선택 설치

* SmolVLA를 쓸 경우:

```bash
pip install -e ".[smolvla]"
```

## 5. 확인 항목

```bash
python --version
ffmpeg -version
pip show lerobot
lerobot-info
```

## 6. 주의사항

* ffmpeg 8.x는 아직 공식 문서 기준 지원되지 않음
* LeRobot 작업은 `lerobot_indy7` 환경에서 진행
* ROS2/indy-ros2와의 연동은 다음 문서에서 정리

````

---

## 2. `INDY7_LEROBOT_INTEGRATION.md`에 들어갈 내용

이 문서는 제일 중요해. Indy7은 LeRobot 문서의 기본 제공 로봇 목록에 있는 장비가 아니라서, 공식적으로는 **Bring Your Own Hardware** 방식으로 붙이는 게 맞다. LeRobot는 이를 위해 **`Robot` 베이스 클래스**를 제공하고, 커스텀 로봇을 별도 패키지로 만들어 CLI가 자동 인식하도록 하는 규칙도 문서화해 두었다. 패키지 이름은 `lerobot_robot_` 접두사를 써야 하고, `Config` 클래스와 실제 디바이스 클래스의 이름 규칙도 맞춰야 한다. :contentReference[oaicite:2]{index=2}

추천 내용은 이렇게:

```markdown
# Indy7 - LeRobot 연동 설계

## 1. 목표
- Indy7을 LeRobot custom robot으로 연결
- LeRobot CLI(`lerobot-record`, `lerobot-teleoperate`, `lerobot-train`)와 연동 가능하게 구성
- 향후 imitation learning용 데이터 수집 및 실기 평가 지원

## 2. 기본 전략
- 저수준 제어: Neuromeka SDK 또는 현재 사용 중인 indy-ros2 활용
- 상위 인터페이스: LeRobot Robot 클래스 구현
- 관측(observation): joint state + gripper state + camera image
- 행동(action): joint command 또는 end-effector command

## 3. 사용할 기존 기반
- ROS 2 Humble
- rmw_cyclonedds_cpp
- neuromeka / indy-ros2

## 4. 패키지 구조(예정)
lerobot_robot_indy7/
├── pyproject.toml
└── lerobot_robot_indy7/
    ├── __init__.py
    ├── config_indy7.py
    └── indy7.py

## 5. 클래스 설계
- `Indy7Config`
- `Indy7`

## 6. 필수 구현 메서드
- `connect()`
- `disconnect()`
- `get_observation()`
- `send_action()`
- 필요 시 `calibrate()` / `configure()`

## 7. observation / action 초안
### observation
- observation.state.joint_position
- observation.state.joint_velocity
- observation.state.gripper
- observation.images.front
- observation.images.wrist (선택)

### action
- action.joint_position
또는
- action.ee_delta
- action.gripper

## 8. 1차 구현 원칙
- 처음에는 joint position control 기반으로 단순하게 시작
- 안정화 후 end-effector space action으로 확장
- 속도 제한 / workspace 제한 / gripper 제한 필수

## 9. 연동 단계
1. Indy7 단독 제어 확인
2. Python/ROS wrapper 정리
3. LeRobot Robot 클래스 구현
4. `lerobot-record`에서 robot.type=indy7로 호출 가능하게 연결
````

---

## 3. `INDY7_IMITATION_LEARNING_PLAN.md`에 들어갈 내용

이건 실험 설계 문서야. LeRobot 공식 흐름은 **데이터 기록 → 시각화 → 학습 → 평가**이고, 데이터는 현재 **LeRobotDataset v3** 포맷으로 관리된다. 이 포맷은 **Parquet + MP4** 기반의 표준 포맷이고, 학습 시 `LeRobotDataset`으로 바로 로드할 수 있다. ([Hugging Face][3])

정책은 첫 시작이면 **ACT**를 추천해. LeRobot 공식 문서가 ACT를 **시작할 때 가장 먼저 추천하는 정책**으로 소개하고 있고, 이유도 **빠른 학습, 낮은 계산량, 단일 GPU에서 수시간 수준, 초보자 친화적**이라고 명시한다. 언어 지시문까지 같이 넣고 싶다면 그 다음 단계에서 **SmolVLA**를 고려하면 된다. SmolVLA는 **멀티카메라 + 로봇 상태 + 자연어 instruction**을 입력으로 쓰고, 공식 문서상 자체 데이터로 파인튜닝하는 구조다. ([Hugging Face][4])

추천 내용은 이렇게:

```markdown
# Indy7 모방학습 계획

## 1. 목표
Indy7 로봇팔이 단일 작업을 모방학습으로 수행하도록 한다.

## 2. 1차 대상 작업
후보:
- 블록 pick-and-place
- 지정 위치로 이동 후 gripper close/open
- 고정된 시작 위치에서 목표 위치까지 이송

우선순위:
1. 반복 가능하고 안전한 작업
2. 성공/실패 판정이 쉬운 작업
3. 카메라로 관측 가능한 작업

## 3. 데이터 수집 방식
- 텔레오퍼레이션 또는 수동 데모 기반 수집
- 1차 목표: 30~50 episode
- variation 포함:
  - 물체 위치 약간 변경
  - 시작 자세 약간 변경
  - 조명/배경 최소한의 변화

## 4. 기록할 데이터
- joint position
- joint velocity
- gripper state
- front camera RGB
- wrist camera RGB (가능하면 추가)
- task description

## 5. 데이터셋 형식
- LeRobotDataset v3 형식 사용
- low-dimensional state: Parquet
- image/video: MP4 기반 저장

## 6. 1차 학습 정책
- baseline: ACT

선정 이유:
- LeRobot 공식 추천 시작점
- 비교적 가볍고 빠름
- manipulation task에 적합

## 7. 2차 확장 정책
- SmolVLA
조건:
- task description(자연어)까지 함께 활용하고 싶을 때
- 더 다양한 변형/일반화를 보고 싶을 때

## 8. 실험 단계
### Stage 1. 시스템 안정화
- Indy7 제어 안정화
- 카메라 입력 안정화
- observation/action schema 확정

### Stage 2. 데이터 수집
- 10 episode 소규모 테스트
- 재생(replay) 확인
- 이후 30~50 episode 본수집

### Stage 3. 학습
- ACT 기본 설정으로 1차 학습
- validation episode로 중간 점검

### Stage 4. 평가
- 학습에 쓰지 않은 시작 위치에서 테스트
- 성공률, 수행 시간, 경로 안정성 기록

### Stage 5. 개선
- 데이터 추가 수집
- camera 추가
- SmolVLA 또는 다른 policy 비교

## 9. 성공 기준
- 고정 task에서 안정적 수행
- 10회 평가 중 목표 성공률 달성
- 위험 동작 없이 반복 가능

## 10. 리스크
- Teleop 품질이 낮으면 데이터 품질 저하
- observation/action 정의 불일치
- 카메라 지연 또는 timestamp mismatch
- 로봇 안전 제한 미설정 시 위험
```

---

## 내가 추천하는 실제 진행 순서

1. `ENVIRONMENT.md`는 그대로 유지
2. 새로 `LEROBOT_SETUP.md` 작성
3. 바로 이어서 `INDY7_LEROBOT_INTEGRATION.md` 작성
4. 마지막으로 `INDY7_IMITATION_LEARNING_PLAN.md` 작성
5. 그다음 실제 작업은
   **LeRobot 설치 → Indy7 custom robot 스켈레톤 생성 → 단순 observation/action 연결 → 10개 episode 테스트 수집 → ACT baseline 학습**
   순으로 가면 된다. 공식 문서 기준으로도 LeRobot은 커스텀 하드웨어를 `Robot` 인터페이스로 붙인 뒤, `record/train/evaluate` 도구를 그대로 활용하는 구조다. ([Hugging Face][5])

원하면 다음 답변에서 바로
**`LEROBOT_SETUP.md` 한국어 초안**을 완성본으로 써줄게.

[1]: https://huggingface.co/docs/lerobot/il_robots?utm_source=chatgpt.com "Imitation Learning on Real-World Robots"
[2]: https://huggingface.co/docs/lerobot/installation?utm_source=chatgpt.com "Installation"
[3]: https://huggingface.co/docs/lerobot/il_robots "Imitation Learning on Real-World Robots · Hugging Face"
[4]: https://huggingface.co/docs/lerobot/act "ACT (Action Chunking with Transformers) · Hugging Face"
[5]: https://huggingface.co/docs/lerobot/en/integrate_hardware "Bring Your Own Hardware · Hugging Face"
