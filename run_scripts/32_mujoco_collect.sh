#!/usr/bin/env bash
set -euo pipefail

# Collect NPZ episode from MuJoCo simulation.
# Usage:
#   ./run_scripts/32_mujoco_collect.sh [seconds] [hz] [success|fail]
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SECONDS="${1:-10}"
HZ="${2:-20}"
LABEL="${3:-success}"

cd "${REPO_ROOT}"
if [[ "${LABEL}" == "success" ]]; then
  exec python mujoco_env/scripts/collect_dataset.py --seconds "${SECONDS}" --hz "${HZ}" --success
else
  exec python mujoco_env/scripts/collect_dataset.py --seconds "${SECONDS}" --hz "${HZ}"
fi
