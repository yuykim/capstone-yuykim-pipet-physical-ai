#!/usr/bin/env bash
set -euo pipefail

# Source ROS2 + workspace overlays for this repository.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ROS setup scripts may reference unset variables internally, so source them
# with nounset disabled and restore the caller's strict mode afterward.
set +u
source /opt/ros/humble/setup.bash
if [[ -f "${REPO_ROOT}/ros2_ws/install/setup.bash" ]]; then
  source "${REPO_ROOT}/ros2_ws/install/setup.bash"
elif [[ -f "${REPO_ROOT}/install/setup.bash" ]]; then
  source "${REPO_ROOT}/install/setup.bash"
fi
set -u
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo "[env] ROS2 ready"
echo "[env] REPO_ROOT=${REPO_ROOT}"
echo "[env] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}"
