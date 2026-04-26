#!/usr/bin/env bash
set -euo pipefail

# Run integrated teleop node for data collection workflow.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${SCRIPT_DIR}/00_env_ros.sh"
cd "${REPO_ROOT}"

exec ros2 run pipet_system_teleop system_teleop_node
