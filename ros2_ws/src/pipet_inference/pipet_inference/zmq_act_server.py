#!/usr/bin/env python3
"""
LeRobot ACT ZMQ 추론 서버 (conda `lerobot` / Python 3.12+ 에서 실행).

ROS 노드(NumPy 1.x)와 conda(NumPy 2.x) 간 pickle 호환이 없어 **raw bytes 멀티파트** 프로토콜을 쓴다.

터미널 1:
  export PYTHONPATH="/path/to/ros2_ws/install/pipet_inference/lib/python3.10/site-packages:$PYTHONPATH"
  conda activate lerobot
  python -m pipet_inference.zmq_act_server \\
    --bind tcp://127.0.0.1:5560 \\
    --model-path .../checkpoints/last
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np

FMT_V2 = "pipet_zmq_v2"


def _send_err(sock: Any, msg: str) -> None:
    sock.send_multipart([json.dumps({"ok": False, "error": msg}).encode("utf-8"), b""])


def main() -> None:
    parser = argparse.ArgumentParser(description="LeRobot ACT ZMQ REP 서버")
    parser.add_argument("--bind", default="tcp://127.0.0.1:5560", help="ZMQ bind 주소")
    parser.add_argument("--model-path", required=True, help="checkpoints/last 또는 pretrained_model")
    parser.add_argument("--dataset-repo-id", default="pipet_dataset")
    parser.add_argument("--dataset-root", default="", help="비우면 train_config.json에서 읽음")
    parser.add_argument("--task", default="Pick up the pipette")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    try:
        import zmq
    except ImportError:
        print("zmq 필요: conda install pyzmq 또는 pip install pyzmq", file=sys.stderr)
        sys.exit(1)

    from pipet_inference.lerobot_act_backend import (
        LeRobotActBackend,
        read_dataset_root_from_train_config,
        resolve_pretrained_model_dir,
    )

    pretrained_dir = resolve_pretrained_model_dir(args.model_path)
    ds_root = args.dataset_root.strip()
    if not ds_root:
        ds_root = read_dataset_root_from_train_config(pretrained_dir)
    if not ds_root:
        print("dataset-root 필요하거나 train_config.json에 dataset.root가 있어야 합니다.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading ACT: {pretrained_dir}\ndataset_root={ds_root}", flush=True)
    backend = LeRobotActBackend(
        pretrained_model_dir=pretrained_dir,
        dataset_repo_id=args.dataset_repo_id,
        dataset_root=Path(ds_root),
        device=args.device,
        task=args.task,
    )

    ctx = zmq.Context()
    sock = ctx.socket(zmq.REP)
    sock.bind(args.bind)
    print(f"zmq_act_server listening {args.bind} (protocol {FMT_V2})", flush=True)

    while True:
        try:
            parts = sock.recv_multipart()
        except Exception as e:
            continue

        if len(parts) == 1:
            try:
                req = pickle.loads(parts[0])
            except Exception as e:
                _send_err(sock, f"legacy pickle recv: {e}")
                continue
            if req.get("ping"):
                sock.send(pickle.dumps({"ok": True, "pong": True}))
                continue
            _send_err(sock, "legacy pickle obs deprecated; update inference_node")
            continue

        if len(parts) not in (4, 6):
            _send_err(sock, f"expected 4 or 6 multipart frames, got {len(parts)}")
            continue

        try:
            hdr: dict[str, Any] = json.loads(parts[0].decode("utf-8"))
        except Exception as e:
            _send_err(sock, f"bad json header: {e}")
            continue

        if hdr.get("fmt") != FMT_V2:
            _send_err(sock, f"unknown fmt {hdr.get('fmt')!r}")
            continue

        try:
            ss = tuple(int(x) for x in hdr["state_shape"])
            fs = tuple(int(x) for x in hdr["front_shape"])
            os_ = tuple(int(x) for x in hdr["over_shape"])
            n_state = int(np.prod(ss, dtype=np.int64)) * 4
            n_front = int(np.prod(fs, dtype=np.int64))
            n_over = int(np.prod(os_, dtype=np.int64))
            if len(parts[1]) != n_state or len(parts[2]) != n_front or len(parts[3]) != n_over:
                _send_err(
                    sock,
                    f"byte len mismatch state {len(parts[1])}!={n_state}, "
                    f"front {len(parts[2])}!={n_front}, over {len(parts[3])}!={n_over}",
                )
                continue

            obs = {
                "observation.state": np.frombuffer(parts[1], dtype=np.float32).reshape(ss).copy(),
                "observation.images.front": np.frombuffer(parts[2], dtype=np.uint8).reshape(fs).copy(),
                "observation.images.overhead": np.frombuffer(parts[3], dtype=np.uint8).reshape(os_).copy(),
            }
            if len(parts) == 6:
                fds = tuple(int(x) for x in hdr.get("front_depth_shape", []))
                ods = tuple(int(x) for x in hdr.get("over_depth_shape", []))
                if not fds or not ods:
                    _send_err(sock, "depth frames provided but depth shapes missing in header")
                    continue
                n_fd = int(np.prod(fds, dtype=np.int64))
                n_od = int(np.prod(ods, dtype=np.int64))
                if len(parts[4]) != n_fd or len(parts[5]) != n_od:
                    _send_err(
                        sock,
                        f"byte len mismatch front_depth {len(parts[4])}!={n_fd}, "
                        f"over_depth {len(parts[5])}!={n_od}",
                    )
                    continue
                obs["observation.images.front_depth"] = (
                    np.frombuffer(parts[4], dtype=np.uint8).reshape(fds).copy()
                )
                obs["observation.images.overhead_depth"] = (
                    np.frombuffer(parts[5], dtype=np.uint8).reshape(ods).copy()
                )
            action = backend.predict(obs)
            a = np.ascontiguousarray(action, dtype=np.float32).reshape(-1)
            if a.size != 7:
                _send_err(sock, f"bad action dim {a.size}")
                continue
            sock.send_multipart(
                [json.dumps({"ok": True}).encode("utf-8"), a.tobytes()]
            )
        except Exception as e:
            _send_err(sock, repr(e))


if __name__ == "__main__":
    main()
