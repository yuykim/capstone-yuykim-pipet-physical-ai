#!/usr/bin/env bash
set -euo pipefail

# Launch the integrated operator GUI with the system Python ROS environment.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${SCRIPT_DIR}/00_env_ros.sh"
cd "${REPO_ROOT}"

export PYTHONPATH="${REPO_ROOT}/ros2_ws/src/pipet_inference:${PYTHONPATH:-}"
exec /usr/bin/python3 -m pipet_inference.operator_gui \
  --repo-root "${REPO_ROOT}" \
  "$@"
