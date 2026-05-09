#!/usr/bin/env bash
set -euo pipefail

# Launch real-robot inference bringup.
# Usage:
#   ./run_scripts/40_inference_ros.sh <model_path> [indy_ip] [mark7_port] [fk_urdf_path] [state_target_dim] [extra launch args...]
#
# extended(26D) 학습 모델 예 (TF + FK fallback):
#   ./run_scripts/40_inference_ros.sh /path/to/checkpoints/last 192.168.1.10 /dev/ttyACM0 /ABS/indy7.urdf 26
# grasp gate 보정 예:
#   ./run_scripts/40_inference_ros.sh /path/to/checkpoints/100000 192.168.1.10 /dev/ttyACM0 /ABS/indy7.urdf 26 grasp_delay_steps:=8 grasp_confirm_steps:=8 grasp_max_delta_norm:=0.008
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODEL_PATH="${1:-}"
INDY_IP="${2:-192.168.1.10}"
MARK7_PORT="${3:-/dev/ttyACM0}"
FK_URDF_PATH="${4:-}"
STATE_TARGET_DIM="${5:-0}"

if [[ -z "${MODEL_PATH}" ]]; then
  echo "Usage: $0 <model_path> [indy_ip] [mark7_port] [fk_urdf_path] [state_target_dim] [extra launch args...]" >&2
  exit 1
fi

EXTRA=()
if [[ "${#}" -gt 5 ]]; then
  shift 5
  EXTRA=("$@")
fi

source "${SCRIPT_DIR}/00_env_ros.sh"
cd "${REPO_ROOT}"

LAUNCH_ARGS=(
  "indy_ip:=${INDY_IP}"
  "mark7_port:=${MARK7_PORT}"
  "model_path:=${MODEL_PATH}"
)
if [[ -n "${FK_URDF_PATH}" ]]; then
  LAUNCH_ARGS+=("fk_urdf_path:=${FK_URDF_PATH}")
fi
if [[ -n "${STATE_TARGET_DIM}" && "${STATE_TARGET_DIM}" != "0" ]]; then
  LAUNCH_ARGS+=("state_target_dim:=${STATE_TARGET_DIM}")
fi
LAUNCH_ARGS+=("${EXTRA[@]}")

exec ros2 launch pipet_bringup inference.launch.py "${LAUNCH_ARGS[@]}"
