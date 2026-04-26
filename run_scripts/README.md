# Run Scripts

루트에서 자주 쓰는 실행 명령을 스크립트로 묶어둔 폴더입니다.

## 공통

- 실행 전 기본적으로 레포 루트 기준으로 동작합니다.
- ROS 관련 스크립트는 `run_scripts/00_env_ros.sh`를 내부에서 자동 source 합니다.
- 실행 권한이 이미 설정되어 있습니다.

## 스크립트 목록

### ROS2 환경

- `00_env_ros.sh`
  - ROS2 Humble + `install/setup.bash` + Cyclone DDS를 로드합니다.

### 데이터 수집

- `10_data_collection_backend.sh [indy_ip] [mark7_port]`
  - 기본값: `192.168.1.10`, `/dev/ttyACM0`
  - 예: `./run_scripts/10_data_collection_backend.sh 192.168.1.10 /dev/ttyACM1`

- `11_data_collection_teleop.sh`
  - 통합 텔레옵 노드 실행

### 학습

- `20_train_lerobot.sh <episodes_dir> <dataset_output_dir> <dataset_repo_id> <job_name> [device]`
  - 기본값 사용 시: `./run_scripts/20_train_lerobot.sh`
  - 예: `./run_scripts/20_train_lerobot.sh episodes ai/datasets/pipet_dataset pipet_dataset act_pipet cuda`

- `21_train_26_04_20_half_data.sh`
  - 고정 레시피(`ai/lerobot/train_26_04_20_half_data.sh`) 실행

### MuJoCo

- `30_mujoco_prepare.sh`
  - Indy7+Mark7 결합 URDF 생성 + mesh 복사

- `31_mujoco_teleop.sh [teleop options...]`
  - `keyboard_cartesian_teleop.py`로 옵션 passthrough
  - 예: `./run_scripts/31_mujoco_teleop.sh --qvel-gain 4.0 --max-qvel 3.0`

- `32_mujoco_collect.sh [seconds] [hz] [success|fail]`
  - 기본값: `10`, `20`, `success`
  - 예: `./run_scripts/32_mujoco_collect.sh 15 20 fail`

### 추론/테스트

- `40_inference_ros.sh <model_path> [indy_ip] [mark7_port]`
  - 예: `./run_scripts/40_inference_ros.sh /path/to/model/checkpoints/last 192.168.1.10 /dev/ttyACM1`

- `50_mark7_preset_test.sh open|grasp|press|release`
  - 예: `./run_scripts/50_mark7_preset_test.sh press`

### 진단/개선 (파이펫 오프셋)

- `60_check_preprocess_alignment.sh [train_config] [img_h] [img_w] [action_delta_scale]`
  - 학습/추론 전처리(해상도, repo_id, delta scale) 정합 검사
  - 예: `./run_scripts/60_check_preprocess_alignment.sh ai/models/26.04.20_half_data/checkpoints/last/pretrained_model/train_config.json 360 480 8.0`

- `61_offline_error_split.sh [episodes_dir] [action_delta_scale] [max_delta_rad]`
  - 오프라인으로 제어 스케일 포화율(clipping) 진단
  - 예: `./run_scripts/61_offline_error_split.sh ros2_ws/episodes/success 8.0 0.25`

## 추천 실행 순서 예시

### 실제 데이터 수집

1. 터미널 A: `./run_scripts/10_data_collection_backend.sh`
2. 터미널 B: `./run_scripts/11_data_collection_teleop.sh`

### MuJoCo 테스트

1. `./run_scripts/30_mujoco_prepare.sh`
2. `./run_scripts/31_mujoco_teleop.sh`
3. (선택) `./run_scripts/32_mujoco_collect.sh 10 20 success`
