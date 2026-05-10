# Run Scripts

레포 루트에서 자주 쓰는 실행 명령을 모아둔 폴더입니다.

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai
```

## 공통 규칙

- 모든 예시는 레포 루트 기준입니다.
- ROS2 관련 스크립트는 내부에서 `run_scripts/00_env_ros.sh`를 source합니다.
- AI/LeRobot 학습은 먼저 conda 환경을 켜야 합니다.

```bash
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

export PYTHONPATH="${PWD}/ai/lerobot_source/lerobot/src:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_HOME="${PWD}/ai/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export PYTORCH_ALLOC_CONF=expandable_segments:True
mkdir -p "${HF_DATASETS_CACHE}" ai/logs
```

## 스크립트 목록

### ROS2 환경

#### `00_env_ros.sh`

ROS2 Humble, `ros2_ws/install/setup.bash`, Cyclone DDS 환경을 로드합니다.

직접 쓸 때:

```bash
source run_scripts/00_env_ros.sh
```

### 데이터 수집

#### `10_data_collection_backend.sh [indy_ip] [mark7_port]`

Indy7, Mark7, RealSense, data collector를 포함한 데이터 수집 backend를 실행합니다.

기본값:

```text
indy_ip=192.168.1.10
mark7_port=/dev/ttyACM0
```

예시:

```bash
./run_scripts/10_data_collection_backend.sh
./run_scripts/10_data_collection_backend.sh 192.168.1.10 /dev/ttyACM0
```

#### `11_data_collection_teleop.sh`

통합 텔레옵 노드를 실행합니다. backend와 별도 터미널에서 실행합니다.

```bash
./run_scripts/11_data_collection_teleop.sh
```

추천 수집 순서:

```text
터미널 A: ./run_scripts/10_data_collection_backend.sh
터미널 B: ./run_scripts/11_data_collection_teleop.sh
```

실패 데이터는 `fail/`에 저장할 수 있지만, 현재 ACT 학습에는 성공 데이터 중심으로 넣는 것을 권장합니다.

### LeRobot 학습

#### `20_train_lerobot.sh <episodes_dir> <dataset_output_dir> <dataset_repo_id> <job_name> [device] [extra args...]`

`ai/lerobot/run_lerobot_train.py`를 호출하는 얇은 wrapper입니다.
6번째 인자부터는 `run_lerobot_train.py`에 그대로 전달됩니다.

형식:

```bash
./run_scripts/20_train_lerobot.sh \
  <episodes_dir> \
  <dataset_output_dir> \
  <dataset_repo_id> \
  <job_name> \
  [device] \
  [extra run_lerobot_train.py args...]
```

extended 26D + depth + FK 변환 예시:

```bash
./run_scripts/20_train_lerobot.sh \
  ros2_ws/episodes/success/26.05.03_half_data_100 \
  ai/datasets/pipet_extended_depth_100 \
  pipet_extended_depth_100 \
  act_pipet_extended_depth_100 \
  cuda \
  --steps 100000 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 4 \
  --state_profile extended \
  --include_depth \
  --fk_urdf "${PWD}/mujoco_env/generated/indy7_mujoco.urdf"
```

이미 변환된 dataset으로 학습만 할 때는 `--skip_convert`를 붙입니다.

#### `21_train_26_04_20_half_data.sh`

이전 고정 레시피(`ai/lerobot/train_26_04_20_half_data.sh`) 실행용입니다.

```bash
./run_scripts/21_train_26_04_20_half_data.sh
```

### MuJoCo

현재 `mujoco_env/`는 실험용 프로토타입입니다. 실기 pipeline의 주 경로는 아닙니다.

#### `30_mujoco_prepare.sh`

Indy7 + Mark7 결합 URDF 생성 및 mesh 복사를 수행합니다.

```bash
./run_scripts/30_mujoco_prepare.sh
```

#### `31_mujoco_teleop.sh [teleop options...]`

`keyboard_cartesian_teleop.py`에 옵션을 그대로 넘깁니다.

```bash
./run_scripts/31_mujoco_teleop.sh --qvel-gain 4.0 --max-qvel 3.0
```

#### `32_mujoco_collect.sh [seconds] [hz] [success|fail]`

기본값:

```text
seconds=10
hz=20
label=success
```

예시:

```bash
./run_scripts/32_mujoco_collect.sh 15 20 fail
```

### 추론/실기 테스트

#### `40_inference_ros.sh <model_path> [indy_ip] [mark7_port] [fk_urdf_path] [state_target_dim] [extra launch args...]`

실제 로봇 추론 launch를 실행합니다.

형식:

```bash
./run_scripts/40_inference_ros.sh \
  <model_path> \
  [indy_ip] \
  [mark7_port] \
  [fk_urdf_path] \
  [state_target_dim] \
  [extra launch args...]
```

extended 26D 모델 기본 예시:

```bash
./run_scripts/40_inference_ros.sh \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last \
  192.168.1.10 \
  /dev/ttyACM0 \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/mujoco_env/generated/indy7_mujoco.urdf \
  26
```

grasp gate 주요 인자:

```text
grasp_delay_steps:=8
pre_grasp_delta_scale:=1.0
grasp_confirm_steps:=3
grasp_max_delta_norm:=0.012
max_joint_speed_rad_s:=0.25
```

튜닝 방향:

- 너무 빨리 잡음: `grasp_delay_steps` 증가, `grasp_confirm_steps` 증가
- 아예 안 잡음: `grasp_confirm_steps` 감소, `grasp_max_delta_norm` 증가
- 마지막에 더 들어가야 함: `pre_grasp_delta_scale` 소폭 증가
- 전체 움직임이 거칠면: `max_joint_speed_rad_s` 감소

### Mark7 손 테스트

#### `50_mark7_preset_test.sh open|grasp|press|release`

Mark7 preset 동작을 단독 테스트합니다.

```bash
./run_scripts/50_mark7_preset_test.sh open
./run_scripts/50_mark7_preset_test.sh grasp
./run_scripts/50_mark7_preset_test.sh press
./run_scripts/50_mark7_preset_test.sh release
```

### 진단/개선

#### `60_check_preprocess_alignment.sh [train_config] [img_h] [img_w] [action_delta_scale]`

학습/추론 전처리 정합을 확인합니다.

```bash
./run_scripts/60_check_preprocess_alignment.sh \
  ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last/pretrained_model/train_config.json \
  360 \
  480 \
  1.0
```

#### `61_offline_error_split.sh [episodes_dir] [action_delta_scale] [max_delta_rad]`

오프라인으로 action scale과 clipping 비율을 점검합니다.

```bash
./run_scripts/61_offline_error_split.sh \
  ros2_ws/episodes/success/26.05.03_half_data_100 \
  1.0 \
  0.25
```

## 최근 사용 예시

### 1) grasp-focus NPZ 추가 데이터 생성

현재 마지막 1~2cm grasp 실패를 줄이기 위해, 원본 성공 100개 episode에 grasp 직전/직후 6초 crop episode 100개를 추가했습니다.

```bash
python ai/data_conversion/make_grasp_focus_episodes.py \
  --input_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100" \
  --output_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --pre_grasp_sec 4.0 \
  --post_grasp_sec 2.0 \
  --fps 20 \
  2>&1 | tee "ai/logs/make_grasp_focus_episodes_$(date +%Y%m%d_%H%M%S).log"
```

결과:

```text
ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus
200 NPZ episodes = 원본 100 + grasp-focus 100
```

### 2) grasp-focus dataset 변환

```bash
python ai/data_conversion/npz_to_lerobot/convert.py \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --output_dir "${PWD}/ai/datasets/pipet_extended_depth_100_grasp_focus" \
  --output_repo_id pipet_extended_depth_100_grasp_focus \
  --fps 20 \
  --task "Pick up the pipette" \
  --image_resize_to 360x480 \
  --state_profile extended \
  --include_depth \
  --fk_urdf "${PWD}/mujoco_env/generated/indy7_mujoco.urdf" \
  --fk_tcp_frame tcp \
  --log_every_frames 1000 \
  2>&1 | tee "ai/logs/convert_pipet_extended_depth_100_grasp_focus_$(date +%Y%m%d_%H%M%S).log"
```

결과:

```text
ai/datasets/pipet_extended_depth_100_grasp_focus
total_episodes=200
total_frames=47222
fps=20
```

### 3) grasp-focus 학습 resume, workers=4

20k checkpoint까지 `num_workers=2`로 진행한 뒤 dataloader 병목이 보여서, `last -> 020000`에서 `num_workers=4`로 resume했습니다.

```bash
python ai/lerobot/run_lerobot_train.py \
  --skip_convert \
  --episodes_dir "${PWD}/ros2_ws/episodes/success/26.05.03_half_data_100_grasp_focus" \
  --dataset_output_dir "${PWD}/ai/datasets/pipet_extended_depth_100_grasp_focus" \
  --dataset_repo_id pipet_extended_depth_100_grasp_focus \
  --output_dir "${PWD}/ai/models/act_pipet_extended_depth_100_grasp_focus" \
  --job_name act_pipet_extended_depth_100_grasp_focus \
  --resume \
  --resume_config_path "${PWD}/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last/pretrained_model/train_config.json" \
  --steps 100000 \
  --eval_freq 10000 \
  --save_freq 10000 \
  --log_freq 100 \
  --batch_size 8 \
  --chunk_size 40 \
  --n_action_steps 40 \
  --num_workers 4 \
  --device cuda \
  2>&1 | tee "ai/logs/train_act_pipet_extended_depth_100_grasp_focus_resume_workers4_$(date +%Y%m%d_%H%M%S).log"
```

확인 포인트:

```text
resume=True
checkpoint_path=.../checkpoints/last
num_workers=4
step이 20K 근처에서 이어짐
```

### 4) ZMQ sidecar 추론 실행

LeRobot은 conda Python, ROS2는 system Python을 쓰므로 ACT 모델 추론은 ZMQ sidecar를 먼저 띄우는 방식이 안정적입니다.

터미널 A: ZMQ ACT server

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ros2_ws

source /opt/ros/humble/setup.bash
source install/setup.bash
source /home/sirlab-pwd-0000/miniconda3/etc/profile.d/conda.sh
conda activate lerobot

export PYTHONPATH="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/lerobot_source/lerobot/src:${PWD}/install/pipet_inference/lib/python3.10/site-packages:${PYTHONPATH:-}"

python -m pipet_inference.zmq_act_server \
  --bind tcp://127.0.0.1:5560 \
  --model-path /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last
```

터미널 B: ROS inference

```bash
cd /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai

./run_scripts/40_inference_ros.sh \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act_pipet_extended_depth_100_grasp_focus/checkpoints/last \
  192.168.1.10 \
  /dev/ttyACM0 \
  /home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/mujoco_env/generated/indy7_mujoco.urdf \
  26 \
  autonomy_enabled:=true \
  use_zmq_sidecar:=true \
  zmq_endpoint:=tcp://127.0.0.1:5560 \
  image_target_height:=360 \
  image_target_width:=480 \
  grasp_delay_steps:=10 \
  pre_grasp_delta_scale:=1.0 \
  grasp_confirm_steps:=3 \
  grasp_max_delta_norm:=0.012 \
  max_joint_speed_rad_s:=0.25 \
  use_gemini_er_verifier:=false
```

Gemini-ER verifier는 quota/rate-limit 429가 자주 발생했으므로, 현재 실기 테스트 기본값은 `use_gemini_er_verifier:=false`를 권장합니다.
