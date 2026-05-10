#!/usr/bin/env python3
"""Build an NPZ episode folder with extra near-grasp crops.

The output folder contains:
- all original episodes copied unchanged
- one extra cropped episode per source episode, centered around the first grasp

This is intended to oversample final approach / alignment / grasp timing without
discarding the original full trajectories.
"""

from __future__ import annotations

import argparse
import glob
import shutil
from pathlib import Path
from typing import Any

import numpy as np


def _derive_fps(timestamps: np.ndarray, fallback: int) -> int:
    ts = np.asarray(timestamps, dtype=np.float64).reshape(-1)
    if ts.shape[0] < 3:
        return fallback
    dts = ts[1:] - ts[:-1]
    dts = dts[dts > 0]
    if dts.size == 0:
        return fallback
    fps = int(round(1.0 / float(np.median(dts))))
    return max(1, fps)


def _first_grasp_index(gripper_actions: np.ndarray) -> int | None:
    g = np.asarray(gripper_actions).reshape(-1)
    if g.size == 0:
        return None
    rising = np.flatnonzero((g[:-1] != 1) & (g[1:] == 1)) + 1
    if rising.size:
        return int(rising[0])
    any_grasp = np.flatnonzero(g == 1)
    if any_grasp.size:
        return int(any_grasp[0])
    return None


def _slice_value(value: Any, start: int, end: int, n: int) -> Any:
    arr = np.asarray(value)
    if arr.ndim >= 1 and arr.shape[0] == n:
        out = arr[start:end]
        if arr.dtype == object:
            return out.copy()
        return out
    return arr


def _write_crop(src: Path, dst: Path, *, pre_frames: int, post_frames: int, fallback_fps: int) -> tuple[bool, str]:
    with np.load(src, allow_pickle=True) as ep:
        if "gripper_actions" not in ep:
            return False, "missing gripper_actions"
        g = np.asarray(ep["gripper_actions"]).reshape(-1)
        n = int(g.shape[0])
        if n < 2:
            return False, "too few frames"

        grasp_idx = _first_grasp_index(g)
        if grasp_idx is None:
            return False, "no grasp action"

        start = max(0, grasp_idx - pre_frames)
        end = min(n, grasp_idx + post_frames)
        if end - start < 2:
            return False, f"crop too short start={start} end={end}"

        data = {key: _slice_value(ep[key], start, end, n) for key in ep.files}
        if "timestamps" in data:
            ts = np.asarray(data["timestamps"], dtype=np.float64)
            if ts.ndim == 1 and ts.size:
                data["timestamps"] = (ts - ts[0]).astype(ts.dtype, copy=False)
        data["grasp_focus_source"] = np.array(str(src.name))
        data["grasp_focus_source_start"] = np.array(start, dtype=np.int64)
        data["grasp_focus_source_end"] = np.array(end, dtype=np.int64)
        data["grasp_focus_source_grasp_index"] = np.array(grasp_idx, dtype=np.int64)
        data["grasp_focus_fps"] = np.array(
            _derive_fps(np.asarray(ep["timestamps"]) if "timestamps" in ep else np.array([]), fallback_fps),
            dtype=np.int64,
        )

    np.savez_compressed(dst, **data)
    return True, f"frames={end - start} source_grasp={grasp_idx} window=[{start},{end})"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Folder containing source episode_*.npz files.")
    parser.add_argument("--output_dir", required=True, help="New folder to write original + grasp-focus episodes.")
    parser.add_argument("--pre_grasp_sec", type=float, default=4.0, help="Seconds to keep before first grasp.")
    parser.add_argument("--post_grasp_sec", type=float, default=2.0, help="Seconds to keep after first grasp.")
    parser.add_argument("--fps", type=int, default=20, help="FPS used to convert seconds to frame windows.")
    parser.add_argument("--no_copy_originals", action="store_true", help="Only write grasp-focus crops.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"input_dir not found: {input_dir}")
    if output_dir.exists():
        raise FileExistsError(f"output_dir already exists: {output_dir}")

    files = sorted(Path(p) for p in glob.glob(str(input_dir / "episode_*.npz")))
    if not files:
        raise FileNotFoundError(f"No episode_*.npz files found under: {input_dir}")

    output_dir.mkdir(parents=True)
    copied = 0
    crops = 0
    skipped = 0
    if not args.no_copy_originals:
        for i, src in enumerate(files):
            dst = output_dir / f"episode_{i:06d}_orig_{src.name}"
            shutil.copy2(src, dst)
            copied += 1

    pre_frames = max(0, int(round(float(args.pre_grasp_sec) * float(args.fps))))
    post_frames = max(1, int(round(float(args.post_grasp_sec) * float(args.fps))))
    for i, src in enumerate(files):
        dst = output_dir / f"episode_{i:06d}_grasp_focus_{src.stem}.npz"
        ok, msg = _write_crop(
            src,
            dst,
            pre_frames=pre_frames,
            post_frames=post_frames,
            fallback_fps=int(args.fps),
        )
        if ok:
            crops += 1
        else:
            skipped += 1
        print(f"[{i+1:03d}/{len(files):03d}] {'crop' if ok else 'skip'} {src.name}: {msg}")

    print(
        f"Done. originals={copied} grasp_focus_crops={crops} skipped={skipped} "
        f"total_output={copied + crops} -> {output_dir}"
    )


if __name__ == "__main__":
    main()
