#!/usr/bin/env bash
set -euo pipefail

# Check training/inference preprocessing alignment.
# Usage:
#   ./run_scripts/60_check_preprocess_alignment.sh <train_config> [img_h] [img_w] [action_delta_scale]
#
# Example:
#   ./run_scripts/60_check_preprocess_alignment.sh \
#     ai/models/26.04.20_half_data/checkpoints/last/pretrained_model/train_config.json \
#     360 480 8.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TRAIN_CONFIG="${1:-${REPO_ROOT}/ai/models/26.04.20_half_data/checkpoints/last/pretrained_model/train_config.json}"
IMG_H="${2:-0}"
IMG_W="${3:-0}"
DELTA_SCALE="${4:-1.0}"

cd "${REPO_ROOT}"
exec python3 ai/diagnostics/check_preprocess_alignment.py \
  --train_config "${TRAIN_CONFIG}" \
  --inference_image_height "${IMG_H}" \
  --inference_image_width "${IMG_W}" \
  --action_delta_scale "${DELTA_SCALE}"
