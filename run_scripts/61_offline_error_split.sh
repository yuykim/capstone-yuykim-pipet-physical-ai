#!/usr/bin/env bash
set -euo pipefail

# Offline split diagnostic: control-scale saturation vs vision mismatch risk.
# Usage:
#   ./run_scripts/61_offline_error_split.sh [episodes_dir] [action_delta_scale] [max_delta_rad]
#
# Example:
#   ./run_scripts/61_offline_error_split.sh ros2_ws/episodes/success 8.0 0.25

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

EP_DIR="${1:-${REPO_ROOT}/ros2_ws/episodes/success}"
DELTA_SCALE="${2:-8.0}"
MAX_DELTA="${3:-0.25}"

cd "${REPO_ROOT}"
exec python3 ai/diagnostics/offline_error_split.py \
  --episodes_dir "${EP_DIR}" \
  --action_delta_scale "${DELTA_SCALE}" \
  --max_delta_rad "${MAX_DELTA}"
