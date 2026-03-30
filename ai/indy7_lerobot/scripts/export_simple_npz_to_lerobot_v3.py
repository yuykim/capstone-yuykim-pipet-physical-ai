from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from lerobot.datasets.lerobot_dataset import LeRobotDataset


STATE_NAMES = [
    "joint_pos_1", "joint_pos_2", "joint_pos_3", "joint_pos_4", "joint_pos_5", "joint_pos_6",
    "joint_vel_1", "joint_vel_2", "joint_vel_3", "joint_vel_4", "joint_vel_5", "joint_vel_6",
    "joint_eff_1", "joint_eff_2", "joint_eff_3", "joint_eff_4", "joint_eff_5", "joint_eff_6",
]

ACTION_NAMES = [
    "delta_joint_1", "delta_joint_2", "delta_joint_3",
    "delta_joint_4", "delta_joint_5", "delta_joint_6",
    "gripper_action",
]


def build_features(image_shape: tuple[int, int, int]):
    h, w, c = image_shape
    return {
        "observation.images.front": {
            "dtype": "video",
            "shape": (h, w, c),
            "names": ["height", "width", "channels"],
        },
        "observation.state": {
            "dtype": "float32",
            "shape": (18,),
            "names": STATE_NAMES,
        },
        "action": {
            "dtype": "float32",
            "shape": (7,),
            "names": ACTION_NAMES,
        },
    }


def load_npz(path: Path):
    data = np.load(path, allow_pickle=True)

    required = [
        "timestamp",
        "observation.state",
        "observation.images.front",
        "action",
    ]
    for key in required:
        if key not in data:
            raise KeyError(f"{path.name}: missing key '{key}'")

    ts = data["timestamp"].astype(np.float32)                  # (N,)
    state = data["observation.state"].astype(np.float32)       # (N, 18)
    image = data["observation.images.front"]                   # (N, H, W, 3), uint8
    action = data["action"].astype(np.float32)                 # (N, 7)

    n = len(ts)
    if state.shape != (n, 18):
        raise ValueError(f"{path.name}: invalid state shape {state.shape}")
    if action.shape != (n, 7):
        raise ValueError(f"{path.name}: invalid action shape {action.shape}")
    if image.shape[0] != n:
        raise ValueError(f"{path.name}: image length mismatch {image.shape[0]} vs {n}")
    if image.ndim != 4 or image.shape[-1] != 3:
        raise ValueError(f"{path.name}: invalid image shape {image.shape}")

    return ts, state, image, action


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src_dir",
        type=str,
        default="ai/indy7_lerobot/datasets/simple_lerobot_v1",
        help="simple_lerobot_v1 npz 폴더",
    )
    parser.add_argument(
        "--out_root",
        type=str,
        default="ai/indy7_lerobot/datasets/lerobot_v3_overhead_v1",
        help="LeRobotDataset v3 저장 폴더",
    )
    parser.add_argument(
        "--repo_id",
        type=str,
        default="local/indy7_pipette_overhead_v1",
        help="로컬용 dataset repo id",
    )
    parser.add_argument(
        "--robot_type",
        type=str,
        default="indy7_mark7",
        help="dataset info에 기록할 robot_type",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=20,
        help="dataset fps",
    )
    parser.add_argument(
        "--single_task",
        type=str,
        default="Pick up the pipette",
        help="task description",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="기존 out_root 삭제 후 새로 생성",
    )
    parser.add_argument(
        "--image_writer_threads",
        type=int,
        default=2,
        help="영상 인코딩 thread 수",
    )
    args = parser.parse_args()

    src_dir = Path(args.src_dir)
    out_root = Path(args.out_root)

    if not src_dir.exists():
        raise FileNotFoundError(f"src_dir not found: {src_dir}")

    files = sorted(src_dir.glob("*_lerobot_v1.npz"))
    if not files:
        raise FileNotFoundError(f"No converted npz files found in: {src_dir}")

    if out_root.exists() and args.overwrite:
        shutil.rmtree(out_root)

    # 첫 파일로 feature schema 결정
    first_ts, first_state, first_image, first_action = load_npz(files[0])
    features = build_features(first_image[0].shape)

    dataset = LeRobotDataset.create(
        repo_id=args.repo_id,
        root=out_root,
        fps=args.fps,
        robot_type=args.robot_type,
        features=features,
        use_videos=True,
        image_writer_threads=args.image_writer_threads,
    )

    total_episodes = 0
    total_frames = 0

    for path in files:
        ts, state, image, action = load_npz(path)
        n = len(ts)

        print(f"[EXPORT] {path.name} | frames={n}")

        for i in range(n):
            frame = {
                "observation.images.front": image[i],  # uint8 HWC
                "observation.state": state[i],         # (18,)
                "action": action[i],                   # (7,)
                "task": args.single_task,
            }
            dataset.add_frame(frame)

        dataset.save_episode()
        total_episodes += 1
        total_frames += n

    dataset.finalize()

    print("\nDone.")
    print(f"repo_id      : {args.repo_id}")
    print(f"dataset root : {out_root}")
    print(f"episodes     : {total_episodes}")
    print(f"frames       : {total_frames}")
    print("Expected structure: meta/, data/, videos/")


if __name__ == "__main__":
    main()