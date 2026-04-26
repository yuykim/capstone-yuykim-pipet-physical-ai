# Pipette Localization Recovery Playbook

파이펫 접근 시 "근처까지 가지만 오프셋 발생" 문제를 빠르게 줄이기 위한 실행 가이드다.

## 1) 전처리 정합 체크 (align-preprocess)

학습/추론 해상도와 데이터셋 메타 정합을 먼저 확인한다.

```bash
python ai/diagnostics/check_preprocess_alignment.py \
  --train_config ai/models/26.04.20_half_data/checkpoints/last/pretrained_model/train_config.json \
  --inference_image_height 360 \
  --inference_image_width 480 \
  --action_delta_scale 8.0
```

판정:
- `RESULT: PASS`이면 해상도/repo_id 기준 정합
- `FAIL`이면 학습-추론 입력 불일치가 1순위 원인

## 2) 오프라인 제어 vs 시각 분리 (offline-error-split)

현재 데이터셋의 `delta_q` 분포를 기준으로, 추론 파라미터에서 클리핑 과다 여부를 본다.

```bash
python ai/diagnostics/offline_error_split.py \
  --episodes_dir ros2_ws/episodes/success \
  --action_delta_scale 8.0 \
  --max_delta_rad 0.25
```

판정:
- `CONTROL_RISK`: 제어 스케일/클립 영향 큼
- `VISION_RISK`: 가림/조명/배경 등 시각 분포 영향 큼

## 3) 데이터 수집 확장 프로토콜 (dataset-expansion-targeted)

목표:
- 성공 에피소드 50~100개
- 오프셋 취약 분포(손 가림/조명 변화/파이펫 위치 미세 랜덤화) 포함

수집 블록(각 10~20 episode):
- Block A: 기준 세팅(기존과 동일)
- Block B: 손 부분 가림 포함
- Block C: 조명 강도/각도 소폭 변화
- Block D: 파이펫 위치 5~15mm 랜덤 오프셋

규칙:
- 에피소드 단위 split (train/val 누수 금지)
- 성공/실패/폐기 라벨 엄격 분리
- 시작 pose와 카메라 고정값 기록

## 4) 입력 확장 실험 분기 (state-feature-branch)

`convert.py`는 두 가지 상태 프로파일을 지원한다.

- baseline: `q+dq+tau` (18D)
- extended: `+ee_pose(7D)+gripper_state(1D)` (총 26D)

추가로 depth 입력을 별도 채널로 포함할 수 있다.

예시:

```bash
python ai/lerobot/run_lerobot_train.py \
  --episodes_dir ros2_ws/episodes/success \
  --dataset_output_dir ai/datasets/pipet_extended \
  --dataset_repo_id pipet_extended \
  --job_name act_pipet_extended \
  --state_profile extended \
  --include_depth \
  --device cuda
```

주의:
- `--state_profile extended`는 NPZ에 `ee_pose`, `gripper_state`가 없으면 해당 값을 0으로 패딩한다.
- `--include_depth`는 depth 키가 없으면 변환 단계에서 실패하도록 설계했다.

## 5) 실험 채택 기준 (metrics-gate)

각 실험은 최소 20회 반복 후 아래 3지표를 기록한다.

- SuccessRate: 파지 성공/총 시도
- FirstApproachOffsetMm: 첫 접근 시 파이펫 중심 오프셋(mm)
- TimeToContactSec: 시작~첫 접촉 시간(sec)

채택 규칙:
- SuccessRate 증가 + FirstApproachOffsetMm 감소를 동시에 만족할 때만 채택
- 둘 중 하나만 개선되면 보류 (추가 반복 검증)

권장 로그 포맷(CSV):

```text
experiment_id,trial_id,success,first_approach_offset_mm,time_to_contact_sec,notes
```
