#!/usr/bin/env bash
set -euo pipefail

# Run MuJoCo keyboard teleop (Indy7 Cartesian + Mark7 presets).
# Args are passed directly to keyboard_cartesian_teleop.py.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
exec python mujoco_env/scripts/keyboard_cartesian_teleop.py "$@"
