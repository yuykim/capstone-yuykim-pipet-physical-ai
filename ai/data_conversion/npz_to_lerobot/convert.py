#!/usr/bin/env python3
"""
이 프로젝트의 `episodes/*.npz`(직접교시 수집 결과)를 로컬 `LeRobotDataset v3.0` 폴더 구조로 변환한다.

입력 NPZ 키(현재 `pipet_data_collector/data_collector_node.py`가 저장하는 구조):
  - timestamps: (N,)
  - home_joint_deg: (6,) metadata only; ignored during LeRobot conversion
  - camera_setup: () metadata only; ignored during LeRobot conversion
  - task_name: () metadata only; optional remove/insert task marker
  - joint_names: (6,)
  - joint_positions: (N, 6)
  - joint_velocities: (N, 6)
  - ee_poses: (N, 6) Indy native [x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg]
  - wrist_rgb_images: (N, H, W, 3) uint8
  - wrist_depth_images: (N, H, W) uint16  (optional legacy/depth profile)
  - overhead_rgb_images: (N, H, W, 3) uint8
  - overhead_depth_images: (N, H, W) uint16 (optional legacy/depth profile)
  - gripper_actions: (N,) int8 모드 (0=유지, 1=잡기, 2=펴기, 3=누르기, 4=엄지 펴기)
  - final_gripper_action: () int8 metadata only; ignored during LeRobot conversion
  - quality_warnings: (M,) str metadata only; ignored during LeRobot conversion

출력 LeRobotDataset( ACT baseline 기준 ) feature 매핑:
  - observation.images.front     : wrist_rgb_images[t]
  - observation.images.overhead  : overhead_rgb_images[t]
  - observation.state            : [q, dq] concat (12차원)
  - action                       : action_space에 따라 [delta_q 또는 delta_ee_pose, gripper_action] concat (7차원)

설계/주의사항:
  - 원본 `timestamps[t]`를 프레임에 **일부러 저장하지 않는다.**
    LeRobotDataset은 `fps`와 timestamp 간격을 엄격하게 검증한다(허용오차가 작음).
    실제 로봇 로그는 jitter가 있기 쉬우므로, timestamp를 생략하고 LeRobot이
    frame_index/fps 기반으로 단조 증가 timestamp를 생성하게 둔다.
  - `delta_q[t] = q[t+1] - q[t]` 이므로 마지막 프레임은 학습 샘플에서 제외한다.
  - Depth는 현재 수집하지 않는다. 예전 NPZ/depth 실험은 --include_depth로만 사용한다.

extended 프로파일:
  - NPZ에 ``ee_pose``가 없으면 ``--fk_urdf`` + Pinocchio로 TCP FK를 계산해 7D를 채운다.
  - NPZ에 ``gripper_state``가 없으면 이산 ``gripper_actions[t]``를 gripper_state 슬롯에 넣는다.
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path
from typing import Any, Optional

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


def _ensure_joint_matrix_n6(arr: np.ndarray, name: str) -> np.ndarray:
    """Indy7 6축 기준으로 joint 행렬을 보정한다."""
    a = np.asarray(arr, dtype=np.float32)
    if a.ndim != 2:
        raise ValueError(f"{name} expected 2D array, got shape {a.shape}")
    n = a.shape[0]
    c = a.shape[1]
    if c == 6:
        return a
    if c == 0:
        return np.zeros((n, 6), dtype=np.float32)
    if c > 6:
        return a[:, :6].astype(np.float32)
    out = np.zeros((n, 6), dtype=np.float32)
    out[:, :c] = a
    return out


def _ensure_matrix(arr: np.ndarray, cols: int, name: str) -> np.ndarray:
    """주어진 열 수(cols)에 맞춰 2D 행렬을 보정한다."""
    a = np.asarray(arr, dtype=np.float32)
    if a.ndim != 2:
        raise ValueError(f"{name} expected 2D array, got shape {a.shape}")
    n = a.shape[0]
    c = a.shape[1]
    if c == cols:
        return a
    if c == 0:
        return np.zeros((n, cols), dtype=np.float32)
    if c > cols:
        return a[:, :cols].astype(np.float32)
    out = np.zeros((n, cols), dtype=np.float32)
    out[:, :c] = a
    return out


def _build_features(h: int, w: int) -> dict[str, dict[str, Any]]:
    # LeRobot의 dataset feature spec에서 이미지 shape는 (H, W, C)로 정의한다.
    # 실제 프레임 값은 HWC/CHW 모두 받아들이지만, 우리는 NPZ가 HWC이므로 그대로 사용한다.
    image_shape = (h, w, 3)  # HWC
    state_names = (
        [f"joint_positions_{i}" for i in range(6)]
        + [f"joint_velocities_{i}" for i in range(6)]
    )
    action_names = [f"delta_q_{i}" for i in range(6)] + ["gripper_action"]

    return {
        "observation.images.front": {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        },
        "observation.images.overhead": {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        },
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


def _build_features_ext(
    h: int,
    w: int,
    *,
    ee_pose_cols: int,
    include_gripper_state: bool,
    include_depth: bool,
    action_space: str,
) -> dict[str, dict[str, Any]]:
    image_shape = (h, w, 3)  # HWC
    state_names = (
        [f"joint_positions_{i}" for i in range(6)]
        + [f"joint_velocities_{i}" for i in range(6)]
    )
    if ee_pose_cols == 6:
        state_names += [f"ee_pose_{label}" for label in ["x", "y", "z", "rx", "ry", "rz"]]
    elif ee_pose_cols > 0:
        state_names += [f"ee_pose_{i}" for i in range(ee_pose_cols)]
    if include_gripper_state:
        state_names += ["gripper_state"]
    if action_space == "cartesian":
        action_names = [f"delta_ee_{label}" for label in ["x", "y", "z", "rx", "ry", "rz"]] + [
            "gripper_action"
        ]
    else:
        action_names = [f"delta_q_{i}" for i in range(6)] + ["gripper_action"]

    out: dict[str, dict[str, Any]] = {
        "observation.images.front": {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        },
        "observation.images.overhead": {
            "dtype": "image",
            "shape": image_shape,
            "names": ["height", "width", "channels"],
        },
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
    if include_depth:
        # LeRobot image writer currently expects 3-channel images.
        # Keep depth as pseudo-RGB (same value repeated across channels).
        depth_shape = (h, w, 3)
        out["observation.images.front_depth"] = {
            "dtype": "image",
            "shape": depth_shape,
            "names": ["height", "width", "channels"],
        }
        out["observation.images.overhead_depth"] = {
            "dtype": "image",
            "shape": depth_shape,
            "names": ["height", "width", "channels"],
        }
    return out


def _compute_idle_keep_mask(
    joint_positions: np.ndarray,
    gripper_actions: np.ndarray,
    *,
    min_idle_steps: int,
    joint_delta_thresh: float,
    protect_action_steps: int = 0,
) -> np.ndarray:
    """
    transition 인덱스 t(0..N-2) 기준 keep mask를 만든다.

    idle transition 정의:
      - 팔: |q[t+1] - q[t]|의 모든 축이 joint_delta_thresh 미만
      - 그리퍼: gripper_actions[t+1] == gripper_actions[t] (상태 변화 없음)

    위 idle이 min_idle_steps 이상 연속된 구간은 drop한다.
    단, non-hold gripper action 또는 gripper action transition 주변
    protect_action_steps 구간은 grasp 타이밍 학습을 위해 보존한다.
    """
    n = int(joint_positions.shape[0])
    m = max(0, n - 1)  # number of transitions / trainable steps
    keep = np.ones((m,), dtype=bool)
    if m == 0:
        return keep

    delta_q = joint_positions[1:] - joint_positions[:-1]  # (m,6)
    arm_idle = np.max(np.abs(delta_q), axis=1) < float(joint_delta_thresh)
    grip_idle = gripper_actions[1:m + 1] == gripper_actions[:m]
    idle = arm_idle & grip_idle
    protect = _compute_action_protect_mask(gripper_actions, m=m, window_steps=protect_action_steps)

    if min_idle_steps <= 1:
        keep[idle] = False
        keep[protect] = True
        return keep

    # 연속 idle run 중 길이가 min_idle_steps 이상인 구간만 drop
    run_start = 0
    while run_start < m:
        if not idle[run_start]:
            run_start += 1
            continue
        run_end = run_start
        while run_end < m and idle[run_end]:
            run_end += 1
        run_len = run_end - run_start
        if run_len >= min_idle_steps:
            keep[run_start:run_end] = False
        run_start = run_end
    keep[protect] = True
    return keep


def _compute_action_protect_mask(
    gripper_actions: np.ndarray,
    *,
    m: int,
    window_steps: int,
) -> np.ndarray:
    """Protect transitions around gripper events from idle-frame dropping."""
    protect = np.zeros((m,), dtype=bool)
    if m <= 0 or window_steps <= 0:
        return protect

    actions = np.asarray(gripper_actions).reshape(-1)
    if actions.shape[0] < 2:
        return protect

    t_actions = actions[:m]
    t_next_actions = actions[1 : m + 1]
    event = (t_actions != 0) | (t_next_actions != 0) | (t_next_actions != t_actions)
    event_indices = np.flatnonzero(event)
    for idx in event_indices:
        start = max(0, int(idx) - int(window_steps))
        end = min(m, int(idx) + int(window_steps) + 1)
        protect[start:end] = True
    return protect


def _depth_u16_to_u8_rgb(depth_hw: np.ndarray) -> np.ndarray:
    """
    uint16 depth(mm) -> uint8 pseudo-RGB.
    - invalid(0) stays 0
    - robust min/max scaling using valid pixels only
    """
    d = np.asarray(depth_hw)
    if d.ndim != 2:
        raise ValueError(f"depth image must be 2D, got shape {d.shape}")
    d = d.astype(np.float32, copy=False)
    valid = d > 0
    out_u8 = np.zeros_like(d, dtype=np.uint8)
    if np.any(valid):
        v = d[valid]
        lo = float(np.percentile(v, 1.0))
        hi = float(np.percentile(v, 99.0))
        if hi <= lo:
            hi = lo + 1.0
        scaled = (d - lo) / (hi - lo)
        scaled = np.clip(scaled, 0.0, 1.0)
        out_u8 = (scaled * 255.0).astype(np.uint8)
        out_u8[~valid] = 0
    return np.repeat(out_u8[..., None], 3, axis=2)


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
        "--drop_idle_sec",
        type=float,
        default=0.0,
        help="Drop continuous idle segments longer than this many seconds. 0 disables.",
    )
    parser.add_argument(
        "--idle_joint_delta_thresh",
        type=float,
        default=1e-4,
        help="Per-step joint delta threshold (rad) for idle detection.",
    )
    parser.add_argument(
        "--idle_keep_action_window_sec",
        type=float,
        default=2.0,
        help=(
            "When --drop_idle_sec is enabled, keep idle transitions within this many seconds around "
            "non-hold gripper actions or gripper action changes. This preserves grasp/open timing."
        ),
    )
    parser.add_argument(
        "--state_profile",
        choices=["baseline", "extended"],
        default="baseline",
        help="baseline: q/dq(12D). extended: +ee_pose(7)+gripper_state(1)=20D; "
        "ee_pose는 NPZ 키 또는 --fk_urdf FK; gripper_state 없으면 gripper_actions[t].",
    )
    parser.add_argument(
        "--action_space",
        choices=["joint", "cartesian"],
        default="joint",
        help="joint=delta_q action | cartesian=delta_ee_pose action from ee_poses.",
    )
    parser.add_argument(
        "--include_depth",
        action="store_true",
        help="Include wrist/overhead depth as additional 1-channel image features.",
    )
    parser.add_argument(
        "--log_every_frames",
        type=int,
        default=200,
        help="Print conversion progress every N kept frames (0 disables).",
    )
    parser.add_argument(
        "--fk_urdf",
        default="",
        help="Indy7 URDF path: when extended and NPZ has no ee_pose, fill ee via Pinocchio TCP FK.",
    )
    parser.add_argument(
        "--fk_tcp_frame",
        default="tcp",
        help="End-effector frame name in URDF (Neuromeka single-arm default: tcp).",
    )
    parser.add_argument(
        "--fk_joint_names",
        default="joint0,joint1,joint2,joint3,joint4,joint5",
        help="Comma-separated URDF joint names matching NPZ joint column order.",
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
        wrist_rgb0 = ep0["wrist_rgb_images"]
        overhead_rgb0 = ep0["overhead_rgb_images"]
        q0 = _ensure_joint_matrix_n6(ep0["joint_positions"], "joint_positions")
        dq0 = _ensure_joint_matrix_n6(ep0["joint_velocities"], "joint_velocities")

        # wrist_rgb_images: (N, H, W, 3)
        if wrist_rgb0.ndim != 4 or wrist_rgb0.shape[-1] != 3:
            raise ValueError(f"Expected wrist_rgb_images shape (N,H,W,3). Got: {wrist_rgb0.shape}")
        if overhead_rgb0.ndim != 4 or overhead_rgb0.shape[-1] != 3:
            raise ValueError(f"Expected overhead_rgb_images shape (N,H,W,3). Got: {overhead_rgb0.shape}")

        h, w = int(wrist_rgb0.shape[1]), int(wrist_rgb0.shape[2])
        if (h, w) != (int(overhead_rgb0.shape[1]), int(overhead_rgb0.shape[2])):
            raise ValueError(
                "wrist_rgb_images and overhead_rgb_images must share (H,W). "
                f"Got wrist={(wrist_rgb0.shape[1], wrist_rgb0.shape[2])} overhead={(overhead_rgb0.shape[1], overhead_rgb0.shape[2])}"
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

    include_ee_pose = args.state_profile == "extended" or args.action_space == "cartesian"
    ee_pose_cols = 6 if args.action_space == "cartesian" else (7 if include_ee_pose else 0)
    include_gripper_state = args.state_profile == "extended"

    fk_solver: Optional[Any] = None
    if include_ee_pose and args.fk_urdf.strip():
        from indy7_tcp_fk import Indy7TcpFk

        jnames = [x.strip() for x in str(args.fk_joint_names).split(",") if x.strip()]
        fk_solver = Indy7TcpFk(
            args.fk_urdf.strip(),
            tcp_frame=str(args.fk_tcp_frame).strip() or "tcp",
            joint_names=jnames,
        )

    features = _build_features_ext(
        h=h,
        w=w,
        ee_pose_cols=ee_pose_cols,
        include_gripper_state=include_gripper_state,
        include_depth=bool(args.include_depth),
        action_space=args.action_space,
    )

    output_dir = Path(args.output_dir)

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
    dropped_idle_frames_total = 0
    total_kept_frames = 0
    for i, ep_path in enumerate(episode_files):
        with np.load(ep_path) as ep:
            success_val = _is_success_episode(Path(ep_path), ep, args.success_key)

            if args.only_success and success_val is not None and not success_val:
                continue

            joint_positions = _ensure_joint_matrix_n6(ep["joint_positions"], "joint_positions")
            joint_velocities = _ensure_joint_matrix_n6(ep["joint_velocities"], "joint_velocities")
            wrist_rgb_images = ep["wrist_rgb_images"].astype(np.uint8)
            overhead_rgb_images = ep["overhead_rgb_images"].astype(np.uint8)
            wrist_depth_images = ep["wrist_depth_images"] if "wrist_depth_images" in ep else None
            overhead_depth_images = ep["overhead_depth_images"] if "overhead_depth_images" in ep else None
            gripper_state = (
                np.asarray(ep["gripper_state"], dtype=np.float32).reshape(-1) if "gripper_state" in ep else None
            )
            gripper_actions = ep["gripper_actions"]

            n = joint_positions.shape[0]
            if n < 2:
                continue

            if include_ee_pose:
                if "ee_poses" in ep:
                    ee_pose_mat = _ensure_matrix(ep["ee_poses"], ee_pose_cols, "ee_poses")
                elif "ee_pose" in ep:
                    ee_pose_mat = _ensure_matrix(ep["ee_pose"], ee_pose_cols, "ee_pose")
                else:
                    if fk_solver is None:
                        raise ValueError(
                            "state_profile=extended or action_space=cartesian but NPZ has no 'ee_poses'/'ee_pose'. "
                            "Either record ee_poses in NPZ or pass "
                            "--fk_urdf PATH_TO_INDY7.urdf (Pinocchio required) to compute TCP pose from joint_positions."
                        )
                    if ee_pose_cols != 7:
                        raise ValueError("FK fallback provides 7D ee_pose and cannot fill 6D Indy-native ee_poses.")
                    ee_pose_mat = np.zeros((n, ee_pose_cols), dtype=np.float32)
                    for ti in range(n):
                        ee_pose_mat[ti] = fk_solver.compute(joint_positions[ti])
            else:
                ee_pose_mat = None

        # 기본은 전체 transition 유지
        keep_mask = np.ones((n - 1,), dtype=bool)
        if args.drop_idle_sec and args.drop_idle_sec > 0.0:
            min_idle_steps = max(1, int(round(float(args.drop_idle_sec) * float(args.fps))))
            protect_action_steps = max(
                0,
                int(round(float(args.idle_keep_action_window_sec) * float(args.fps))),
            )
            keep_mask = _compute_idle_keep_mask(
                joint_positions,
                np.asarray(gripper_actions),
                min_idle_steps=min_idle_steps,
                joint_delta_thresh=float(args.idle_joint_delta_thresh),
                protect_action_steps=protect_action_steps,
            )
            dropped_idle_frames_total += int((~keep_mask).sum())

        # action은 (t -> t+1) 전이 기반이므로 마지막 timestep은 드랍한다.
        # 모방학습 데이터셋에서도 흔한 처리(마지막에 action이 없는 observation을 남기지 않음).
        kept_in_episode = 0
        for t in range(n - 1):
            if not keep_mask[t]:
                continue
            q_t = joint_positions[t]  # (6,)
            dq_t = joint_velocities[t]

            if args.action_space == "cartesian":
                assert ee_pose_mat is not None
                delta_action = ee_pose_mat[t + 1, :6] - ee_pose_mat[t, :6]
            else:
                delta_action = joint_positions[t + 1] - joint_positions[t]  # (6,)
            gripper_cmd = float(gripper_actions[t])

            state_vec = np.concatenate([q_t, dq_t], axis=0).astype(np.float32)
            if include_ee_pose:
                assert ee_pose_mat is not None
                ee_vec = ee_pose_mat[t]
                state_vec = np.concatenate([state_vec, ee_vec.astype(np.float32)], axis=0).astype(np.float32)
            if include_gripper_state:
                # Mark7 등: 연속 피드백이 없어도 NPZ의 이산 명령(gripper_actions)을 상태로 쓰면
                # 학습·추론에서 "현재 그리퍼 모드" 슬롯이 0 패딩이 되지 않는다.
                gs = (
                    float(gripper_state[t])
                    if gripper_state is not None and len(gripper_state) > t
                    else float(gripper_actions[t])
                )
                state_vec = np.concatenate([state_vec, np.array([gs], dtype=np.float32)], axis=0).astype(np.float32)
            action_vec = np.concatenate([delta_action, np.array([gripper_cmd], dtype=np.float32)], axis=0).astype(
                np.float32
            )

            wrist_rgb_t = maybe_resize_rgb(wrist_rgb_images[t])
            overhead_rgb_t = maybe_resize_rgb(overhead_rgb_images[t])

            # LeRobotDataset은 프레임마다 `task` 문자열을 요구한다.
            # 추후 task-conditioned 학습(다중 task) 확장 시 그대로 활용 가능.
            frame = {
                "task": args.task,
                "observation.state": state_vec,
                "observation.images.front": wrist_rgb_t,
                "observation.images.overhead": overhead_rgb_t,
                "action": action_vec,
            }
            if args.include_depth:
                if wrist_depth_images is None or overhead_depth_images is None:
                    raise ValueError(
                        "--include_depth enabled but depth keys are missing in "
                        f"{ep_path}. Required: wrist_depth_images, overhead_depth_images."
                    )
                wrist_depth_t = maybe_resize_rgb(_depth_u16_to_u8_rgb(wrist_depth_images[t]))
                overhead_depth_t = maybe_resize_rgb(_depth_u16_to_u8_rgb(overhead_depth_images[t]))
                frame["observation.images.front_depth"] = wrist_depth_t
                frame["observation.images.overhead_depth"] = overhead_depth_t
            dataset.add_frame(frame)
            kept_in_episode += 1
            total_kept_frames += 1
            if args.log_every_frames and args.log_every_frames > 0:
                if kept_in_episode % args.log_every_frames == 0:
                    print(
                        f"[progress] episode={i+1}/{len(episode_files)} "
                        f"kept_in_episode={kept_in_episode} total_kept={total_kept_frames}"
                    )

        # episode 1개 = demonstration trajectory 1개로 저장한다.
        dataset.save_episode()
        kept_episodes += 1
        print(
            f"[{kept_episodes}] Converted: {ep_path} "
            f"(kept_frames={kept_in_episode}, total_kept={total_kept_frames})"
        )

    # 중요: finalize()가 parquet writer를 닫아 footer 메타데이터를 기록한다.
    # 이 호출이 없으면 데이터셋이 정상 로드되지 않는다.
    dataset.finalize()
    if args.drop_idle_sec and args.drop_idle_sec > 0.0:
        print(
            f"Idle filter: drop_idle_sec={args.drop_idle_sec}, "
            f"idle_joint_delta_thresh={args.idle_joint_delta_thresh}, "
            f"idle_keep_action_window_sec={args.idle_keep_action_window_sec}, "
            f"dropped_transitions={dropped_idle_frames_total}"
        )
    print(f"Done. Kept {kept_episodes} episodes -> {output_dir}")


if __name__ == "__main__":
    main()
