#!/usr/bin/env bash
set -euo pipefail

# Depth 유무 비교 학습 v3 (lr 1e-4 + cosine + 데이터로더 최적화).
#
# 24번 대비 변경점:
#   - lerobot_train.py 패치 적용: persistent_workers=True + prefetch_factor 환경변수
#   - LEROBOT_PREFETCH_FACTOR=8 (워커당 미리 쌓는 배치 수, 기본 2 -> 8)
#   - num_workers 12 -> 14 (CPU 8C/16T 에서 여유분 활용)
#   => CPU 디코딩 병목으로 GPU 가 굶던 문제 완화 (18초 정지 감소 기대).
#
# 학습 HP(lr/cosine/steps/batch)는 24번과 동일하게 유지해 depth 비교 공정성 보존.
#
# 사용:
#   STAGE=depth   ./run_scripts/25_train_overhead_fast.sh
#   STAGE=nodepth ./run_scripts/25_train_overhead_fast.sh
#   ./run_scripts/25_train_overhead_fast.sh            # depth -> nodepth 순차
#
# 기존 모델 폴더가 있으면 묻고 지운다(덮어쓰기 충돌 방지).
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

# === 데이터로더 최적화 (lerobot_train.py 패치가 읽는 환경변수) ===
export LEROBOT_PREFETCH_FACTOR=8
# 전체 이미지를 학습 전 1회 디코딩해 RAM(약 26GB)에 적재 → 매 step PNG 디코딩 병목 제거.
export LEROBOT_RAM_CACHE=1

mkdir -p "${HF_DATASETS_CACHE}" ai/logs

# --- 공통 설정 ---
EPISODES_DIR="pipet_data/260510_pipet_up_data_with_cover/SUCCESS"
FK_URDF="${REPO_ROOT}/mujoco_env/generated/indy7_mujoco.urdf"
CONVERT_PY="ai/data_conversion/npz_to_lerobot/convert.py"

# 학습 스텝/스케줄러
STEPS=60000
WARMUP=2000
DECAY_STEPS=60000
PEAK_LR=1e-4
DECAY_LR=1e-6
BATCH=64
NUM_WORKERS=14
SAVE_FREQ=10000

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
  [[ -n "${depth_flag}" ]] && cmd+=("${depth_flag}")
  "${cmd[@]}"
}

# 기존 모델 폴더가 있으면 정리(새 학습은 처음부터 시작).
clean_output() {
  local out_dir="$1"
  if [[ -d "${out_dir}" ]]; then
    echo "[clean] 기존 폴더 삭제: ${out_dir}"
    rm -rf "${out_dir}"
  fi
}

train_cosine() {
  local repo_id="$1" data_root="$2" job_name="$3"
  local out_dir="${REPO_ROOT}/ai/models/${job_name}"
  clean_output "${out_dir}"
  echo "=================================================="
  echo "[train] ${job_name}  (prefetch=${LEROBOT_PREFETCH_FACTOR}, workers=${NUM_WORKERS})"
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
