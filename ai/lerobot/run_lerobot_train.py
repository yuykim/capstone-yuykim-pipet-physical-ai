#!/usr/bin/env python3
"""
이 프로젝트용 LeRobot 학습 실행 스크립트(ACT baseline).

이 파일은 아래 두 단계를 한 번에(또는 부분적으로) 실행하기 위한 래퍼다.
  - `ai/data_conversion/npz_to_lerobot/convert.py`  (NPZ -> LeRobotDataset v3.0)
  - `lerobot-train`                                (ACT policy 학습)

전제:
  - LeRobot이 설치된 파이썬 환경에서 실행해야 한다.
    (즉, `import lerobot` 및 CLI `lerobot-train`이 가능해야 함)

권장 워크플로우:
  1) ROS2 수집기로 `episodes/*.npz`를 만든다.
  2) NPZ를 LeRobotDataset v3.0 폴더로 변환한다( meta/info.json, meta/stats.json 생성 ).
     출력은 `ai/datasets/<이름>/` 권장.
  3) `lerobot-train` 실행 시 `--dataset.root`에 위 폴더 경로를 넣어 학습한다.
     `--output_dir` 생략 시 체크포인트는 `ai/models/<job_name>/` 에 저장된다.

기본 학습 하이퍼파라미터(ACT):
  - `policy.chunk_size` / `policy.n_action_steps`: 40
  - `policy.use_vae`: false
  - `policy.use_amp`: true
  - `batch_size`: 8
  - `dataset.use_imagenet_stats`: true

이 래퍼를 두는 이유:
  - 팀이 동일한 명령/옵션으로 반복 실행하기 쉽게(재현성)
  - `--dataset.root` 같은 핵심 플래그를 빼먹지 않도록
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(
    cmd: list[str],
    env: dict[str, str] | None = None,
    env_overrides: dict[str, str] | None = None,
) -> None:
    if env_overrides:
        print("[env]", " ".join(f"{key}={value}" for key, value in env_overrides.items()))
    print("[cmd]", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes_dir", required=True, help="Folder containing episodes/*.npz")
    parser.add_argument("--dataset_output_dir", required=True, help="Output LeRobotDataset root folder")
    parser.add_argument("--dataset_repo_id", default="pipet_dataset")
    parser.add_argument("--fps", type=int, default=0, help="0 => derive from timestamps")
    parser.add_argument("--task", default="Pick up the pipette")
    parser.add_argument("--only_success", action="store_true")

    parser.add_argument(
        "--output_dir",
        default="",
        help="비우면 ai/models/<job_name> (절대 경로 권장)",
    )
    parser.add_argument("--job_name", default="act_pipet")
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--eval_freq", type=int, default=10_000)
    parser.add_argument(
        "--log_freq",
        type=int,
        default=50,
        help="N 스텝마다 콘솔에 loss/lr/grad_norm 등 로그(LeRobot train_tracker). 기본 50.",
    )
    parser.add_argument(
        "--save_freq",
        type=int,
        default=None,
        help="체크포인트 저장 주기(미지정 시 lerobot 기본 20000). steps=20000이면 10000으로 두면 10k/20k에 저장.",
    )
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=40,
        help="ACT action chunk horizon. Smaller values reduce GPU memory.",
    )
    parser.add_argument(
        "--n_action_steps",
        type=int,
        default=None,
        help="ACT action steps used at inference. Defaults to --chunk_size.",
    )
    parser.add_argument(
        "--use_amp",
        choices=["true", "false"],
        default="true",
        help="Enable mixed precision for policy training.",
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=None,
        help="DataLoader worker 수. 미지정 시 lerobot 기본(4). 스트리밍+고해상도 이미지는 0이 안전(OOM·worker Killed 방지).",
    )
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--policy_dim_model",
        type=int,
        default=None,
        help="Optional ACT transformer hidden size override, e.g. 256 for lower VRAM.",
    )
    parser.add_argument(
        "--policy_dim_feedforward",
        type=int,
        default=None,
        help="Optional ACT transformer FFN size override, e.g. 1024 for lower VRAM.",
    )
    parser.add_argument(
        "--policy_n_heads",
        type=int,
        default=None,
        help="Optional ACT attention head count override. Must divide dim_model.",
    )
    parser.add_argument(
        "--policy_n_encoder_layers",
        type=int,
        default=None,
        help="Optional ACT encoder layer count override.",
    )
    parser.add_argument(
        "--torch_alloc_conf",
        default="expandable_segments:True",
        help="CUDA allocator config for the lerobot-train subprocess. Empty string disables this wrapper default.",
    )
    parser.add_argument(
        "--image_resize_to",
        default="360x480",
        help="Optional HxW resize for conversion (default: 360x480).",
    )

    parser.add_argument("--skip_convert", action="store_true", help="Skip NPZ -> LeRobotDataset conversion.")
    parser.add_argument(
        "--dataset_streaming",
        action="store_true",
        help="Pass --dataset.streaming true (IterableDataset). 로컬 parquet 재구성 캐시로 ~/.cache 가 가득 찰 때 유리.",
    )
    parser.add_argument(
        "--drop_idle_sec",
        type=float,
        default=0.0,
        help="Drop continuous idle segments longer than this many seconds during conversion (0 disables).",
    )
    parser.add_argument(
        "--idle_joint_delta_thresh",
        type=float,
        default=1e-4,
        help="Per-step joint delta threshold (rad) for idle detection during conversion.",
    )
    parser.add_argument(
        "--state_profile",
        choices=["baseline", "extended"],
        default="baseline",
        help="Dataset state profile for conversion (baseline=18D, extended=+ee_pose+gripper_state).",
    )
    parser.add_argument(
        "--include_depth",
        action="store_true",
        help="Include depth observations during conversion as additional image features.",
    )
    parser.add_argument(
        "--fk_urdf",
        default="",
        help="Indy7 URDF for extended ee_pose FK when NPZ has no ee_pose (same file as inference fk_urdf_path 권장).",
    )
    parser.add_argument("--fk_tcp_frame", default="tcp", help="TCP frame name in URDF.")
    parser.add_argument(
        "--fk_joint_names",
        default="joint0,joint1,joint2,joint3,joint4,joint5",
        help="Comma-separated URDF joint names matching NPZ joint order.",
    )
    parser.add_argument(
        "--convert_log_every_frames",
        type=int,
        default=200,
        help="Conversion progress log interval in frames (0 disables).",
    )
    args = parser.parse_args()
    n_action_steps = args.n_action_steps if args.n_action_steps is not None else args.chunk_size
    if n_action_steps > args.chunk_size:
        parser.error("--n_action_steps must be less than or equal to --chunk_size")
    dim_model = args.policy_dim_model or 512
    n_heads = args.policy_n_heads or 8
    if dim_model % n_heads != 0:
        parser.error("--policy_n_heads must divide policy dim_model")

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.strip()
    if not output_dir:
        output_dir = str((repo_root / "models" / args.job_name).resolve())
    convert_py = repo_root / "data_conversion" / "npz_to_lerobot" / "convert.py"

    if not args.skip_convert:
        # 변환 단계는 "새 데이터셋 폴더"를 생성한다.
        # (LeRobot 메타데이터 writer가 내부적으로 exist_ok=False 성격이라, 기존 폴더가 있으면 실패할 수 있음)
        # 재변환이 필요하면:
        # - 기존 --dataset_output_dir 폴더를 지우거나
        # - --dataset_output_dir를 다른 경로로 바꿔서 실행한다.
        cmd_convert = [
            sys.executable,
            str(convert_py),
            "--episodes_dir",
            args.episodes_dir,
            "--output_dir",
            args.dataset_output_dir,
            "--output_repo_id",
            args.dataset_repo_id,
            "--fps",
            str(args.fps),
            "--task",
            args.task,
            "--log_every_frames",
            str(args.convert_log_every_frames),
        ]
        if args.only_success:
            cmd_convert.append("--only_success")
        if args.image_resize_to:
            cmd_convert += ["--image_resize_to", args.image_resize_to]
        if args.drop_idle_sec and args.drop_idle_sec > 0.0:
            cmd_convert += [
                "--drop_idle_sec",
                str(args.drop_idle_sec),
                "--idle_joint_delta_thresh",
                str(args.idle_joint_delta_thresh),
            ]
        cmd_convert += ["--state_profile", args.state_profile]
        if args.include_depth:
            cmd_convert.append("--include_depth")
        fk_urdf = str(args.fk_urdf).strip()
        if fk_urdf:
            cmd_convert += [
                "--fk_urdf",
                fk_urdf,
                "--fk_tcp_frame",
                str(args.fk_tcp_frame),
                "--fk_joint_names",
                str(args.fk_joint_names),
            ]
        run(cmd_convert)

    # 학습 단계: 로컬 데이터셋은 --dataset.root 로 전달한다.
    # 주의: `dataset_repo_id`는 변환 시 meta/info.json에 기록된 repo_id와 일치해야 한다.
    cmd_train = [
        "lerobot-train",
        "--dataset.repo_id",
        args.dataset_repo_id,
        "--dataset.root",
        str(args.dataset_output_dir),
        "--policy.type",
        "act",
        "--policy.push_to_hub",
        "false",
        "--policy.device",
        args.device,
        "--output_dir",
        output_dir,
        "--job_name",
        args.job_name,
        "--batch_size",
        str(args.batch_size),
        "--steps",
        str(args.steps),
        "--eval_freq",
        str(args.eval_freq),
        "--log_freq",
        str(args.log_freq),
        "--policy.chunk_size",
        str(args.chunk_size),
        "--policy.n_action_steps",
        str(n_action_steps),
        "--policy.use_vae",
        "false",
        "--policy.use_amp",
        args.use_amp,
        "--dataset.use_imagenet_stats",
        "true",
    ]
    if args.save_freq is not None:
        cmd_train += ["--save_freq", str(args.save_freq)]
    if args.dataset_streaming:
        cmd_train += ["--dataset.streaming", "true"]
    if args.num_workers is not None:
        cmd_train += ["--num_workers", str(args.num_workers)]
    if args.policy_dim_model is not None:
        cmd_train += ["--policy.dim_model", str(args.policy_dim_model)]
    if args.policy_dim_feedforward is not None:
        cmd_train += ["--policy.dim_feedforward", str(args.policy_dim_feedforward)]
    if args.policy_n_heads is not None:
        cmd_train += ["--policy.n_heads", str(args.policy_n_heads)]
    if args.policy_n_encoder_layers is not None:
        cmd_train += ["--policy.n_encoder_layers", str(args.policy_n_encoder_layers)]

    train_env = None
    env_overrides: dict[str, str] = {}
    torch_alloc_conf = args.torch_alloc_conf.strip()
    if torch_alloc_conf:
        train_env = os.environ.copy()
        for key in ("PYTORCH_ALLOC_CONF", "PYTORCH_CUDA_ALLOC_CONF"):
            if not train_env.get(key):
                train_env[key] = torch_alloc_conf
                env_overrides[key] = torch_alloc_conf

    run(cmd_train, env=train_env, env_overrides=env_overrides)


if __name__ == "__main__":
    main()
