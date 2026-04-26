#!/usr/bin/env python3
"""
오프라인에서 "시각 인식 오차 vs 제어 스케일 오차"를 분리 진단하는 보조 스크립트.

입력:
- episodes 폴더(episode_*.npz)
- 추론 파라미터(action_delta_scale, max_delta_rad)

출력:
- 데이터셋의 실제 delta_q 분포
- 현재 스케일/클립 가정에서의 축별/샘플별 포화율
- 포화율 기반 제어 스케일 리스크 판정
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np


def _iter_episode_paths(episodes_dir: Path, max_episodes: int) -> list[Path]:
    files = sorted(glob.glob(str(episodes_dir / "**" / "episode_*.npz"), recursive=True))
    ps = [Path(p) for p in files]
    if max_episodes > 0:
        ps = ps[:max_episodes]
    return ps


def _collect_deltas(paths: list[Path]) -> np.ndarray:
    all_dq: list[np.ndarray] = []
    for p in paths:
        with np.load(p) as ep:
            if "joint_positions" not in ep:
                continue
            q = np.asarray(ep["joint_positions"], dtype=np.float32)
            if q.ndim != 2 or q.shape[0] < 2:
                continue
            q = q[:, :6]
            dq = q[1:] - q[:-1]
            all_dq.append(dq)
    if not all_dq:
        return np.zeros((0, 6), dtype=np.float32)
    return np.concatenate(all_dq, axis=0)


def _q(v: np.ndarray, p: float) -> float:
    if v.size == 0:
        return 0.0
    return float(np.quantile(v, p))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes_dir", required=True, help="Folder containing episode_*.npz")
    parser.add_argument("--max_episodes", type=int, default=0, help="0 means all")
    parser.add_argument("--action_delta_scale", type=float, default=8.0)
    parser.add_argument("--max_delta_rad", type=float, default=0.25)
    parser.add_argument(
        "--saturation_warn_ratio",
        type=float,
        default=0.30,
        help="Warn if clipping ratio exceeds this value.",
    )
    args = parser.parse_args()

    ep_dir = Path(args.episodes_dir).expanduser().resolve()
    paths = _iter_episode_paths(ep_dir, args.max_episodes)
    if not paths:
        raise FileNotFoundError(f"No episode_*.npz found under: {ep_dir}")

    dq = _collect_deltas(paths)
    if dq.shape[0] == 0:
        raise RuntimeError("No valid joint_positions sequences found.")

    scaled = dq * float(args.action_delta_scale)
    clipped = np.clip(scaled, -float(args.max_delta_rad), float(args.max_delta_rad))

    saturated_axis = np.isclose(np.abs(clipped), float(args.max_delta_rad), atol=1e-9)
    saturated_step = np.any(saturated_axis, axis=1)

    print("=== Offline Error Split Report ===")
    print(f"episodes_dir: {ep_dir}")
    print(f"episodes_used: {len(paths)}")
    print(f"transitions_used: {dq.shape[0]}")
    print(f"action_delta_scale: {args.action_delta_scale}")
    print(f"max_delta_rad: {args.max_delta_rad}")
    print()

    abs_dq = np.abs(dq)
    print("delta_q abs stats (rad):")
    print(f"  p50={_q(abs_dq, 0.50):.6f} p90={_q(abs_dq, 0.90):.6f} p99={_q(abs_dq, 0.99):.6f}")
    print()

    sat_axis_ratio = float(saturated_axis.mean())
    sat_step_ratio = float(saturated_step.mean())
    print("post-scale clipping stats:")
    print(f"  axis_clip_ratio={sat_axis_ratio:.3f}")
    print(f"  step_clip_ratio={sat_step_ratio:.3f}")

    print()
    if sat_step_ratio >= args.saturation_warn_ratio:
        print(
            "[CONTROL_RISK] clipping ratio is high. "
            "현재 오프셋은 제어 스케일/클립 설정 영향이 클 수 있습니다."
        )
        print("  -> action_delta_scale 하향 또는 max_delta_rad 상향(안전 검증 전제) 실험 권장.")
    else:
        print(
            "[VISION_RISK] clipping ratio is low. "
            "제어 포화보다는 시각 분포 불일치(가림/조명/배경) 가능성이 큽니다."
        )
        print("  -> occlusion 포함 데이터 확장, 카메라 시야 고정, 전처리 정합 점검 권장.")


if __name__ == "__main__":
    main()
