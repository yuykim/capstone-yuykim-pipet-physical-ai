"""ROS2 (Python 3.10) → conda LeRobot: ZMQ 멀티파트(raw bytes)로 NumPy 버전 호환."""

from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    import zmq
except ImportError as e:
    zmq = None  # type: ignore
    _ZMQ_IMPORT_ERROR = e
else:
    _ZMQ_IMPORT_ERROR = None

FMT_V2 = "pipet_zmq_v2"


class ZmqLerobotClient:
    def __init__(self, endpoint: str, *, timeout_ms: int = 10_000) -> None:
        if zmq is None:
            raise RuntimeError(
                "pyzmq 없음. `sudo apt install python3-zmq` 후 다시 빌드하세요."
            ) from _ZMQ_IMPORT_ERROR
        self._ctx = zmq.Context.instance()
        self._sock = self._ctx.socket(zmq.REQ)
        self._sock.setsockopt(zmq.RCVTIMEO, timeout_ms)
        self._sock.setsockopt(zmq.SNDTIMEO, timeout_ms)
        self._sock.connect(endpoint)
        self._endpoint = endpoint

    def predict(self, observation: dict[str, np.ndarray]) -> np.ndarray:
        state = np.ascontiguousarray(observation["observation.state"], dtype=np.float32)
        front = np.ascontiguousarray(observation["observation.images.front"], dtype=np.uint8)
        over = np.ascontiguousarray(observation["observation.images.overhead"], dtype=np.uint8)

        header: dict[str, Any] = {
            "fmt": FMT_V2,
            "state_shape": list(state.shape),
            "front_shape": list(front.shape),
            "over_shape": list(over.shape),
        }
        b0 = json.dumps(header).encode("utf-8")
        b1 = state.tobytes()
        b2 = front.tobytes()
        b3 = over.tobytes()

        exp1 = int(np.prod(state.shape, dtype=np.int64)) * 4
        exp2 = int(np.prod(front.shape, dtype=np.int64))
        exp3 = int(np.prod(over.shape, dtype=np.int64))
        if len(b1) != exp1 or len(b2) != exp2 or len(b3) != exp3:
            raise ValueError(
                f"observation buffer size mismatch: state {len(b1)}!={exp1}, "
                f"front {len(b2)}!={exp2}, over {len(b3)}!={exp3}"
            )

        self._sock.send_multipart([b0, b1, b2, b3])
        parts = self._sock.recv_multipart()
        if not parts:
            raise RuntimeError("empty zmq response")
        hdr = json.loads(parts[0].decode("utf-8"))
        if not hdr.get("ok"):
            raise RuntimeError(hdr.get("error", "inference failed"))
        if len(parts) < 2 or len(parts[1]) < 7 * 4:
            raise RuntimeError("missing action bytes in zmq response")
        return np.frombuffer(parts[1], dtype=np.float32, count=7).copy()
