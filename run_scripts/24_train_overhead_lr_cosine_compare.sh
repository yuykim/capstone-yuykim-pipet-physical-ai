#!/usr/bin/env bash
set -euo pipefail

# Depth 유무 비교 학습 v2 (lr 상향 + cosine 스케줄러).
#
# 기존 23번 스크립트는 lr=1e-5 constant 라 loss가 0.16에서 평탄했다.
# 이 스크립트는 batch=64 에 맞춰 lr 을 1e-4 로 올리고,
# cosine_decay_with_warmup 스케줄러로 후반부 lr 을 낮춰 loss 를 더 깊이 수렴시킨다.
#
# - act_overhead_depth_cosine   : overhead RGB + overhead depth
# - act_overhead_nodepth_cosine : overhead RGB only
# 두 run 의 유일한 차이는 depth 포함 여부(데이터셋)이고, 학습 HP 는 100% 동일하다.
#
# 사용:
#   ./run_scripts/24_train_overhead_lr_cosine_compare.sh            # depth -> nodepth 순차
#   STAGE=depth   ./run_scripts/24_train_overhead_lr_cosine_compare.sh
#   STAGE=nodepth ./run_scripts/24_train_overhead_lr_cosine_compare.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# --- conda lerobot 환경 + PYTHONPATH ---
source /home/sirlab/miniconda3/etc/profile.d/conda.sh
conda activate lerobot
export PYTHONPATH="${REPO_ROOT}/ai/lerobot_source/lerobot/src:${REPO_ROOT}/ai/data_conversion/npz_to_lerobot:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${REPO_ROOT}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs

# --- 공통 설정 ---
EPISODES_DIR="pipet_data/260510_pipet_up_data_with_cover/SUCCESS"
FK_URDF="${REPO_ROOT}/mujoco_env/generated/indy7_mujoco.urdf"
CONVERT_PY="ai/data_conversion/npz_to_lerobot/convert.py"

# 학습 스텝/스케줄러 (decay_steps 와 steps 를 맞춘다)
STEPS=60000
WARMUP=2000
DECAY_STEPS=60000
PEAK_LR=1e-4
DECAY_LR=1e-6
BATCH=64
NUM_WORKERS=12
SAVE_FREQ=10000

# 변환이 필요한 데이터셋만 만든다(이미 있으면 건너뜀).
convert_dataset() {
  local out_dir="$1" repo_id="$2" depth_flag="$3"
  if [[ -f "${out_dir}/meta/info.json" ]]; then
    echo "[convert] ${out_dir} 이미 존재 → 건너뜀"
    return 0
  fi
  echo "[convert] ${out_dir} 생성 (depth_flag='${depth_flag}')"
  local cmd=(
    python "${CONVERT_PY}"
    --episodes_dir "${EPISODES_DIR}"
    --output_dir "${out_dir}"
    --output_repo_id "${repo_id}"
    --only_success
    --image_resize_to 360x480
    --state_profile extended
    --fk_urdf "${FK_URDF}"
    --cameras overhead_only
  )
  if [[ -n "${depth_flag}" ]]; then
    cmd+=("${depth_flag}")
  fi
  "${cmd[@]}"
}

# lerobot-train (lr 1e-4 + cosine) 직접 호출.
train_cosine() {
  local repo_id="$1" data_root="$2" job_name="$3"
  local out_dir="${REPO_ROOT}/ai/models/${job_name}"
  echo "=================================================="
  echo "[train] ${job_name}  (lr peak=${PEAK_LR}, cosine warmup=${WARMUP}/decay=${DECAY_STEPS})"
  echo "=================================================="
  lerobot-train \
    --dataset.repo_id "${repo_id}" \
    --dataset.root "${data_root}" \
    --dataset.use_imagenet_stats true \
    --policy.type act \
    --policy.push_to_hub false \
    --policy.device cuda \
    --policy.use_vae false \
    --policy.use_amp true \
    --policy.chunk_size 40 \
    --policy.n_action_steps 40 \
    --use_policy_training_preset false \
    --optimizer.type adamw \
    --optimizer.lr "${PEAK_LR}" \
    --optimizer.weight_decay 1e-4 \
    --optimizer.grad_clip_norm 10 \
    --scheduler.type cosine_decay_with_warmup \
    --scheduler.num_warmup_steps "${WARMUP}" \
    --scheduler.num_decay_steps "${DECAY_STEPS}" \
    --scheduler.peak_lr "${PEAK_LR}" \
    --scheduler.decay_lr "${DECAY_LR}" \
    --batch_size "${BATCH}" \
    --num_workers "${NUM_WORKERS}" \
    --steps "${STEPS}" \
    --eval_freq 0 \
    --save_freq "${SAVE_FREQ}" \
    --log_freq 100 \
    --output_dir "${out_dir}" \
    --job_name "${job_name}" \
    2>&1 | tee "ai/logs/train_${job_name}_$(date +%Y%m%d_%H%M%S).log"
}

run_depth() {
  convert_dataset ai/datasets/with_cover_overhead_depth with_cover_overhead_depth "--include_depth"
  train_cosine with_cover_overhead_depth ai/datasets/with_cover_overhead_depth act_overhead_depth_cosine
}

run_nodepth() {
  convert_dataset ai/datasets/with_cover_overhead_nodepth with_cover_overhead_nodepth ""
  train_cosine with_cover_overhead_nodepth ai/datasets/with_cover_overhead_nodepth act_overhead_nodepth_cosine
}

STAGE="${STAGE:-all}"
case "${STAGE}" in
  depth)   run_depth ;;
  nodepth) run_nodepth ;;
  all)     run_depth; run_nodepth ;;
  *) echo "Unknown STAGE=${STAGE} (depth|nodepth|all)"; exit 1 ;;
esac

echo "완료. 모델: ai/models/act_overhead_depth_cosine, ai/models/act_overhead_nodepth_cosine"
