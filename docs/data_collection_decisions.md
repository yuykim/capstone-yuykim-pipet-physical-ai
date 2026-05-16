# Data Collection Decisions

**작성일:** 2026-05-17

이 문서는 데이터 수집 스키마와 학습에 사용할 observation/action 방향을 정리한 결정 로그다.
기준 구현은 `ros2_ws/src/pipet_data_collector/pipet_data_collector/data_collector_node.py`이다.

---

## 1. 최종 방향

- 데이터는 NPZ episode 파일로 저장한다.
- 라벨은 NPZ 내부가 아니라 경로/파일명으로 관리한다.
- 학습 중심은 `ee_poses` 기반 Cartesian 제어로 둔다.
- `joint_positions`는 학습의 중심은 아니지만, 로봇 상태/검증/안전용으로 저장한다.
- 그리퍼 명령은 이벤트가 아니라 mode로 저장한다.
- 추가 metadata는 유지보수용으로만 저장하고, LeRobot 변환 시 학습 feature에는 넣지 않는다.

저장 경로:

```text
episodes/success/episode_YYYYMMDD_HHMMSS_success.npz
episodes/fail/episode_YYYYMMDD_HHMMSS_fail.npz
episodes/unlabeled/episode_YYYYMMDD_HHMMSS_unlabeled.npz
```

---

## 2. 현재 NPZ 저장 데이터

| 키 | Shape | dtype | 역할 |
|----|-------|-------|------|
| `timestamps` | `(N,)` | `float64` | 녹화 시작 기준 상대 시간 |
| `home_joint_deg` | `(6,)` | `float32` | 수집 당시 home joint metadata |
| `camera_setup` | `()` | `str` | 카메라 구성 metadata |
| `joint_names` | `(6,)` | `str` | `joint_positions` column 순서 |
| `joint_positions` | `(N, 6)` | `float32` | Indy7 관절 위치, rad |
| `joint_velocities` | `(N, 6)` | `float32` | Indy7 관절 속도 |
| `joint_efforts` | `(N, 6)` | `float32` | Indy7 관절 effort/토크 계열 값 |
| `ee_poses` | `(N, 6)` | `float32` | TCP pose: `[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]` |
| `wrist_rgb_images` | `(N, H, W, 3)` | `uint8` | 손목 카메라 RGB |
| `overhead_rgb_images` | `(N, H, W, 3)` | `uint8` | 오버헤드 카메라 RGB |
| `gripper_actions` | `(N,)` | `int8` | 그리퍼 mode |

`success`는 NPZ 내부에 저장하지 않는다. `fail`과 `unlabeled`가 둘 다 `False`로 뭉개지는 문제가 있어서, 라벨은 경로/파일명으로만 관리한다.

---

## 3. 학습에 사용할 핵심 데이터

### `wrist_rgb_images`

손목 카메라 시점이다. 손끝 근처 상황, 파지 직전 정렬, 접촉 직전의 세부 상황을 보기 위해 필요하다.

- 학습 영향: 정밀 조작과 가까운 거리 보정에 중요하다.
- 판단: 필수.

### `overhead_rgb_images`

작업 공간을 위에서 보는 고정 시점이다. 전체 작업판, 물체 위치, 목표 위치를 파악하는 데 유리하다.

- 학습 영향: 전역 상황 인식에 중요하다.
- 판단: 필수.
- 참고: wrist only 또는 overhead only 학습도 가능하지만, 현재 작업은 둘 다 쓰는 쪽이 안정적이다.

### `ee_poses`

Indy7 TCP/end-effector pose다.

```text
[x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]
```

- 학습 영향: 파이펫 작업의 실제 작업 언어에 가장 가깝다.
- 결정: 학습의 중심 state/action은 `ee_pose`로 둔다.
- action 생성: `delta_ee_pose = ee_poses[t+1] - ee_poses[t]`.

### `joint_positions`

Indy7 6축 관절 위치다.

- `ee_pose`가 있어도 같은 TCP pose를 여러 관절 자세로 만들 수 있으므로 저장 가치는 있다.
- 학습 중심은 아니지만, 로봇 내부 상태, 관절 한계/특이점 분석, replay/debug에 유용하다.
- 판단: 저장 유지. 학습에서는 보조 상태로 쓸 수 있지만 중심은 `ee_pose`.

### `gripper_actions`

그리퍼 명령 mode다.

```text
0 = hold
1 = grasp
2 = open
3 = press
4 = release
```

논의 중 이벤트 방식도 고려했다.

이벤트 방식:

```text
0 0 0 1 0 0 0 2 0 0
```

mode 방식:

```text
0 0 0 1 1 1 1 2 2 2
```

최종 결정은 mode 방식이다.

- 이유: 이벤트 방식은 대부분 `0`이 되어 class imbalance가 심해질 수 있다.
- 학습 관점: mode가 gripper action label을 더 조밀하게 제공한다.
- 실행 시에는 같은 mode가 반복 예측되더라도, 실제 서비스 호출은 변화 시점에만 보내도록 처리할 수 있다.

---

## 4. 저장하지만 학습 feature로 쓰지 않는 데이터

### `timestamps`

녹화 시작 기준 상대 시간이다.

- 학습 입력으로는 필수 아님.
- 데이터 품질 관리, FPS 추정, drop/jitter 확인, replay/후처리에 중요하다.
- 저장 비용이 작으므로 유지한다.

### `joint_velocities`

관절 속도다.

- 필수는 아님.
- 저장 비용이 작고, 부드러운 trajectory 분석이나 개선 실험에 쓸 수 있다.
- 초기 학습 입력에서는 제외해도 된다.

### `joint_efforts`

관절 effort/토크 계열 값이다.

- 필수는 아님.
- 접촉/부하/실패 분석에 쓸 수 있지만, 노이즈와 의미 불확실성이 있을 수 있다.
- 저장 비용이 작으므로 유지한다.

### `joint_names`

`joint_positions`의 column 순서를 기록한다.

- 학습 입력으로는 불필요.
- 데이터 무결성/디버깅용으로 중요하다.
- 저장 비용이 거의 없으므로 유지한다.

### `home_joint_deg`

수집 당시 home position이다.

```text
[0.00, 25.00, -115.000, 90.0, 0.00, 0.000]
```

- 학습 입력으로 사용하지 않는다.
- home position이 바뀐 데이터셋이 섞일 때 유지보수용으로 사용한다.
- LeRobot 변환 시 제거/무시한다.

### `camera_setup`

카메라 구성 metadata다.

현재 기본값:

```text
wrist+overhead_rgb
```

- 학습 입력으로 사용하지 않는다.
- 나중에 `wrist only`, `overhead only`, `both` 데이터가 섞일 가능성이 있어 기록한다.
- LeRobot 변환 시 제거/무시한다.

---

## 5. 저장하지 않기로 한 데이터

### `success` 내부 키

저장하지 않는다.

- 경로/파일명에 이미 `success/fail/unlabeled`가 있다.
- NPZ 내부 bool은 `fail`과 `unlabeled`를 구분하지 못한다.
- 변환/리플레이 코드는 경로/파일명 기준으로 라벨을 판단한다.

### `camera_info`

저장하지 않는다.

- `camera_info`는 depth가 아니라 카메라 내부 파라미터다.
- RGB imitation learning baseline에는 직접 필요하지 않다.
- 나중에 depth/3D geometry를 쓰게 되면 다시 고려한다.

### Depth 이미지

저장하지 않는다.

- RGB 두 대 + `ee_pose` baseline을 먼저 만든다.
- Depth는 용량과 동기화 복잡도를 크게 늘린다.
- RealSense depth는 얇거나 반사되는 물체에서 노이즈가 있을 수 있다.
- 거리/높이 인식이 baseline 실패 원인으로 확인되면 2차 실험으로 추가한다.

### Camera extrinsics / TF

보류한다.

- RGB imitation learning에는 직접 필요하지 않다.
- 정확한 캘리브레이션 없이 넣으면 오히려 잘못된 좌표계를 믿게 될 수 있다.
- 나중에 visual servoing, depth, point cloud, robot-camera 좌표 변환이 필요하면 다시 고려한다.

### `schema_version`

저장하지 않는다.

- 사람이 버전 업데이트를 관리해야 해서 빠뜨리면 오히려 부정확한 metadata가 된다.
- 필요할 때 실제 NPZ keys를 확인해서 처리한다.

### `ee_twist` / TCP velocity

저장하지 않는다.

- `ee_poses` 차분으로 후처리 가능하다.
- 직접 저장하면 노이즈와 동기화 관리가 늘어난다.

### `episode_phase`

저장하지 않는다.

- 사람이 phase를 라벨링해야 해서 번거롭다.
- 라벨 기준이 애매하면 데이터 품질이 떨어질 수 있다.

### `robot_status`

저장하지 않는다.

- 로봇 상태 종류가 많지 않고, 에러가 난 에피소드는 저장하지 않는 운영으로 처리한다.

### `raw_commanded_action`

보류한다.

- 키보드 조작 시 사람이 실제로 누른 명령을 저장하는 후보였다.
- 하지만 사람이 잘못 누른 순간 입력이 정답 action으로 남을 수 있다.
- 현재는 실제 수행 결과인 `ee_pose[t+1] - ee_pose[t]`를 action으로 사용하는 쪽이 낫다.

---

## 6. LeRobot 변환 원칙

- 학습 action은 기본적으로 Cartesian action이다.

```text
action = [delta_ee_pose(6), gripper_action(1)]
```

- `home_joint_deg`, `camera_setup`, `joint_names`, `timestamps`는 LeRobot feature로 넣지 않는다.
- 라벨 필터링은 NPZ 내부 `success`가 아니라 경로/파일명 기준으로 한다.
- 초기 학습은 `success` episode 위주로 진행한다.

---

## 7. 현재 추천 수집 전략

1. RGB 두 대와 `ee_pose` 중심 스키마로 먼저 성공 데모를 수집한다.
2. 학습은 `ee_pose` delta 기반 Cartesian action으로 시작한다.
3. `joint_positions`는 저장하되 중심 action으로 쓰지 않는다.
4. 실패/에러 에피소드는 저장하지 않거나 `fail`로 분리한다.
5. 데이터 종류를 더 늘리기보다, 깨끗한 성공 데모를 충분히 모으는 것을 우선한다.
