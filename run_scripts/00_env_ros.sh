#!/usr/bin/env bash
set -euo pipefail

# Source ROS2 + workspace overlays for this repository.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source /opt/ros/humble/setup.bash
if [[ -f "${REPO_ROOT}/install/setup.bash" ]]; then
  source "${REPO_ROOT}/install/setup.bash"
fi
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo "[env] ROS2 ready"
echo "[env] REPO_ROOT=${REPO_ROOT}"
echo "[env] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}"
