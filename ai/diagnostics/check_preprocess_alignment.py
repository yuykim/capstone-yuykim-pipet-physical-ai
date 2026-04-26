#!/usr/bin/env python3
"""
학습/추론 전처리 정합성을 점검한다.

점검 항목:
- dataset meta(info.json)의 이미지 해상도
- train_config.json의 dataset root/repo_id
- 추론 런치 인자(image_target_*, action_delta_scale) 권장값
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _resolve_train_config(path: Path) -> Path:
    p = path.expanduser().resolve()
    if p.is_file():
        return p
    cand = p / "train_config.json"
    if cand.is_file():
        return cand
    raise FileNotFoundError(f"train_config.json not found: {p}")


def _get_image_hw(info: dict, key: str) -> tuple[int, int] | None:
    feat = info.get("features", {}).get(key, {})
    shape = feat.get("shape")
    if not isinstance(shape, list) or len(shape) < 2:
        return None
    return int(shape[0]), int(shape[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_config", required=True, help="Path to train_config.json or its parent directory.")
    parser.add_argument(
        "--dataset_root",
        default="",
        help="Override dataset root. If empty, read from train_config.dataset.root",
    )
    parser.add_argument("--dataset_repo_id", default="", help="Override dataset repo_id for consistency check")
    parser.add_argument("--inference_image_height", type=int, default=0)
    parser.add_argument("--inference_image_width", type=int, default=0)
    parser.add_argument("--action_delta_scale", type=float, default=1.0)
    parser.add_argument("--warn_scale_min", type=float, default=2.0)
    parser.add_argument("--warn_scale_max", type=float, default=15.0)
    args = parser.parse_args()

    tc_path = _resolve_train_config(Path(args.train_config))
    tc = _load_json(tc_path)
    ds_cfg = tc.get("dataset", {})
    cfg_root = str(ds_cfg.get("root", "")).strip()
    cfg_repo_id = str(ds_cfg.get("repo_id", "")).strip()

    ds_root = Path(args.dataset_root.strip() or cfg_root).expanduser().resolve()
    if not (ds_root / "meta" / "info.json").is_file():
        raise FileNotFoundError(f"Dataset info.json missing: {ds_root / 'meta' / 'info.json'}")
    info = _load_json(ds_root / "meta" / "info.json")

    run_repo_id = args.dataset_repo_id.strip() or cfg_repo_id
    front_hw = _get_image_hw(info, "observation.images.front")
    overhead_hw = _get_image_hw(info, "observation.images.overhead")

    print("=== Preprocess Alignment Report ===")
    print(f"train_config: {tc_path}")
    print(f"dataset.root: {ds_root}")
    print(f"dataset.repo_id(train): {cfg_repo_id or '(empty)'}")
    print(f"dataset.repo_id(run): {run_repo_id or '(empty)'}")
    print(f"front image shape(meta): {front_hw}")
    print(f"overhead image shape(meta): {overhead_hw}")
    print(
        "inference image target: "
        f"{args.inference_image_height}x{args.inference_image_width} "
        "(0x0 means no resize)"
    )
    print(f"inference action_delta_scale: {args.action_delta_scale:.3f}")
    print()

    ok = True

    if run_repo_id and cfg_repo_id and run_repo_id != cfg_repo_id:
        ok = False
        print("[FAIL] dataset_repo_id mismatch (run != train_config).")
    else:
        print("[PASS] dataset_repo_id consistent (or not explicitly overridden).")

    if front_hw is None or overhead_hw is None:
        ok = False
        print("[FAIL] Could not read image shapes from dataset meta/features.")
    elif front_hw != overhead_hw:
        ok = False
        print("[FAIL] front/overhead image sizes differ in dataset.")
    else:
        print("[PASS] front/overhead image sizes match in dataset.")
        if args.inference_image_height > 0 and args.inference_image_width > 0:
            target_hw = (args.inference_image_height, args.inference_image_width)
            if target_hw != front_hw:
                ok = False
                print(
                    "[FAIL] inference resize != training dataset shape "
                    f"(inference={target_hw}, dataset={front_hw})."
                )
            else:
                print("[PASS] inference resize matches training dataset shape.")
        else:
            print(
                "[WARN] inference resize disabled (0x0). "
                "Ensure camera stream resolution equals dataset shape."
            )

    if not (args.warn_scale_min <= args.action_delta_scale <= args.warn_scale_max):
        print(
            "[WARN] action_delta_scale is outside recommended range "
            f"[{args.warn_scale_min}, {args.warn_scale_max}] for this project."
        )
    else:
        print("[PASS] action_delta_scale in recommended range.")

    print()
    print("RESULT:", "PASS" if ok else "FAIL")
    if not ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
