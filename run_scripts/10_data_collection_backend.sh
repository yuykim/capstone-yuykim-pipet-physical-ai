#!/usr/bin/env bash
set -euo pipefail

# Launch full data-collection backend (Indy7 + Mark7 + RealSense + collector)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

INDY_IP="${1:-192.168.1.10}"
MARK7_PORT="${2:-/dev/ttyACM0}"

source "${SCRIPT_DIR}/00_env_ros.sh"
cd "${REPO_ROOT}"

exec ros2 launch pipet_bringup data_collection.launch.py   indy_ip:="${INDY_IP}"   mark7_port:="${MARK7_PORT}"
