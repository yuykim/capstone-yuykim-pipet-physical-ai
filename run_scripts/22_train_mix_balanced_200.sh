#!/usr/bin/env bash
set -euo pipefail

# Build a balanced 200-episode training set and train ACT:
# - no-cover original 50
# - no-cover grasp-focus 50, from different source episodes
# - with-cover original 50
# - with-cover grasp-focus 50

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

source /home/sirlab/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

set -o pipefail

export PYTHONPATH="${REPO_ROOT}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${REPO_ROOT}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs

NO_COVER_ORIG="${REPO_ROOT}/ros2_ws/episodes/success/260503_half_data_100"
NO_COVER_FOCUS="${REPO_ROOT}/ros2_ws/episodes/success/260503_half_data_100_grasp_focus"
COVER_ORIG="${REPO_ROOT}/ros2_ws/episodes/success/260510_pipet_up_data_with_cover"
COVER_FOCUS_ONLY="${REPO_ROOT}/ros2_ws/episodes/success/260510_pipet_up_data_with_cover_focus_only"
MIX_DIR="${REPO_ROOT}/ros2_ws/episodes/success/260512_mix_balanced_200"
DATASET_DIR="${REPO_ROOT}/ai/datasets/pipet_extended_depth_mix_balanced_200"
OUT_DIR="${REPO_ROOT}/ai/models/act_pipet_extended_depth_mix_balanced_200"

rm -rf "${MIX_DIR}" "${DATASET_DIR}" "${OUT_DIR}"

python3 - <<'PY'
from pathlib import Path
import os
import re
import shutil

import numpy as np

root = Path("/home/sirlab/WORKSPACE/capstone-yuykim/capstone-yuykim-pipet-physical-ai")

no_cover_orig = root / "ros2_ws/episodes/success/260503_half_data_100"
no_cover_focus = root / "ros2_ws/episodes/success/260503_half_data_100_grasp_focus"
cover_orig = root / "ros2_ws/episodes/success/260510_pipet_up_data_with_cover"
cover_focus_only = root / "ros2_ws/episodes/success/260510_pipet_up_data_with_cover_focus_only"
mix = root / "ros2_ws/episodes/success/260512_mix_balanced_200"

cover_focus_only.mkdir(parents=True, exist_ok=True)
if mix.exists():
    shutil.rmtree(mix)
mix.mkdir(parents=True, exist_ok=True)


def link(src: Path, dst: Path) -> None:
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def orig_id_from_focus_name(name: str) -> str:
    match = re.search(r"(episode_\d{8}_\d{6}_success\.npz)$", name)
    return match.group(1) if match else name


def make_focus(src: Path, dst: Path, pre: int = 80, post: int = 40) -> None:
    ep = np.load(src, allow_pickle=False)
    actions = ep["gripper_actions"]
    idxs = np.where(actions == 1)[0]
    if len(idxs) == 0:
        raise RuntimeError(f"no grasp action in {src.name}")

    center = int(idxs[0])
    start = max(0, center - pre)
    end = min(len(actions), center + post)

    out = {}
    for key in ep.files:
        arr = ep[key]
        if hasattr(arr, "shape") and len(arr.shape) > 0 and arr.shape[0] == len(actions):
            out[key] = arr[start:end]
        else:
            out[key] = arr
    np.savez_compressed(dst, **out)


# 1) Generate missing with-cover grasp-focus only, not duplicated originals.
cover_orig_files = sorted(cover_orig.glob("*.npz"))[:50]
for i, src in enumerate(cover_orig_files):
    dst = cover_focus_only / f"episode_cover_focus_{i:06d}_{src.name}"
    if not dst.exists():
        make_focus(src, dst)

# 2) Pick no-cover original 50 and no-cover focus 50 from non-overlapping source episodes.
no_orig_files = sorted(no_cover_orig.glob("*.npz"))
no_orig_a = no_orig_files[:50]
no_orig_b_ids = {p.name for p in no_orig_files[50:100]}

no_focus_files = [
    p
    for p in sorted(no_cover_focus.glob("*grasp_focus*.npz"))
    if orig_id_from_focus_name(p.name) in no_orig_b_ids
][:50]

cover_focus_files = sorted(cover_focus_only.glob("episode_*.npz"))[:50]

groups = [
    ("no_cover_orig", no_orig_a),
    ("no_cover_focus", no_focus_files),
    ("with_cover_orig", cover_orig_files),
    ("with_cover_focus", cover_focus_files),
]

counter = 0
for label, files in groups:
    print(label, len(files), flush=True)
    if len(files) != 50:
        raise SystemExit(f"{label} expected 50, got {len(files)}")
    for src in files:
        # convert.py loads only episode_*.npz.
        dst = mix / f"episode_mix_{counter:06d}_{label}_{src.name}"
        link(src, dst)
        counter += 1

print("mix output:", mix, flush=True)
print("mix total:", len(list(mix.glob("episode_*.npz"))), flush=True)
PY

python ai/lerobot/run_lerobot_train.py \
  --episodes_dir "${MIX_DIR}" \
  --dataset_output_dir "${DATASET_DIR}" \
  --dataset_repo_id pipet_extended_depth_mix_balanced_200 \
  --output_dir "${OUT_DIR}" \
  --job_name act_pipet_extended_depth_mix_balanced_200 \
  --state_profile extended \
  --include_depth \
  --fk_urdf "${REPO_ROOT}/mujoco_env/generated/indy7_mujoco.urdf" \
  --fk_tcp_frame tcp \
  --fk_joint_names joint0,joint1,joint2,joint3,joint4,joint5 \
  --image_resize_to 360x480 \
  --steps 80000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 4 \
  --device cuda \
  2>&1 | tee "ai/logs/train_act_pipet_extended_depth_mix_balanced_200_$(date +%Y%m%d_%H%M%S).log"
