from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

import numpy as np


REQUIRED_KEYS = [
    "timestamps",
    "joint_positions",
    "joint_velocities",
    "joint_efforts",
    "wrist_rgb_images",
    "overhead_rgb_images",
    "gripper_actions",
    "success",
]


def compute_fps(timestamps: np.ndarray) -> float:
    if len(timestamps) < 2:
        return 0.0
    dt = np.diff(timestamps)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.median(dt))


def validate_episode(data: Dict[str, Any], path: Path) -> int:
    for key in REQUIRED_KEYS:
        if key not in data:
            raise KeyError(f"{path.name}: missing key '{key}'")

    n = len(data["timestamps"])

    checks = {
        "joint_positions": (n, 6),
        "joint_velocities": (n, 6),
        "joint_efforts": (n, 6),
        "wrist_rgb_images": (n, 480, 640, 3),
        "overhead_rgb_images": (n, 480, 640, 3),
        "gripper_actions": (n,),
    }

    for key, expected_shape in checks.items():
        actual_shape = data[key].shape
        if actual_shape != expected_shape:
            raise ValueError(
                f"{path.name}: key '{key}' shape mismatch. "
                f"expected={expected_shape}, actual={actual_shape}"
            )

    return n


def build_converted_episode(
    path: Path,
    camera: str = "overhead",
) -> Dict[str, Any]:
    raw = np.load(path, allow_pickle=True)

    n = validate_episode(raw, path)
    if n < 2:
        raise ValueError(f"{path.name}: need at least 2 frames, got {n}")

    timestamps = raw["timestamps"].astype(np.float32)          # (N,)
    q = raw["joint_positions"].astype(np.float32)              # (N, 6)
    dq = raw["joint_velocities"].astype(np.float32)            # (N, 6)
    tau = raw["joint_efforts"].astype(np.float32)              # (N, 6)
    g = raw["gripper_actions"].astype(np.int8)                 # (N,)
    success = bool(raw["success"].item())                      # scalar bool

    if camera == "overhead":
        rgb = raw["overhead_rgb_images"]                       # (N, 480, 640, 3)
    elif camera == "wrist":
        rgb = raw["wrist_rgb_images"]
    else:
        raise ValueError(f"Unsupported camera: {camera}")

    # 마지막 프레임은 t+1이 없으므로 제외
    timestamp_out = timestamps[:-1]                            # (N-1,)
    obs_state = np.concatenate(
        [
            q[:-1],    # 6
            dq[:-1],   # 6
            tau[:-1],  # 6
        ],
        axis=1,
    ).astype(np.float32)                                       # (N-1, 18)

    arm_actions = (q[1:] - q[:-1]).astype(np.float32)          # (N-1, 6)
    gripper_out = g[:-1].reshape(-1, 1).astype(np.float32)     # (N-1, 1)

    action = np.concatenate(
        [arm_actions, gripper_out],
        axis=1,
    ).astype(np.float32)                                       # (N-1, 7)

    converted = {
        "timestamp": timestamp_out,
        "observation.state": obs_state,
        "observation.images.front": rgb[:-1],                  # (N-1, 480, 640, 3), uint8
        "action": action,
        # 아래 둘은 디버깅용으로 같이 저장
        "action.arm_delta": arm_actions,
        "action.gripper_code": g[:-1],
        "episode_success": np.array([success], dtype=np.bool_),
        "episode_id": np.array([path.stem]),
        "source_file": np.array([str(path)]),
        "fps": np.array([compute_fps(timestamps)], dtype=np.float32),
    }
    return converted


def save_npz(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_dir",
        type=str,
        default="ai/indy7_lerobot/raw_data",
        help="원본 npz 폴더",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="ai/indy7_lerobot/datasets/simple_lerobot_v1",
        help="변환 결과 저장 폴더",
    )
    parser.add_argument(
        "--camera",
        type=str,
        choices=["overhead", "wrist"],
        default="overhead",
        help="front 이미지로 쓸 카메라",
    )
    parser.add_argument(
        "--include_fail",
        action="store_true",
        help="실패 episode도 포함",
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)

    if not raw_dir.exists():
        raise FileNotFoundError(f"raw_dir not found: {raw_dir}")

    files = sorted(raw_dir.glob("*.npz"))
    if not files:
        raise FileNotFoundError(f"No npz files found in: {raw_dir}")

    manifest = {
        "camera": args.camera,
        "state_dim": 18,
        "action_dim": 7,
        "episodes": [],
        "total_episodes": 0,
        "total_samples": 0,
    }

    for path in files:
        raw = np.load(path, allow_pickle=True)
        success = bool(raw["success"].item())

        if (not args.include_fail) and (not success):
            print(f"[SKIP] fail episode: {path.name}")
            continue

        try:
            converted = build_converted_episode(path, camera=args.camera)
            out_path = out_dir / f"{path.stem}_lerobot_v1.npz"
            save_npz(out_path, converted)

            n_samples = int(converted["timestamp"].shape[0])
            fps = float(converted["fps"][0])

            manifest["episodes"].append(
                {
                    "source_file": str(path),
                    "out_file": str(out_path),
                    "success": success,
                    "num_samples": n_samples,
                    "fps": fps,
                }
            )
            manifest["total_episodes"] += 1
            manifest["total_samples"] += n_samples

            print(
                f"[OK] {path.name} -> {out_path.name} | "
                f"samples={n_samples}, fps={fps:.2f}, success={success}"
            )

        except Exception as e:
            print(f"[ERROR] {path.name}: {e}")

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\nDone.")
    print(f"Saved manifest: {manifest_path}")
    print(f"Total episodes: {manifest['total_episodes']}")
    print(f"Total samples : {manifest['total_samples']}")


if __name__ == "__main__":
    main()