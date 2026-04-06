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
  3) `lerobot-train` 실행 시 `--dataset.root`에 위 폴더 경로를 넣어 학습한다.

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
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("[cmd]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes_dir", required=True, help="Folder containing episodes/*.npz")
    parser.add_argument("--dataset_output_dir", required=True, help="Output LeRobotDataset root folder")
    parser.add_argument("--dataset_repo_id", default="pipet_dataset")
    parser.add_argument("--fps", type=int, default=0, help="0 => derive from timestamps")
    parser.add_argument("--task", default="Pick up the pipette")
    parser.add_argument("--only_success", action="store_true")

    parser.add_argument("--output_dir", default="outputs/train/act_pipet")
    parser.add_argument("--job_name", default="act_pipet")
    parser.add_argument("--steps", type=int, default=50_000)
    parser.add_argument("--eval_freq", type=int, default=10_000)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--image_resize_to",
        default="360x480",
        help="Optional HxW resize for conversion (default: 360x480).",
    )

    parser.add_argument("--skip_convert", action="store_true", help="Skip NPZ -> LeRobotDataset conversion.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
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
        ]
        if args.only_success:
            cmd_convert.append("--only_success")
        if args.image_resize_to:
            cmd_convert += ["--image_resize_to", args.image_resize_to]
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
        args.output_dir,
        "--job_name",
        args.job_name,
        "--batch_size",
        str(args.batch_size),
        "--steps",
        str(args.steps),
        "--eval_freq",
        str(args.eval_freq),
        "--policy.chunk_size",
        "40",
        "--policy.n_action_steps",
        "40",
        "--policy.use_vae",
        "false",
        "--policy.use_amp",
        "true",
        "--dataset.use_imagenet_stats",
        "true",
    ]

    run(cmd_train)


if __name__ == "__main__":
    main()

