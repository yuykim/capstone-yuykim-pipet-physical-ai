#!/usr/bin/env python3
"""
이 프로젝트의 `episodes/*.npz`(직접교시 수집 결과)를 로컬 `LeRobotDataset v3.0` 폴더 구조로 변환한다.

입력 NPZ 키(현재 `pipet_data_collector/data_collector_node.py`가 저장하는 구조):
  - timestamps: (N,)
  - home_joint_deg: (6,) metadata only; ignored during LeRobot conversion
  - camera_setup: () metadata only; ignored during LeRobot conversion
  - joint_names: (6,)
  - joint_positions: (N, 6)
  - joint_velocities: (N, 6)
  - joint_efforts: (N, 6)
  - ee_poses: (N, 6) Indy native [x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]
  - wrist_rgb_images: (N, H, W, 3) uint8
  - overhead_rgb_images: (N, H, W, 3) uint8
  - gripper_actions: (N,) int8 모드 (0=유지, 1=잡기, 2=펴기, 3=누르기, 4=엄지 펴기)

출력 LeRobotDataset feature 매핑 (--camera, --action_space로 조절):
  - observation.image            : (선택된 카메라) wrist 또는 overhead RGB
  - observation.state            : [q, dq, tau, ee_pose] concat (24차원)
  - action                       : action_space에 따라
      cartesian: [delta_ee_pose(6), gripper_action(1)] = 7차원 (movetelel 학습용)
      joint:     [delta_q(6), gripper_action(1)] = 7차원 (movetelej 학습용)

설계/주의사항:
  - 원본 `timestamps[t]`를 프레임에 **일부러 저장하지 않는다.**
    LeRobotDataset은 `fps`와 timestamp 간격을 엄격하게 검증한다(허용오차가 작음).
    실제 로봇 로그는 jitter가 있기 쉬우므로, timestamp를 생략하고 LeRobot이
    frame_index/fps 기반으로 단조 증가 timestamp를 생성하게 둔다.
  - `delta_q[t] = q[t+1] - q[t]` 이므로 마지막 프레임은 학습 샘플에서 제외한다.
  - Depth는 현재 수집하지 않는다.
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path
from typing import Any

import numpy as np

from lerobot.datasets.lerobot_dataset import LeRobotDataset


def _get_scalar_bool(np_value: Any) -> bool:
    if isinstance(np_value, (np.bool_, bool)):
        return bool(np_value)
    if isinstance(np_value, np.ndarray) and np_value.shape == ():
        return bool(np_value.item())
    if isinstance(np_value, np.ndarray) and np_value.size == 1:
        return bool(np_value.reshape(-1)[0].item())
    return bool(np_value)


def _infer_label_from_path(ep_path: Path) -> str | None:
    if ep_path.parent.name in {"success", "fail", "unlabeled"}:
        return ep_path.parent.name
    stem = ep_path.stem
    for label in ("success", "fail", "unlabeled"):
        if stem.endswith(f"_{label}"):
            return label
    return None


def _is_success_episode(ep_path: Path, ep: np.lib.npyio.NpzFile, success_key: str) -> bool | None:
    label = _infer_label_from_path(ep_path)
    if label is not None:
        return label == "success"

    # Backward compatibility for older NPZ files that stored the label internally.
    if success_key in ep:
        return _get_scalar_bool(ep[success_key])
    if "episode_success" in ep:
        return _get_scalar_bool(ep["episode_success"])
    if "success" in ep:
        return _get_scalar_bool(ep["success"])
    return None


def _derive_fps_from_timestamps(timestamps: np.ndarray) -> int:
    """
    상대 timestamp 배열로부터 정수 fps를 추정한다.

    존재 이유:
      - LeRobotDataset은 `meta/info.json`에 정수 `fps`가 필요하다.
      - 프레임에 raw timestamp를 저장하지 않더라도(위 docstring 참고),
        시각화/리플레이 도구가 대략 맞는 속도로 동작하도록 fps는 기록 레이트에 맞추고 싶다.
    """
    if timestamps.ndim != 1 or len(timestamps) < 3:
        raise ValueError("Need at least 3 timestamps to derive fps.")
    dts = timestamps[1:] - timestamps[:-1]
    dts = dts[dts > 0]
    if len(dts) == 0:
        raise ValueError("Timestamps are not strictly increasing or contain non-positive deltas.")
    dt = float(np.median(dts))
    fps = int(round(1.0 / dt))
    return max(1, fps)


def _build_features(
    h: int, w: int, camera: str, action_space: str
) -> dict[str, dict[str, Any]]:
    """
    camera: 'wrist' | 'overhead' | 'both'
    action_space: 'cartesian' | 'joint'
    """
    image_shape = (h, w, 3)  # HWC
    state_names = (
        [f"joint_positions_{i}" for i in range(6)]
        + [f"joint_velocities_{i}" for i in range(6)]
        + [f"joint_efforts_{i}" for i in range(6)]
        + [f"ee_pose_{label}" for label in ['x', 'y', 'z', 'rx', 'ry', 'rz']]
    )
    if action_space == 'cartesian':
        action_names = [f"delta_ee_{label}" for label in ['x', 'y', 'z', 'rx', 'ry', 'rz']] + ["gripper_action"]
    else:
        action_names = [f"delta_q_{i}" for i in range(6)] + ["gripper_action"]

    features: dict[str, dict[str, Any]] = {
        "observation.state": {
            "dtype": "float32",
            "shape": (len(state_names),),
            "names": state_names,
        },
        "action": {
            "dtype": "float32",
            "shape": (len(action_names),),
            "names": action_names,
        },
    }
    if camera in ('wrist', 'both'):
        features["observation.images.wrist"] = {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        }
    if camera in ('overhead', 'both'):
        features["observation.images.overhead"] = {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        }
    return features


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes_dir", required=True, help="Folder containing episodes/*.npz")
    parser.add_argument("--output_dir", required=True, help="Output LeRobotDataset root folder")
    parser.add_argument("--output_repo_id", default="pipet_dataset", help="repo_id stored in meta/info.json")
    parser.add_argument("--fps", type=int, default=0, help="Dataset fps. If 0, derive from the first episode timestamps.")
    parser.add_argument("--task", default="Pick up the pipette", help="Task string stored per frame.")
    parser.add_argument("--only_success", action="store_true", help="Use only episodes under success/ or named *_success.npz.")
    parser.add_argument(
        "--success_key",
        default="success",
        help="Legacy NPZ key for episode label if no success/fail/unlabeled path label is present.",
    )
    parser.add_argument("--max_episodes", type=int, default=0, help="0 means no limit.")
    parser.add_argument("--image_resize_to", type=str, default="", help="Optional HxW resize, e.g. 480x640.")
    parser.add_argument(
        "--camera",
        choices=["wrist", "overhead", "both"],
        default="wrist",
        help="Which camera(s) to include as observation. Default: wrist.",
    )
    parser.add_argument(
        "--action_space",
        choices=["cartesian", "joint"],
        default="cartesian",
        help="Action space: cartesian=delta_ee_pose (movetelel) | joint=delta_q (movetelej).",
    )
    args = parser.parse_args()

    episodes_dir = Path(args.episodes_dir)
    if not episodes_dir.exists():
        raise FileNotFoundError(f"episodes_dir not found: {episodes_dir}")

    episode_files = sorted(glob.glob(str(episodes_dir / "**" / "episode_*.npz"), recursive=True))
    if len(episode_files) == 0:
        raise FileNotFoundError(f"No episode_*.npz found under: {episodes_dir}")

    if args.max_episodes and args.max_episodes > 0:
        episode_files = episode_files[: args.max_episodes]

    # 첫 번째 에피소드를 읽어서 다음을 확정한다.
    # - 입력 shape 검증
    # - 카메라 해상도 결정
    # - fps가 0이면 timestamps로부터 추정
    with np.load(episode_files[0]) as ep0:
        q0 = ep0["joint_positions"]
        dq0 = ep0["joint_velocities"]
        tau0 = ep0["joint_efforts"]

        if q0.shape[1] != 6 or dq0.shape[1] != 6 or tau0.shape[1] != 6:
            raise ValueError(
                f"Expected joint_* arrays with shape (N, 6), got: "
                f"joint_positions={q0.shape}, joint_velocities={dq0.shape}, joint_efforts={tau0.shape}"
            )

        if "ee_poses" not in ep0.files:
            raise KeyError(
                "First episode missing 'ee_poses' key. "
                "Re-collect data with the updated data_collector."
            )

        # Pick reference camera for image shape
        if args.camera in ('wrist', 'both'):
            ref_rgb = ep0["wrist_rgb_images"]
        else:
            ref_rgb = ep0["overhead_rgb_images"]
        if ref_rgb.ndim != 4 or ref_rgb.shape[-1] != 3:
            raise ValueError(f"Expected RGB shape (N,H,W,3). Got: {ref_rgb.shape}")

        h, w = int(ref_rgb.shape[1]), int(ref_rgb.shape[2])

        # If using both cameras, verify shape match
        if args.camera == 'both':
            other_rgb = ep0["overhead_rgb_images"]
            if (h, w) != (int(other_rgb.shape[1]), int(other_rgb.shape[2])):
                raise ValueError(
                    "wrist and overhead images must share (H,W). "
                    f"Got wrist={(ref_rgb.shape[1], ref_rgb.shape[2])} "
                    f"overhead={(other_rgb.shape[1], other_rgb.shape[2])}"
                )

        # fps를 지정하지 않았으면(0) 첫 에피소드 기반으로 추정한다.
        # 한 번 정한 fps는 동일 데이터셋 내에서 고정한다.
        if args.fps == 0:
            timestamps0 = ep0["timestamps"]
            args.fps = _derive_fps_from_timestamps(timestamps0)

    if args.image_resize_to:
        # 리사이즈는 선택 옵션이다.
        # (예: 여러 번 수집해서 해상도가 섞였을 때, 학습 입력 크기를 통일하고 싶을 때 사용)
        # 실행 시 OpenCV(cv2)가 필요하다.
        try:
            import cv2  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("OpenCV(cv2) is required for --image_resize_to.") from e
        size_str = args.image_resize_to.lower().replace(" ", "")
        if "x" not in size_str:
            raise ValueError("--image_resize_to must look like HxW, e.g. 480x640")
        rh, rw = [int(x) for x in size_str.split("x", 1)]
        h, w = rh, rw
    else:
        rh, rw = h, w
        cv2 = None  # type: ignore

    features = _build_features(h=h, w=w, camera=args.camera, action_space=args.action_space)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 로컬 파일시스템에 새 LeRobotDataset을 생성한다.
    # 여기서 `repo_id`는 meta/info.json에 저장되는 식별자일 뿐이며, HF Hub로 push하지 않는다.
    dataset = LeRobotDataset.create(
        repo_id=args.output_repo_id,
        fps=int(args.fps),
        features=features,
        root=output_dir,
        robot_type="pipet",
        use_videos=False,
    )

    def maybe_resize_rgb(img_hwc_u8: np.ndarray) -> np.ndarray:
        if (img_hwc_u8.shape[0], img_hwc_u8.shape[1]) == (rh, rw):
            return img_hwc_u8
        if cv2 is None:
            raise RuntimeError(
                "Image resize requested but OpenCV isn't available (missing --image_resize_to cv2 dependency)."
            )
        return cv2.resize(img_hwc_u8, (rw, rh), interpolation=cv2.INTER_LINEAR)

    kept_episodes = 0
    for i, ep_path in enumerate(episode_files):
        with np.load(ep_path) as ep:
            success_val = _is_success_episode(Path(ep_path), ep, args.success_key)

            if args.only_success and success_val is not None and not success_val:
                continue

            joint_positions = ep["joint_positions"].astype(np.float32)
            joint_velocities = ep["joint_velocities"].astype(np.float32)
            joint_efforts = ep["joint_efforts"].astype(np.float32)
            if "ee_poses" not in ep.files:
                raise KeyError(
                    f"{ep_path}: missing 'ee_poses' key. "
                    "Re-collect data with the updated data_collector."
                )
            ee_poses = ep["ee_poses"].astype(np.float32)
            wrist_rgb_images = ep["wrist_rgb_images"].astype(np.uint8) if args.camera in ('wrist', 'both') else None
            overhead_rgb_images = ep["overhead_rgb_images"].astype(np.uint8) if args.camera in ('overhead', 'both') else None
            gripper_actions = ep["gripper_actions"]

        n = joint_positions.shape[0]
        if n < 2:
            continue

        # action은 (t -> t+1) 전이 기반이므로 마지막 timestep은 드랍한다.
        # 모방학습 데이터셋에서도 흔한 처리(마지막에 action이 없는 observation을 남기지 않음).
        for t in range(n - 1):
            q_t = joint_positions[t]  # (6,)
            dq_t = joint_velocities[t]
            tau_t = joint_efforts[t]
            ee_t = ee_poses[t]  # (6,)

            if args.action_space == 'cartesian':
                delta_action = ee_poses[t + 1] - ee_poses[t]  # (6,) Cartesian delta
            else:
                delta_action = joint_positions[t + 1] - joint_positions[t]  # (6,) joint delta
            gripper_cmd = float(gripper_actions[t])

            state_vec = np.concatenate([q_t, dq_t, tau_t, ee_t], axis=0).astype(np.float32)
            action_vec = np.concatenate(
                [delta_action, np.array([gripper_cmd], dtype=np.float32)], axis=0
            ).astype(np.float32)

            frame: dict[str, Any] = {
                "task": args.task,
                "observation.state": state_vec,
                "action": action_vec,
            }
            if wrist_rgb_images is not None:
                frame["observation.images.wrist"] = maybe_resize_rgb(wrist_rgb_images[t])
            if overhead_rgb_images is not None:
                frame["observation.images.overhead"] = maybe_resize_rgb(overhead_rgb_images[t])

            dataset.add_frame(frame)

        # episode 1개 = demonstration trajectory 1개로 저장한다.
        dataset.save_episode()
        kept_episodes += 1
        print(f"[{kept_episodes}] Converted: {ep_path}")

    # 중요: finalize()가 parquet writer를 닫아 footer 메타데이터를 기록한다.
    # 이 호출이 없으면 데이터셋이 정상 로드되지 않는다.
    dataset.finalize()
    print(f"Done. Kept {kept_episodes} episodes -> {output_dir}")


if __name__ == "__main__":
    main()
