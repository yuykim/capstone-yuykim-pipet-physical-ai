#!/usr/bin/env bash
set -euo pipefail

# Generate MuJoCo-ready Indy7+Mark7 model and copy required meshes.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
exec python mujoco_env/scripts/prepare_models.py
