#!/usr/bin/env bash
set -euo pipefail

# Launch real-robot inference bringup.
# Usage:
#   ./run_scripts/40_inference_ros.sh <model_path> [indy_ip] [mark7_port]
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODEL_PATH="${1:-}"
INDY_IP="${2:-192.168.1.10}"
MARK7_PORT="${3:-/dev/ttyACM0}"

if [[ -z "${MODEL_PATH}" ]]; then
  echo "Usage: $0 <model_path> [indy_ip] [mark7_port]" >&2
  exit 1
fi

source "${SCRIPT_DIR}/00_env_ros.sh"
cd "${REPO_ROOT}"

exec ros2 launch pipet_bringup inference.launch.py   indy_ip:="${INDY_IP}"   mark7_port:="${MARK7_PORT}"   model_path:="${MODEL_PATH}"
