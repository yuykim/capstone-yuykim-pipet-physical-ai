# 설계 문서

**최종 수정:** 2026-03-13
**최종 수정자:** 김유영

---

# 데이터 수집 및 학습 전략

## 왜 추가 데이터가 필요한가

본 프로젝트의 목표는 로봇이 **현재 observation(카메라 영상 + 로봇 상태)** 만을 바탕으로 **적절한 다음 action(팔 움직임 + 그리퍼 명령)** 을 출력하도록 학습하는 것이다.

이를 위해서는 단순히 센서 데이터만 저장하는 것으로는 충분하지 않다.
학습 데이터셋은 각 시점 `t`에 대해 다음과 같은 형태를 가져야 한다.

* **입력 (observation)**: 현재 로봇이 보고 있는 정보와 내부 상태
* **출력 (action)**: 해당 상태에서 실제로 수행해야 하는 다음 행동

즉, 데이터셋은 다음과 같은 구조를 가진다.

```text
observation_t → action_t
```

---

## 모아야 하는 데이터

데이터는 각 시점의 **관측값(observation)** 과 **행동값(action)** 으로 나누어 수집한다.
수집된 데이터는 이후 전처리 및 변환을 거쳐 다양한 형식으로 활용되며, 여러 플랫폼에서 학습을 수행하는 데 사용한다.
*LeRobot 기반 학습을 수행하는 경우에는 Hugging Face에서 제공하는 **LeRobotDataset v3.0** 형식으로 변환한다.*
* [LeRobotDataset v3.0 관련 문서](./lerobot_architecture.md)

### Raw Observation (입력 데이터)

모델이 현재 상황을 판단하기 위해 사용하는 입력값이다.

| 키                  | Shape              | 설명                                                                                               |
| ------------------ | ------------------ | ------------------------------------------------------------------------------------------------ |
| `timestamp`       | `(N,)`             | 녹화 시작 기준 상대 시간                                                                                   |
| `joint_positions`  | `(N, 6)`           | Indy7 관절 각도 (rad)                                                                                |
| `joint_velocities` | `(N, 6)`           | Indy7 관절 속도 (rad/s)                                                                              |
| `joint_efforts`    | `(N, 6)`           | Indy7 관절 토크 (N·m)                                                                                |
| `ee_pose`          | `(N, 7)`           | 엔드이펙터(Mark7 그리퍼 기준점)의 pose — Indy7 base 좌표계 기준 위치 `(x, y, z)` 와 자세 quaternion `(qx, qy, qz, qw)` |
| `rgb_images`       | `(N, 224, 224, 3)` | RGB 이미지                                                                                          |
| `depth_images`     | `(N, 224, 224)`    | Depth 이미지 (mm)                                                                                   |
| `gripper_state`    | `(N,)`             | Mark7 실제 상태 — 이산값 `(0: 열림 / 1: 닫히는 중 / 2: 잡힘 / 3: 누름 상태)`                                        |

### Raw Action (출력 데이터)

모델이 observation을 보고 예측해야 하는 정답 행동값이다.

| 키                 | Shape    | 설명                                                        |
| ----------------- | -------- | --------------------------------------------------------- |
| `arm_actions`     | `(N, 6)` | Indy7의 다음 행동값 — 각 관절 변화량 `Δq = q[t+1] - q[t]`             |
| `gripper_actions` | `(N,)`   | Mark7 그리퍼 액션 — 이산값 `(0: 유지 / 1: 잡기 / 2: 펴기 / 3: 파이펫 누르기)` |

### Raw Episode Metadata (에피소드 단위 메타데이터)

에피소드 품질 관리 및 학습 데이터 정제를 위해 함께 저장하는 메타데이터이다.

| 키                 | Shape  | 설명                               |
| ----------------- | ------ | -------------------------------- |
| `episode_success` | `(1,)` | 해당 에피소드의 성공 여부 `(0: 실패 / 1: 성공)` |
| `episode_id`      | `(1,)` | 에피소드 고유 ID                       |

> **메모 1**: `joint_positions`만으로도 엔드이펙터 위치를 계산할 수 있으나, 파이펫 파지처럼 손끝의 위치와 자세 정렬이 중요한 작업에서는 `ee_pose`를 직접 저장하는 것이 디버깅과 학습에 유리하다.
> **메모 2**: `gripper_actions`는 명령값이고, `gripper_state`는 실제 상태값이다. RF 통신 누락 등으로 명령과 실제 상태가 다를 수 있으므로 분리해서 저장한다.
> **메모 3**: 아직 그리퍼 조작 코드가 완성되기 전이므로 추후 일부 항목은 수정될 수 있다.
> **메모 4**: 필요에 따라 본 raw 데이터는 *LeRobotDataset v3.0*, *일반 PyTorch Dataset*, 또는 기타 학습용 포맷으로 변환하여 사용할 수 있다.

---

## 데이터 수집 방식

### 수집 방식

* **Indy7**: 직접 교시 (중력 보상 모드에서 손으로 직접 조작)
* **Mark7**: 키보드 조작 (잡기 / 펴기 / 파이펫 누르기)
* **RealSense D435**: RGB/Depth 이미지 수집

### 동기화 방식

* `ApproximateTimeSynchronizer`를 사용한다.
* 하나의 샘플은 동일 시점의 다음 데이터를 함께 저장한다.

  * 로봇 관절 상태
  * 엔드이펙터 pose
  * RGB 이미지
  * Depth 이미지
  * 그리퍼 상태
  * 그리퍼 명령

### 에피소드 정의

* 에피소드 = 시연 1회
* 기본 단위: **홈 포지션 → 파이펫 접근 → 파지 시도**
* 초기 목표: `50` 에피소드
* 이후 성능을 보며 점진적으로 증가

### 수집 시 유의사항

* 쓰레기 데이터보다 **깔끔한 시연**이 중요하다.
* 에피소드마다 시작 상태(홈 포지션)는 최대한 통일한다.
* 거치대 위치, 조명, 카메라 각도는 조금씩 변화시켜 다양성을 확보한다.
* 팔 동작과 그리퍼 동작의 타이밍 싱크가 어긋나지 않도록 주의한다.
* 가능하면 초기 학습에는 **성공한 에피소드 위주**로 사용한다.

---

## 학습용 데이터셋 구성 방식

학습 시에는 원본 시계열 데이터를 각 시점 `t`의 **입력-출력 쌍**으로 변환한다.

### 입력 (observation)

시점 `t`의 현재 상태를 입력으로 사용한다.

```text
observation_t =
{
  rgb_images[t],
  depth_images[t],
  joint_positions[t],
  joint_velocities[t],
  joint_efforts[t],
  ee_pose[t],
  gripper_state[t]
}
```

### 출력 (action)

시점 `t`에서 사람이 실제로 수행한 다음 행동을 정답으로 사용한다.

```text
action_t =
{
  arm_actions[t],
  gripper_actions[t]
}
```

즉, 모델은 다음 관계를 학습한다.

```text
현재 카메라 영상 + 현재 로봇 상태 → 다음 팔 움직임 + 다음 그리퍼 명령
```

---

## `arm_actions` 생성 방식

`arm_actions`는 직접 교시로 수집한 관절 시계열 데이터로부터 후처리하여 생성한다.

```text
arm_actions[t] = joint_positions[t+1] - joint_positions[t]
```

즉, 각 시점의 팔 action은 **다음 프레임으로 얼마나 움직였는지**를 나타내는 관절 변화량이다.

### 이 방식을 사용하는 이유

* direct teaching 데이터에서 쉽게 생성 가능
* 현재 상태에서 “얼마나 더 움직일지”를 예측하는 구조가 직관적임
* 연속 제어 문제를 비교적 안정적으로 학습할 수 있음

> 마지막 프레임은 `t+1`이 없으므로 일반적으로 학습 샘플에서 제외한다.

---

## 학습 시 입력 / 출력 정의

### 입력 (observation)

* `rgb_images`
* `depth_images`
* `joint_positions`
* `joint_velocities`
* `joint_efforts`
* `ee_pose`
* `gripper_state`

### 출력 (action)

* `arm_actions`
* `gripper_actions`

즉, 학습은 다음과 같은 형태로 이루어진다.

```text
(rgb, depth, joint state, ee pose, gripper state) → (arm delta, gripper command)
```

---

## 학습 방식

초기 단계에서는 **모방학습(Behavior Cloning)** 을 우선 적용한다.

### 이유

* 직접 교시 기반 시연 데이터를 바로 활용할 수 있음
* 구현 난이도가 비교적 낮음
* 파이펫 파지처럼 동작 구조가 비교적 정형화된 작업에 적합함

### 모델 출력 형태

* **팔 action**: 연속값 회귀

  * 출력: `arm_actions (N, 6)`
* **그리퍼 action**: 이산값 분류

  * 출력: `gripper_actions (N,)`

즉, 하나의 모델이 두 종류의 출력을 동시에 예측하는 **혼합 출력 구조**를 가진다.

### 학습 손실 예시

* 팔 action: MSE Loss 또는 Smooth L1 Loss
* 그리퍼 action: Cross Entropy Loss

최종 loss는 두 값을 가중합하여 사용한다.

```text
Loss = L_arm + λ · L_gripper
```

---

## 학습 절차

### 에피소드 정제

* `episode_success == 1` 인 에피소드를 우선 사용한다.
* 실패 에피소드는 초기 학습에서는 제외하거나 별도 관리한다.

### 프레임 단위 샘플 생성

* 각 시점 `t`에 대해 `observation_t → action_t` 쌍을 생성한다.
* `arm_actions[t] = joint_positions[t+1] - joint_positions[t]`

### 전처리

* RGB / Depth 이미지를 resize 및 normalize 한다.
* joint state를 normalize 한다.
* 필요 시 action clipping을 적용한다.

### Train / Validation 분리

* 프레임 단위가 아니라 **episode 단위로 분리**한다.
* 같은 에피소드가 train과 validation에 동시에 들어가지 않도록 한다.

### 학습

* Behavior Cloning으로 초기 정책을 학습한다.
* 이후 필요 시 ACT, Diffusion Policy, GAIL, PPO 등으로 확장할 수 있다.

---

## 추론 및 배포 시 동작 방식

배포 시에는 현재 observation을 모델에 입력하고, 모델이 예측한 action을 실제 로봇 명령으로 변환한다.

```text
observation_t
    ↓
학습된 모델
    ↓
(arm_actions_t, gripper_actions_t)
    ↓
Indy7 관절 목표값 계산 + Mark7 서비스 호출
```

### Indy7 제어

현재 관절값에 예측된 변화량을 더해 다음 목표 관절값을 계산한다.

```text
q_target = q_current + arm_actions_t
```

### Mark7 제어

예측된 `gripper_actions_t` 값에 따라 다음 서비스 중 하나를 호출한다.

* `0`: 유지
* `1`: `/gripper/grasp`
* `2`: `/gripper/open`
* `3`: `/gripper/press`

---

## 향후 확장 가능성

초기에는 그리퍼 action을 이산값으로 정의하지만, 향후에는 다음 방식으로 확장할 수 있다.

* 손가락별 연속 관절값 제어
* 시계열 입력 기반 정책 학습
* 시뮬레이션 기반 데이터 증강
* BC 이후 PPO / GAIL 등 강화학습 적용

현재 파이펫 조작은 동작이 비교적 고정적이므로, 초기 단계에서는 이산 action 기반 구조로도 충분하다고 판단한다.

좋아. 네 문서 흐름에 맞춰서 **전체 학습 레이어**를 텍스트 다이어그램으로 그리면 아래처럼 적을 수 있어.

---

## 학습 레이어

```text
┌──────────────────────────────────────────────────────────────────────┐
│                           데이터 수집 레이어                           │
│                                                                      │
│  Indy7 직접 교시        Mark7 키보드 조작        RealSense D435       │
│  (팔 시연)              (잡기/펴기/누르기)        (RGB/Depth 수집)     │
│        │                        │                        │             │
│        └───────────────┬────────┴────────┬───────────────┘             │
│                        │   시간 동기화 / 기록                          │
│                        │   (ApproximateTimeSynchronizer)               │
│                        ▼                                               │
│  observation 원본 저장:                                                │
│  joint_positions, joint_velocities, joint_efforts, ee_pose,           │
│  rgb_images, depth_images, gripper_state, gripper_actions             │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        데이터셋 구성 / 전처리 레이어                    │
│                                                                      │
│  1) episode 정제                                                     │
│     - 성공 episode 선택                                              │
│     - 시작 자세 / 품질 확인                                          │
│                                                                      │
│  2) action 생성                                                      │
│     - arm_actions[t] = joint_positions[t+1] - joint_positions[t]     │
│                                                                      │
│  3) 학습 샘플 생성                                                   │
│     - observation_t → action_t                                       │
│                                                                      │
│  4) 전처리                                                           │
│     - 이미지 resize / normalize                                      │
│     - joint state normalize                                          │
│     - episode 단위 train/val 분리                                    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                             학습 레이어                               │
│                                                                      │
│  입력 (observation)                                                  │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ rgb_images, depth_images, joint_positions, joint_velocities,  │   │
│  │ joint_efforts, ee_pose, gripper_state                         │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                               │                                      │
│                 ┌─────────────┴─────────────┐                        │
│                 │                           │                        │
│                 ▼                           ▼                        │
│        Vision Encoder                 State Encoder                  │
│   (RGB/Depth feature 추출)      (joint / ee_pose / gripper)         │
│                 │                           │                        │
│                 └─────────────┬─────────────┘                        │
│                               ▼                                      │
│                         Feature Fusion                               │
│                               ▼                                      │
│                        Policy Network                                │
│                               │                                      │
│              ┌────────────────┴────────────────┐                     │
│              ▼                                 ▼                     │
│      Arm Action Head                    Gripper Action Head          │
│    (연속값 회귀 출력)                     (이산값 분류 출력)          │
│              │                                 │                     │
│              ▼                                 ▼                     │
│      arm_actions (Δq)                  gripper_actions               │
│                                                                      │
│  Loss = L_arm + λ · L_gripper                                        │
│   - L_arm: MSE / Smooth L1                                           │
│   - L_gripper: Cross Entropy                                         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         추론 / 배포 레이어                            │
│                                                                      │
│  현재 observation 입력                                               │
│     rgb + depth + robot state + gripper state                        │
│                               │                                      │
│                               ▼                                      │
│                         학습된 모델                                  │
│                               │                                      │
│              ┌────────────────┴────────────────┐                     │
│              ▼                                 ▼                     │
│       arm_actions_t                      gripper_actions_t           │
│              │                                 │                     │
│              ▼                                 ▼                     │
│ q_target = q_current + arm_actions_t      grasp / open / press 호출  │
│              │                                 │                     │
│              └────────────────┬────────────────┘                     │
│                               ▼                                      │
│                     Indy7 + Mark7 실제 동작                           │
└──────────────────────────────────────────────────────────────────────┘

---

## 학습 레이어 요약

```text
[데이터 수집]
Indy7 직접 교시 + Mark7 키보드 조작 + RealSense RGB/Depth
        ↓
[동기화 및 저장]
observation 원본 저장
(joint, ee_pose, rgb, depth, gripper_state, gripper_actions)
        ↓
[데이터셋 구성]
arm_actions 생성
Δq = joint_positions[t+1] - joint_positions[t]
observation_t → action_t 샘플 생성
        ↓
[학습]
입력: rgb, depth, joint state, ee_pose, gripper_state
출력: arm_actions, gripper_actions
방법: Behavior Cloning
        ↓
[배포]
현재 observation 입력
        ↓
학습된 모델이 arm delta + gripper command 출력
        ↓
Indy7 + Mark7 제어
```