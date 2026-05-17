# LeRobot 학습 아키텍처

**최종 수정:** 2026-03-13  
**최종 수정자:** 김유영

---

# 문서 목적

본 문서는 프로젝트의 공통 raw 데이터가 LeRobot 기반 학습 파이프라인으로 어떻게 변환되고 사용되는지를 설명한다.


본 프로젝트의 원시 데이터 구조는 `ai_architecture.md`에서 정의하며,  
이 문서는 그 데이터를 **LeRobotDataset v3.0 형식으로 변환하여 학습하는 과정**에 초점을 맞춘다.

---

# 적용 범위

본 문서는 다음 경우에 적용된다.

- Hugging Face **LeRobotDataset v3.0** 형식으로 데이터셋을 구성하는 경우
- `lerobot-train` 기반으로 policy를 학습하는 경우
- 초기 baseline으로 **ACT** policy를 사용하는 경우
- 이후 필요 시 custom policy 구조로 확장하는 경우

본 문서는 프로젝트 전체의 유일한 데이터 정의 문서가 아니라,  
**LeRobot 전용 학습 아키텍처 문서**이다.

---

# 전체 구조

```text
[Raw Data]
timestamp
joint_positions
joint_velocities
ee_pose
rgb_images
depth_images
gripper_state
arm_actions
gripper_actions
episode_success
episode_id
    ↓
[Preprocessing / Export]
동기화
정제
정규화 통계 계산
LeRobot 키 구조로 변환
    ↓
[LeRobotDataset v3.0]
timestamp
observation.state
observation.images.front
action
meta/tasks.jsonl
meta/episodes/
data/
videos/
    ↓
[Training]
lerobot-train
policy.type=act
    ↓
[Inference / Evaluation]
학습된 policy checkpoint
    ↓
Indy7 + Mark7 제어
````

---

# Raw 데이터와 LeRobot 키 매핑

## 1. Raw Observation → LeRobot Observation

프로젝트에서 수집한 raw observation은 LeRobot 형식으로 다음과 같이 변환한다.

### Raw 입력 항목

* `timestamp`
* `joint_positions`
* `joint_velocities`
* `ee_pose`
* `rgb_images`
* `depth_images`
* `gripper_state`

### LeRobot 변환 결과

#### `timestamp`

원시 `timestamp`를 그대로 사용한다.

#### `observation.state`

아래 저차원 상태값을 하나의 벡터로 concatenate 하여 저장한다.

```text
observation.state[t] =
[
  joint_positions[t],     # 6
  joint_velocities[t],    # 6
  ee_pose[t],             # 7
  gripper_state[t]        # 1
]
```

총 차원은 다음과 같다.

```text
6 + 6 + 7 + 1 = 20
```

즉,

```text
observation.state.shape = (N, 20)
```

#### `observation.images.front`

원시 `rgb_images`를 전면 카메라 이미지로 저장한다.

```text
rgb_images → observation.images.front
```

초기 baseline에서는 RGB 이미지를 주 입력으로 사용한다.

#### `depth_images`

초기 LeRobot baseline에서는 직접 입력으로 사용하지 않고 raw 데이터로만 우선 보관한다.
추후 custom processor 또는 custom policy를 적용할 경우 확장 입력으로 사용할 수 있다.

---

## 2. Raw Action → LeRobot Action

프로젝트의 raw action은 다음과 같다.

* `arm_actions`
* `gripper_actions`

LeRobot baseline 학습에서는 이를 하나의 action 벡터로 결합한다.

```text
action[t] =
[
  arm_actions[t],       # 6
  gripper_actions[t]    # 1
]
```

즉,

```text
action.shape = (N, 7)
```

---

## 3. Episode Metadata → LeRobot Metadata

프로젝트의 raw episode metadata는 다음과 같다.

* `episode_success`
* `episode_id`

LeRobot에서는 episode 관련 정보가 frame-level 샘플 내부가 아니라 별도 metadata로 관리된다.

### 매핑 방식

* `episode_id` → episode-level metadata
* `episode_success` → 프로젝트용 정제 메타데이터
* task 문장 → `single_task` 또는 task metadata

예시:

```text
single_task = "Pick up the pipette"
```

---

# LeRobotDataset v3.0 최종 샘플 구조

최종적으로 각 시점 `t`의 학습 샘플은 다음과 같이 구성된다.

```text
sample_t =
{
  "timestamp": timestamp[t],
  "observation.state": [
    joint_positions[t],
    joint_velocities[t],
    ee_pose[t],
    gripper_state[t]
  ],
  "observation.images.front": rgb_images[t],
  "action": [
    arm_actions[t],
    gripper_actions[t]
  ]
}
```

---

# LeRobotDataset 저장 구조

LeRobotDataset v3.0으로 export할 경우 데이터는 다음 구조를 따른다.

```text
dataset/
├─ meta/
│  ├─ info.json
│  ├─ stats.json
│  ├─ tasks.jsonl
│  └─ episodes/
├─ data/
└─ videos/
```

설명:

* `meta/info.json`: feature schema, shape, dtype, FPS 등
* `meta/stats.json`: normalization용 통계값
* `meta/tasks.jsonl`: task description
* `meta/episodes/`: episode length, task, offset 등
* `data/`: low-dimensional frame data
* `videos/`: camera video shards

---

# 데이터 export 절차

## 1. Raw 데이터 수집

* Indy7 직접 교시
* Mark7 키보드 조작
* RGB/Depth 수집
* episode 단위 저장

## 2. Episode 정제

* `episode_success == 1` 우선 사용
* 품질이 낮은 episode 제외
* 시작 자세와 task 조건 확인

## 3. Action 생성

팔 action은 다음 방식으로 생성한다.

```text
arm_actions[t] = joint_positions[t+1] - joint_positions[t]
```

그리퍼 action은 이산 명령을 사용한다.

```text
0: 유지
1: 잡기
2: 펴기
3: 파이펫 누르기
```

## 4. LeRobot 키 구조로 변환

* raw state → `observation.state`
* raw RGB → `observation.images.front`
* raw arm/gripper action → `action`

## 5. Dataset finalize 및 업로드

LeRobotDataset v3.0 export 시에는 episode 저장 후 반드시 dataset finalize 단계를 수행해야 한다.

---

# 초기 학습 전략

## 기본 정책

초기 baseline은 **ACT** 를 사용한다.

이유:

* LeRobot와 바로 연결 가능
* fine-grained manipulation에 적합
* 비교적 적은 demonstration으로 시작 가능
* 단일 GPU에서도 학습 부담이 크지 않음

## 입력

* `observation.images.front`
* `observation.state`

## 출력

* `action`

즉,

```text
(rgb image + robot state) → action
```

---

# 학습 실행 흐름

```text
LeRobotDataset repo 준비
    ↓
lerobot-train 실행
    ↓
ACT policy 학습
    ↓
checkpoint 저장
    ↓
policy checkpoint 기반 inference / evaluation
```

예시 명령 구조:

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/your_dataset \
  --policy.type=act \
  --output_dir=outputs/train/act_your_dataset \
  --job_name=act_your_dataset \
  --policy.device=cuda \
  --policy.repo_id=${HF_USER}/your_policy
```

---

# 추론 및 배포 구조

학습된 policy는 현재 observation을 입력받아 action을 예측한다.

```text
observation_t
  ├─ observation.images.front
  └─ observation.state
        ↓
    trained policy
        ↓
      action_t
        ├─ arm_actions_t
        └─ gripper_actions_t
```

배포 시에는 이를 실제 로봇 명령으로 변환한다.

## Indy7

```text
q_target = q_current + arm_actions_t
```

## Mark7

```text
0 -> 유지
1 -> grasp
2 -> open
3 -> press
```

---

# 확장 전략

초기에는 ACT + 단일 action 벡터 구조를 사용한다.

이후 필요 시 다음 방향으로 확장할 수 있다.

* custom processor 추가
* custom policy 추가
* gripper action을 별도 head로 분리
* depth 입력 추가
* 시계열 observation window 사용
* imitation learning 이후 RL 또는 reward model 적용

---

# 프로젝트 내 권장 역할 분리

본 프로젝트에서는 다음과 같이 역할을 분리한다.

## 1. 공통 raw 데이터 문서

* `raw_data_schema.md`
* 프로젝트 전체 데이터 정의 담당

## 2. LeRobot 전용 변환 / 학습 문서

* `lerobot_architecture.md`
* LeRobotDataset export 및 학습 구조 담당

## 3. 추후 custom policy 확장

* 별도 policy package 또는 adapter 레이어에서 관리

---

# 관련 문서

* [Raw 데이터 정의 문서](./ai_architecture.md)

````
