#!/usr/bin/env bash
set -euo pipefail

# Depth 유무 비교 학습 (with_cover + overhead 카메라만).
#
# 동일한 데이터(커버 있는 성공 에피소드)와 동일한 학습 하이퍼파라미터로
# 두 모델을 순차 학습한다. 유일한 차이는 depth 포함 여부다.
#   1) act_overhead_depth   : overhead RGB + overhead depth
#   2) act_overhead_nodepth : overhead RGB only
#
# 사용:
#   ./run_scripts/23_train_overhead_depth_compare.sh
#
# 개별 단계만 돌리고 싶으면 STAGE 환경변수로 제어:
#   STAGE=depth   ./run_scripts/23_train_overhead_depth_compare.sh   # depth 포함만
#   STAGE=nodepth ./run_scripts/23_train_overhead_depth_compare.sh   # depth 제외만
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

# 동일하게 유지하는 학습 하이퍼파라미터 (depth 비교의 공정성)
COMMON_TRAIN_ARGS=(
  cuda
  --only_success
  --image_resize_to 360x480
  --state_profile extended
  --fk_urdf "${FK_URDF}"
  --cameras overhead_only
  --batch_size 64
  --steps 100000
  --save_freq 10000
  --num_workers 8
)

STAGE="${STAGE:-all}"

run_depth() {
  echo "=================================================="
  echo "[STAGE 1/2] DEPTH 포함 학습 시작: act_overhead_depth"
  echo "=================================================="
  ./run_scripts/20_train_lerobot.sh \
    "${EPISODES_DIR}" \
    ai/datasets/with_cover_overhead_depth \
    with_cover_overhead_depth \
    act_overhead_depth \
    "${COMMON_TRAIN_ARGS[@]}" \
    --include_depth \
    2>&1 | tee "ai/logs/train_overhead_depth_$(date +%Y%m%d_%H%M%S).log"
}

run_nodepth() {
  echo "=================================================="
  echo "[STAGE 2/2] DEPTH 제외 학습 시작: act_overhead_nodepth"
  echo "=================================================="
  ./run_scripts/20_train_lerobot.sh \
    "${EPISODES_DIR}" \
    ai/datasets/with_cover_overhead_nodepth \
    with_cover_overhead_nodepth \
    act_overhead_nodepth \
    "${COMMON_TRAIN_ARGS[@]}" \
    2>&1 | tee "ai/logs/train_overhead_nodepth_$(date +%Y%m%d_%H%M%S).log"
}

case "${STAGE}" in
  depth)   run_depth ;;
  nodepth) run_nodepth ;;
  all)     run_depth; run_nodepth ;;
  *) echo "Unknown STAGE=${STAGE} (depth|nodepth|all)"; exit 1 ;;
esac

echo "완료. 모델: ai/models/act_overhead_depth, ai/models/act_overhead_nodepth"
