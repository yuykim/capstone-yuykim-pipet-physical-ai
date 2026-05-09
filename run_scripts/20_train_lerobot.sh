#!/usr/bin/env bash
set -euo pipefail

# Generic LeRobot training launcher wrapper.
# Usage:
#   ./run_scripts/20_train_lerobot.sh <episodes_dir> <dataset_output_dir> <dataset_repo_id> <job_name> [device] [extra run_lerobot_train.py args...]
#
# extended 상태(26D) + ee FK + depth 예시 (6번째 인자부터 python에 그대로 전달):
#   ./run_scripts/20_train_lerobot.sh episodes/success/mybatch ai/datasets/my_ds my_ds act_my cuda \
#     --state_profile extended --fk_urdf /ABS/path/indy7.urdf --include_depth
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

EPISODES_DIR="${1:-episodes}"
DATASET_OUTPUT_DIR="${2:-ai/datasets/pipet_dataset}"
DATASET_REPO_ID="${3:-pipet_dataset}"
JOB_NAME="${4:-act_pipet}"
DEVICE="${5:-cuda}"

cd "${REPO_ROOT}"

EXTRA=()
if [[ "${#}" -gt 5 ]]; then
  shift 5
  EXTRA=("$@")
fi

exec python ai/lerobot/run_lerobot_train.py \
  --episodes_dir "${EPISODES_DIR}" \
  --dataset_output_dir "${DATASET_OUTPUT_DIR}" \
  --dataset_repo_id "${DATASET_REPO_ID}" \
  --job_name "${JOB_NAME}" \
  --device "${DEVICE}" \
  "${EXTRA[@]}"
