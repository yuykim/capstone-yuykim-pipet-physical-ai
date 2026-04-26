#!/usr/bin/env bash
# 26.04.20 half data LeRobotDataset으로 ACT 학습: 10만 스텝, 1만 스텝마다 체크포인트 저장.
# 체크포인트: <repo>/ai/models/26.04.20_half_data/checkpoints/<step>/
#
# HF 캐시는 ai/.cache 로 둔다(홈 ~/.cache 가득 참 방지).
# 학습은 기본 비스트리밍(LeRobotDataset). --dataset.streaming 은 Accelerate+IterableDataset에서
# 첫 배치 None 버그가 있어 이 스크립트에서는 쓰지 않는다. 디스크가 극도로 부족할 때만 수동으로
# run_lerobot_train.py 에 --dataset_streaming 을 추가해 볼 것(OOM·버그 가능).
#
# 주의: LeRobot은 --resume 이 아니면 output_dir 이 이미 디렉터리로 있으면 시작하지 않는다.
#       (예전 스크립트의 mkdir 때문에 생긴 빈 폴더도 동일) 처음부터 다시 돌리려면:
#         rm -rf "${REPO_ROOT}/ai/models/26.04.20_half_data"
#       이 스크립트는 mkdir 하지 않는다 — 학습이 output_dir 을 생성한다.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MINICONDA="${MINICONDA:-${HOME}/miniconda3}"

source "${MINICONDA}/etc/profile.d/conda.sh"
conda activate lerobot

export PYTHONPATH="${REPO_ROOT}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1

# HF datasets 가 parquet 를 재처리할 때 기본은 ~/.cache — 홈 디스크가 가득 차면 Errno 28.
# 캐시를 저장소 여유가 있는 리포지토리 쪽으로 둔다(필요 시 다른 경로로 바꿔도 됨).
export HF_HOME="${REPO_ROOT}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
mkdir -p "${HF_DATASETS_CACHE}"

OUT="${REPO_ROOT}/ai/models/26.04.20_half_data"
LOG_DIR="${REPO_ROOT}/ai/logs"
LOG_FILE="${LOG_DIR}/act_26_04_20_half_data_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "${LOG_DIR}"

python3 "${REPO_ROOT}/ai/lerobot/run_lerobot_train.py" \
  --skip_convert \
  --episodes_dir "${REPO_ROOT}/ros2_ws/episodes/success/26.04.20 half data" \
  --dataset_output_dir "${REPO_ROOT}/ai/datasets/26.04.20_half_data" \
  --dataset_repo_id pipet_26_04_20_half_data \
  --output_dir "${OUT}" \
  --job_name act_26_04_20_half_data \
  --steps 100000 \
  --eval_freq 10000 \
  --log_freq 50 \
  --save_freq 10000 \
  --batch_size 8 \
  --num_workers 2 \
  --device cuda \
  2>&1 | tee "${LOG_FILE}"

exit "${PIPESTATUS[0]}"
