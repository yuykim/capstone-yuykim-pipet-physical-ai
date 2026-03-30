#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import time
from pathlib import Path

import mujoco
import numpy as np


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect MuJoCo digital twin dataset (Indy7).")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "generated" / "indy7_mujoco.urdf",
        help="Path to MuJoCo-loadable URDF/MJCF model.",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=10.0,
        help="Collection duration in seconds.",
    )
    parser.add_argument(
        "--hz",
        type=float,
        default=20.0,
        help="Sampling rate in Hz.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Output directory for npz episodes.",
    )
    parser.add_argument(
        "--success",
        action="store_true",
        help="Set success label true in saved episode.",
    )
    return parser


def main() -> None:
    args = build_argparser().parse_args()
    if not args.model.exists():
        raise FileNotFoundError(f"Model not found: {args.model}")

    model = mujoco.MjModel.from_xml_path(str(args.model))
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)

    dt_sample = 1.0 / args.hz
    n_steps = int(args.seconds * args.hz)
    if n_steps <= 0:
        raise ValueError("seconds * hz must be > 0")

    # Dataset fields align with your physical collection format for joints.
    timestamps = np.zeros((n_steps,), dtype=np.float64)
    joint_positions = np.zeros((n_steps, model.nq), dtype=np.float32)
    joint_velocities = np.zeros((n_steps, model.nv), dtype=np.float32)
    joint_efforts = np.zeros((n_steps, model.nv), dtype=np.float32)
    gripper_actions = np.zeros((n_steps,), dtype=np.int8)  # 0=hold

    start_wall = time.time()
    for i in range(n_steps):
        t = i * dt_sample

        # Simple scripted motion as a baseline trajectory generator.
        for j in range(model.nq):
            data.qpos[j] = 0.35 * np.sin(0.8 * t + 0.4 * j)

        mujoco.mj_forward(model, data)

        timestamps[i] = time.time() - start_wall
        joint_positions[i] = data.qpos[: model.nq]
        joint_velocities[i] = data.qvel[: model.nv]
        joint_efforts[i] = data.qfrc_constraint[: model.nv]

        sleep_sec = dt_sample - (time.time() - (start_wall + i * dt_sample))
        if sleep_sec > 0:
            time.sleep(sleep_sec)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "success" if args.success else "fail"
    out_path = args.out_dir / f"episode_{stamp}_{suffix}.npz"
    np.savez_compressed(
        out_path,
        timestamps=timestamps,
        joint_positions=joint_positions,
        joint_velocities=joint_velocities,
        joint_efforts=joint_efforts,
        gripper_actions=gripper_actions,
        success=np.array(args.success, dtype=np.bool_),
    )
    print(f"Saved episode: {out_path}")
    print(f"shape: qpos={joint_positions.shape}, qvel={joint_velocities.shape}")


if __name__ == "__main__":
    main()
