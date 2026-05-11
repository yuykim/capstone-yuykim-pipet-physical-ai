# 2026-05-11 Grasp Focus Inference Result

## 요약

- 테스트 모델: `act_pipet_extended_depth_100_grasp_focus` 계열, 70k step 학습 모델
- 현재 결과: 파이펫 방향으로 접근하는 경우는 있으나, 최종 grasp 위치와 타이밍이 불안정함.
- 핵심 실패 양상: 파이펫을 충분히 깊게 물기 전에 너무 일찍 `grasp`를 시도함.
- 5회 시도 중 1회 성공했지만, 그 1회도 완전히 안정적인 성공으로 보기 어렵다. 너무 일찍 잡으려는 동작이 있었고 우연히 잡힌 것에 가까움.

## 관찰된 문제

### 1. 너무 이른 grasp

로봇이 파이펫을 향해 접근하긴 하지만, 실제로는 더 깊숙이 들어간 뒤 손을 닫아야 한다.
현재 모델은 그 전에 `grasp`를 시도하는 경향이 있다.

즉, 실패 구조는 다음과 같다.

```text
로봇이 파이펫 쪽으로 접근
-> 아직 파이펫을 안정적으로 잡을 위치가 아님
-> 모델이 grasp를 예측
-> 그리퍼가 너무 일찍 닫힘
-> 파이펫을 빗나가거나 얕게 건드림
```

### 2. 정확한 파이펫 위치/최종 grasp pose 불안정

단순히 파이펫 방향을 전혀 못 찾는 문제라기보다는, grasp 직전의 정확한 위치를 안정적으로 잡지 못하는 문제가 크다.
최종적으로는 파이펫이 그리퍼 안쪽에 충분히 들어온 뒤 잡아야 하는데, 그 기준을 모델이 아직 확실히 못 잡고 있다.

### 3. 파이펫 위치를 무시하는 이상 동작

일부 시도에서는 파이펫 위치와 무관하게 그냥 앞쪽/위쪽 방향으로 올라가는 현상도 있었다.
이는 카메라 입력, state/ee_pose 정렬, 학습 데이터 분포, 또는 action 출력 스케일/게이트 조건을 함께 점검해야 하는 신호다.

## 현재 성공률

```text
총 시도: 5회
성공: 1회
실패: 4회
```

성공 1회도 완전한 안정 성공은 아니다.
일찍 잡으려는 동작이 있었고, 결과적으로 잡히긴 했지만 재현성 있는 성공으로 판단하기는 어렵다.

## 현재 판단

- 70k step 모델은 파이펫 접근 자체는 일부 학습했지만, 안정적인 grasp 타이밍과 최종 위치 정렬은 부족하다.
- 문제는 단순히 step 수 부족이라기보다, 마지막 접근 구간의 데이터/행동 분포와 grasp 판단 조건이 약한 쪽에 가깝다.
- 현재 적용한 grasp gate(`grasp_delay_steps`, `grasp_confirm_steps`, `grasp_max_delta_norm`)는 너무 이른 grasp를 줄이기 위한 보정이지만, 모델이 최종 pose 자체를 흔들리게 잡으면 한계가 있다.

## 다음 실험

다음으로 80k step 모델을 실행해 비교한다.

대상 모델:

```text
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/080000
```

비교할 항목:

- 파이펫 방향 접근이 70k보다 안정적인지
- grasp를 너무 일찍 시도하는 빈도가 줄었는지
- 더 깊숙이 들어간 뒤 손을 닫는지
- 파이펫 위치를 무시하고 앞/위로 이동하는 이상 동작이 줄었는지
- 5회 이상 반복했을 때 성공률이 개선되는지

## 후속 개선 방향

- grasp 직전 구간을 더 많이 포함한 추가 데이터 수집
- 파이펫이 그리퍼 안쪽에 충분히 들어온 상태에서만 `grasp`가 나오도록 데모 타이밍 정리
- 필요 시 Gemini-ER 또는 별도 비전 검증기를 사용해 `grasp_ready` 조건을 추가
- 단순 delay보다 "확실히 잡을 위치인지"를 판단하는 gate 강화

---

## 2026-05-12 80k 모델 실기 결과

### 실행 모델

```text
ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/080000
```

실행 조건:

```text
grasp_delay_steps:=8
pre_grasp_delta_scale:=1.15
grasp_confirm_steps:=8
grasp_max_delta_norm:=0.008
max_joint_speed_rad_s:=0.25
image_target_height:=360
image_target_width:=480
state_target_dim:=26
```

### 10회 시도 결과

```text
총 시도: 10회
성공: 3회
실패: 7회
```

단, 성공 3회 중 일부는 완전히 안정적인 성공으로 보기 어렵다.
공통적으로 그리퍼가 조금 빠르게 닫히는 느낌이 있었고, 파이펫을 깊고 단단하게 문 느낌보다는 얕거나 헐겁게 잡힌 경우가 있었다.

### 시도별 메모

1. 성공. 다만 조금 빨리 잡은 느낌이 있었음.
2. 실패. 파이펫 위치를 조금 옮기자 바로 실패. 파이펫을 실제로 보고 잡는다기보다 특정 위치를 외운 것일 가능성이 제기됨.
3. 성공. 하지만 역시 조금 빨리 잡는 느낌이 있었고, 파이펫을 꽉 잡기보다는 헐겁게 잡은 느낌.
4. 실패. 파이펫을 앞뒤 방향으로 옮기면 어느 정도 따라가지만, 좌우 이동에는 대응이 약함. 로봇 기준으로 먼 위치에 둔 경우 좀 더 오른쪽으로 가야 했으나 헛손질함. 하드웨어 reach/작업공간 한계 가능성도 있음.
5. 실패. 그리퍼가 갑자기 `grasp`하는 현상 발생.
6. 실패. 5번째와 유사하게 갑작스러운/이른 `grasp` 발생.
7. 실패. 그리퍼가 너무 빨리 닫힘.
8. 실패. 파이펫을 그리퍼와 더 가까운 위치에 뒀는데도 너무 빨리 잡아서 실패.
9. 성공. 가장 완벽한 성공. 파이펫은 로봇과 가까운 곳에 위치.
10. 실패. 너무 빨리 잡음.

### 70k 대비 변화

- grasp 데이터 증강을 하지 않았던 이전 학습 모델보다 결과는 좋아졌다.
- 적어도 파이펫 방향으로 접근하고, 일부 조건에서는 실제로 잡는 동작까지 수행한다.
- 하지만 80k 모델도 핵심 실패는 여전히 `grasp` 타이밍이 너무 빠른 것.
- 파이펫이 로봇과 가까운 위치에서는 성공 가능성이 높아 보이나, 위치를 조금 바꾸거나 좌우로 옮기면 성능이 크게 떨어진다.

### 로그 해석: 갑자기 grasp한 원인

로그상 그리퍼가 임의로 닫힌 것이 아니라, 모델 출력이 `grasp`로 해석되어 gate를 통과한 뒤 `/gripper/grasp` 서비스가 호출된 것으로 보인다.

근거:

```text
grasp delay 시작: 8 ticks 동안 그리퍼 hold
grasp delay 완료: 안정 조건 확인 시작
grasp gate 통과: confirm=8/8, delta_norm=0.0006
grip_preset_node: grasp: [0.0, 0.0, 350.0, 350.0, 350.0, 0.0]
Mark7SystemHardware: Tx: [0,0,350,350,350,0]
```

위 흐름은 다음 의미다.

```text
모델이 raw_grip_cmd=grasp 계열 신호를 냄
-> inference_node가 8 tick delay를 시작
-> 이후 grasp가 연속 조건을 만족
-> delta_norm이 threshold보다 작다고 판단
-> /gripper/grasp 서비스 호출
-> Mark7에 실제 grasp target 전송
```

따라서 현재 "갑자기 닫힘"은 Mark7 하드웨어/시리얼 버그라기보다는, ACT 모델이 아직 잘못된 위치에서도 `grasp`를 내는 문제에 가깝다.

### 추가로 발견된 코드/설정 이슈

실행 로그에 아래 에러가 반복됨.

```text
indy7_tcp_fk.py 없음:
/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ros2_ws/ai/data_conversion/npz_to_lerobot/indy7_tcp_fk.py
```

현재 추론은 `use_tf_ee_pose=true`라 TF(`world <- tcp`)를 우선 사용하므로 즉시 치명적이지는 않지만, FK fallback 경로가 잘못되어 있다.
TF가 실패하면 학습 때 사용한 FK 정의와 동일한 `ee_pose`를 넣지 못할 수 있다.

### 현재 판단

- 80k 모델은 70k보다 좋아졌지만, 아직 안정적인 실기 정책은 아니다.
- 실패의 중심은 "파이펫 방향 탐색"보다 "잡아도 되는 정확한 최종 위치 판단"에 있다.
- 특히 좌우 위치 변화와 먼 위치 배치에 약하다.
- 모델이 `grasp`를 너무 빨리 내는 경향이 강하므로, 단순 delay/gate만으로는 한계가 있다.

### 다음 개선 우선순위

1. `grasp`를 잘못 내는 모델 출력 자체를 줄이기 위해, grasp 직전/직후 데이터를 더 많이 수집한다.
2. 파이펫 좌우 위치 변화와 먼 위치 배치를 포함한 데이터셋을 보강한다.
3. FK fallback 경로 오류를 수정해 26D `ee_pose` 입력 안정성을 높인다.
4. `grasp_max_delta_norm` 기준만으로는 "정말 파이펫이 그리퍼 안에 들어왔는지"를 알 수 없으므로, wrist image 기반 `grasp_ready` 검증기를 추가 검토한다.

---

## 2026-05-12 Early-Grasp 방지 패치 및 다음 실행안

### 로그 해석 보강

080000 모델 실기 로그에서 갑작스러운 `grasp`는 수동 입력이나 Mark7 단독 오동작이 아니라, 모델 출력이 `grasp`로 해석되어 `inference_node` gate를 통과한 흐름으로 판단한다.

중요한 로그 흐름:

```text
grasp delay 시작
grasp gate 통과: confirm=8/8, delta_norm=0.0006
grip_preset_node: grasp: [0.0, 0.0, 350.0, 350.0, 350.0, 0.0]
```

즉, `inference_node`가 ZMQ 모델 출력의 gripper action을 받아 `/gripper/grasp` 서비스를 호출한 것이다.

주의할 점:

- `use_zmq_sidecar:=true`일 때 실제로 로드되는 모델은 ROS launch 명령의 `model_path`가 아니라, 별도 터미널에서 실행한 `zmq_act_server --model-path ...` 쪽이다.
- 따라서 ZMQ 서버 터미널에서 실제 경로가 `.../act_pipet_extended_depth_100_grasp_focus/checkpoints/080000` 또는 그 안의 `pretrained_model`로 뜨는지 반드시 확인해야 한다.

### 추가 코드 수정

기존 gate는 `grasp_delay_steps`, `grasp_confirm_steps`, `grasp_max_delta_norm`으로 너무 이른 grasp를 줄였지만, 시작 직후 모델이 계속 `grasp`를 내면 짧은 delay 후 바로 닫힐 수 있었다.

이를 막기 위해 다음 파라미터를 추가했다.

```text
grasp_min_elapsed_steps
grasp_min_motion_rad
enable_gripper
```

의도:

- `grasp_min_elapsed_steps`: 추론 시작 후 최소 tick 수 전에는 grasp를 무조건 보류.
- `grasp_min_motion_rad`: 시작 자세에서 관절 기준으로 일정량 이상 움직이기 전에는 grasp를 보류.
- `enable_gripper`: 디버깅용. `false`이면 팔은 움직이지만 그리퍼 서비스 호출은 차단.

코드 반영 위치:

- `ros2_ws/src/pipet_inference/pipet_inference/inference_node.py`
  - 새 파라미터 선언 및 로그 출력
  - `_gate_gripper_cmd()`에서 최소 elapsed/motion 조건 검사
  - `_maybe_gripper_service()`에서 `enable_gripper=false` 시 서비스 호출 차단
- `ros2_ws/src/pipet_bringup/launch/inference.launch.py`
  - 새 launch argument 노출

### 다음 테스트 실행 명령 변경

기존 실행 명령에 아래 파라미터를 추가해서 테스트한다.

```text
grasp_min_elapsed_steps:=50
grasp_min_motion_rad:=0.015
grasp_delay_steps:=12
grasp_confirm_steps:=12
grasp_max_delta_norm:=0.006
```

의미:

- 20Hz 기준 `50 tick`은 약 2.5초.
- 시작하자마자 뜬금없이 닫는 현상을 차단한다.
- 실제로 관절이 조금이라도 움직인 뒤에만 grasp 후보를 받는다.
- 너무 늦게 잡으면 `grasp_min_elapsed_steps`를 40으로 낮추고, 아직 빨리 잡으면 60으로 올린다.

실제 테스트 명령:

```bash
./run_scripts/40_inference_ros.sh \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/080000 \
  192.168.1.10 \
  /dev/ttyACM0 \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/mujoco_env/generated/indy7_mujoco.urdf \
  26 \
  autonomy_enabled:=true \
  use_zmq_sidecar:=true \
  zmq_endpoint:=tcp://127.0.0.1:5560 \
  image_target_height:=360 \
  image_target_width:=480 \
  grasp_min_elapsed_steps:=50 \
  grasp_min_motion_rad:=0.015 \
  grasp_delay_steps:=12 \
  pre_grasp_delta_scale:=1.15 \
  grasp_confirm_steps:=12 \
  grasp_max_delta_norm:=0.006 \
  max_joint_speed_rad_s:=0.25
```

팔 접근 경로만 먼저 확인하고 싶으면 아래를 추가한다.

```text
enable_gripper:=false
```

이 경우 모델과 팔 명령은 그대로 동작하지만 Mark7 grasp/open/press/release 서비스 호출은 차단된다.

---

## 2026-05-12 Early-Grasp 방지 패치 후 배치 실험

### 테이블/로봇 배치 기록

- 위에서 봤을 때 Indy7과 테이블 사이 거리: 약 40cm
- 테이블 높이: 72cm
- 테이블 너비: 95cm

### 실험 조건

이전 080000 모델에 early-grasp 방지 파라미터를 강화한 상태로 테스트.

핵심 의도:

- 시작 직후/뜬금없는 위치에서 닫는 문제를 막기 위해 `grasp_min_elapsed_steps`, `grasp_min_motion_rad`, 더 강한 confirm/delta gate를 사용.
- 그러나 이번 실험에서는 반대로 너무 보수적으로 동작해 `grasp`가 거의 나오지 않는 문제가 관찰됨.

### 시도별 결과

1. 실패.
   - 테이블 중심 기준, 테이블 바깥에서 5cm 더 들어간 위치에서 시도.
   - 로봇이 왼쪽으로 이동하지 못함.

2. 실패.
   - 로봇 기준으로 테이블을 봤을 때, 왼쪽에서 51.5cm 들어온 위치.
   - 테이블 가장자리에서 4cm 들어간 위치.
   - 그리퍼 동작 없이 계속 앞으로 감.

3. 실패.
   - 2차와 거의 동일한 위치에서 왼쪽으로 2cm 이동한 위치.
   - 실패.

### 판단

- 실험 중단.
- 현재 early-grasp 방지 파라미터는 너무 보수적일 가능성이 큼.
- 이전 문제는 "너무 빨리 잡음"이었고, 이번 문제는 "너무 안 잡음"으로 바뀜.
- 즉 gate가 모델의 잘못된 early grasp를 막는 데는 효과가 있을 수 있으나, 현재 설정에서는 정상 grasp 후보까지 과하게 차단하는 것으로 보인다.

### 다음 튜닝 방향

- `grasp_min_elapsed_steps`를 50에서 40 또는 30으로 낮춘다.
- `grasp_confirm_steps`를 12에서 8로 낮춘다.
- `grasp_max_delta_norm`을 0.006에서 0.008 또는 0.010으로 완화한다.
- `grasp_min_motion_rad`가 너무 높은지 확인하고, 필요 시 0.010 또는 0.0으로 낮춰 비교한다.

추천 완화안:

```text
grasp_min_elapsed_steps:=40
grasp_min_motion_rad:=0.010
grasp_delay_steps:=8
pre_grasp_delta_scale:=1.15
grasp_confirm_steps:=8
grasp_max_delta_norm:=0.008
max_joint_speed_rad_s:=0.25
```

더 공격적인 완화안:

```text
grasp_min_elapsed_steps:=30
grasp_min_motion_rad:=0.0
grasp_delay_steps:=8
pre_grasp_delta_scale:=1.15
grasp_confirm_steps:=8
grasp_max_delta_norm:=0.010
max_joint_speed_rad_s:=0.25
```

---

## 2026-05-12 위치 좌표 기록 기반 실험

### 좌표계 정의

테이블과 로봇 배치를 기준으로 이후 실험 위치를 좌표로 기록하기 시작했다.

- 테이블과 Indy7 사이 거리: 약 40cm
- 테이블 높이: 72cm
- 테이블 너비: 95cm
- 테이블 너비 방향을 `x`축으로 둔다.
  - 테이블 가운데를 `x=0`
  - 로봇이 테이블을 바라봤을 때 오른쪽을 `+x`
  - 왼쪽을 `-x`
- 깊이 방향을 `y`축으로 둔다.
  - Indy7 쪽 테이블 가장자리를 `y=0`
  - Indy7에서 멀어질수록 `+y`

위치 표기는 `x*y` 형태로 기록한다.

### 1~16차 결과

| 차수 | 위치 | 결과 | 메모 |
|---|---:|---|---|
| 1차 | `0*5` | 실패 | 너무 빨리 잡음. |
| 2차 | `2*5` | 실패 | 좌우 위치를 못 잡음. |
| 3차 | `4*3.5` | 성공 | 좌우 위치를 맞춰놓고 시작했을 때 성공. |
| 4차 | `4*5` | 성공 | Indy7을 일부러 오른쪽 방향을 바라보게 움직여 둠. 오른쪽에서 왼쪽으로 들어오면서 거리 잡는 듯함. |
| 5차 | `0*10` | 실패 | 위치를 아예 못 잡음. grasp도 안 함. |
| 6차 | `4*10` | 실패 | 5차와 비슷하게 실패. |
| 7차 | `4*5` | 성공 | 같은 근방 위치에서는 다시 성공. y축/깊이 방향이 더 큰 문제일 가능성 제기. |
| 8차 | `0*5` | 실패 | 5/6차와 비슷한 형태로 실패. |
| 9차 | `2*5` | 실패 | 5/6/8차와 비슷한 형태로 실패. |
| 10차 | `4*0` | 실패 | 5/6/8차와 비슷한 형태로 실패. |
| 11차 | `5.5*4.5` | 실패 | grasp는 했지만 조금 높게 잡아서 실패. |
| 12차 | `5.5*4.5` | 실패 | 같은 위치인데 11차와 다르게 실패. 시작 자세도 중요할 가능성. 이후 잡기 직전 형태로 Indy7/그리퍼 위치를 가져다 놓고 재시도했지만 너무 빨리 잡음. |
| 13차 | `5.5*4.5` 근방 | 실패 | 조금 더 왼쪽으로 이동했어야 함. |
| 14차 | 미기록 | 실패 | 그리퍼를 완전히 떨어뜨려 놓고 처음부터 찾아가게 했는데, 오히려 가장 아까운 시도였음. |
| 15차 | 미기록 | 실패 | 이번에도 좌우 위치를 못 잡음. |
| 16차 | `2*3.5` | 실패 | 빨리 잡는 문제라기보다 더 깊숙이 들어가서 잡음. 원래 실행 명령어를 써도 괜찮을 것 같다는 판단. |

### 관찰 요약

- 080000 grasp-focus 모델은 특정 위치(`x≈4`, `y≈3.5~5`)에서는 성공 가능성이 있다.
- `x=0`, `x=2` 또는 `y=10` 쪽에서는 위치를 잘 못 잡거나 grasp 자체가 나오지 않는 경우가 많았다.
- 좌우(`x`) 일반화가 약하고, 깊이(`y`)가 커질수록 실패가 늘어나는 것으로 보인다.
- 같은 좌표에서도 시작 자세에 따라 결과가 크게 달라졌다.
- 이는 모델이 파이펫을 완전히 일반화해서 추적한다기보다, 학습 데이터에서 자주 본 접근 자세/위치/카메라 구도에 강하게 의존할 가능성을 시사한다.
- early-grasp 방지 gate를 과하게 조이면 grasp가 안 나오고, 너무 풀면 빨리 잡는 문제가 다시 나타난다.
- 16차까지 보면 단순 gate 튜닝보다 **데이터 분포와 시작 자세/작업공간 조건**이 더 큰 변수로 보인다.

### 현재 판단

- `grasp_focus` 증강은 이전보다 분명히 좋아졌지만, 아직 실기 성공률은 특정 위치와 시작 자세에 많이 의존한다.
- 특히 좌우 위치 변화에 약하고, 테이블 깊이 방향으로 멀어지면 실패가 많다.
- 일부 실패는 “너무 빨리 잡음”이 아니라 “더 깊숙이 들어가서 잡아야 하는 위치 판단 실패” 또는 “좌우 정렬 실패”에 가깝다.
- 현재 gate를 너무 보수적으로 조정하는 것보다, 일단 원래 실행 명령어 또는 약한 gate 설정으로 돌아가 비교하는 것도 타당하다.

### 다음 데이터 수집 제안

- 좌표계를 유지하고, 각 좌표별 성공/실패를 계속 기록한다.
- `x=0`, `x=2`, `x=4`, `x=5.5`와 `y=3.5`, `y=5`, `y=10` 조합을 의도적으로 나눠 수집한다.
- 성공한 `4*3.5`, `4*5` 근방뿐 아니라 실패한 `0*5`, `2*5`, `0*10`, `4*10` 근방의 성공 데모를 추가해야 한다.
- 같은 파이펫 좌표에서도 시작 자세를 다양하게 바꿔 수집한다.

### 추가 관찰: 가림막 제거 실험

가림막을 제거한 상태에서 같은 계열 테스트를 진행했다.

결과:

- 위치 `4*5`에서 1차 시도 실패.
- 가림막 제거 후 잘못된 `grasp`가 3번 연속 발생.
- 이후 약 10회 연속으로 파이펫 방향으로 이동하지 못하고, 파이펫 위치를 아예 못 잡는 양상이 반복됨.
- 즉, 단순히 grasp 타이밍 문제가 아니라 시각 입력 자체가 크게 흔들린 것으로 보인다.

판단:

- 현재 모델/카메라/데이터 분포에서는 **가림막이 필수**.
- 가림막이 없으면 배경/반사/테이블 주변 물체가 들어와 파이펫 위치 인식이 무너지는 것으로 추정.
- 향후 데이터 수집과 추론 테스트는 동일한 가림막 조건을 유지해야 한다.
- 만약 가림막 없는 환경도 목표라면, 그 조건을 포함한 별도 데이터 수집이 필요하다.
