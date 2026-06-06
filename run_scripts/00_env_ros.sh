#!/usr/bin/env bash
set -euo pipefail

# Source ROS2 + workspace overlays for this repository.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ROS setup scripts may reference unset variables internally, so source them
# with nounset disabled and restore the caller's strict mode afterward.
set +u
# ROS distro 자동 감지 (이 머신은 jazzy, 옛 노트북은 humble). 환경변수 ROS_DISTRO로 강제 가능.
if [[ -n "${ROS_DISTRO:-}" && -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
elif [[ -f /opt/ros/jazzy/setup.bash ]]; then
  source /opt/ros/jazzy/setup.bash
elif [[ -f /opt/ros/humble/setup.bash ]]; then
  source /opt/ros/humble/setup.bash
else
  echo "[env] ERROR: ROS2 setup.bash 를 찾을 수 없음 (/opt/ros/{jazzy,humble})" >&2
  return 1 2>/dev/null || exit 1
fi

# Jazzy packages use Ubuntu's Python 3.12. Keep an active Conda base
# environment from redirecting ROS and colcon to a different Python. Include
# user-installed ROS utilities such as xacro before the system paths.
export PATH="${HOME}/.local/bin:/usr/bin:/bin:${PATH}"

if [[ -f "${REPO_ROOT}/ros2_ws/install/setup.bash" ]]; then
  source "${REPO_ROOT}/ros2_ws/install/setup.bash"
elif [[ -f "${REPO_ROOT}/install/setup.bash" ]]; then
  source "${REPO_ROOT}/install/setup.bash"
fi
set -u
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo "[env] ROS2 ready"
echo "[env] ROS_DISTRO=${ROS_DISTRO}"
echo "[env] python3=$(command -v python3) ($(python3 --version 2>&1))"
echo "[env] REPO_ROOT=${REPO_ROOT}"
echo "[env] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}"

if [[ -e /dev/ttyACM0 && ! -r /dev/ttyACM0 ]]; then
  echo "[env] WARNING: /dev/ttyACM0 is not accessible in this login session." >&2
  echo "[env] Log out/in after joining dialout, or launch with: sg dialout -c '<command>'" >&2
fi
