#!/usr/bin/env bash
set -euo pipefail

# Quick Mark7 preset service calls.
# Usage:
#   ./run_scripts/50_mark7_preset_test.sh open|grasp|press|release
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTION="${1:-open}"

source "${SCRIPT_DIR}/00_env_ros.sh"

case "${ACTION}" in
  open|grasp|press|release)
    exec ros2 service call "/gripper/${ACTION}" std_srvs/srv/Trigger '{}'
    ;;
  *)
    echo "Invalid action: ${ACTION}" >&2
    echo "Allowed: open|grasp|press|release" >&2
    exit 1
    ;;
esac
