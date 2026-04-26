#!/usr/bin/env bash
set -euo pipefail

# Run fixed training recipe for 26.04.20 half data.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"
exec bash ai/lerobot/train_26_04_20_half_data.sh
