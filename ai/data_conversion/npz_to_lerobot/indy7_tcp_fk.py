"""
Indy7 TCP forward kinematics from URDF (Pinocchio).

Used by npz_to_lerobot/convert.py when ``--state_profile extended`` and NPZ has no ``ee_pose``.
Output matches project convention: ``(x, y, z, qx, qy, qz, qw)`` in the URDF root / world frame.

Requires: ``pip install pin`` or ``conda install -c conda-forge pinocchio``.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import numpy as np

try:
    import pinocchio as pin
except ImportError:  # pragma: no cover
    pin = None


def _rot_to_quat_xyzw(R) -> np.ndarray:
    Rm = np.asarray(R, dtype=np.float64).reshape(3, 3)
    try:
        from scipy.spatial.transform import Rotation as SciRot

        q = SciRot.from_matrix(Rm).as_quat()
        return q.astype(np.float32)
    except Exception:  # pragma: no cover
        if pin is None:
            raise
        qu = pin.Quaternion(Rm)
        return np.array([float(qu.x), float(qu.y), float(qu.z), float(qu.w)], dtype=np.float32)


class Indy7TcpFk:
    """Single-arm Indy7: six revolute joints -> tcp frame pose."""

    def __init__(
        self,
        urdf_path: str,
        *,
        tcp_frame: str = "tcp",
        joint_names: Optional[List[str]] = None,
    ) -> None:
        if pin is None:  # pragma: no cover
            raise ImportError(
                "pinocchio is required for --fk_urdf FK. "
                "Try: conda install -c conda-forge pinocchio"
            )
        path = Path(urdf_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"URDF not found: {path}")
        self._urdf = str(path)
        self.model = pin.buildModelFromUrdf(self._urdf)
        self.data = self.model.createData()
        # 일부 URDF(Indy+그리퍼 합성 등)는 동일 이름의 FRAME/BODY가 같이 있어 모호해질 수 있다.
        try:
            self.tcp_fid = int(self.model.getFrameId(tcp_frame, pin.BODY))
        except (ValueError, TypeError, AttributeError):
            self.tcp_fid = int(self.model.getFrameId(tcp_frame))
        n_fr = len(self.model.frames)
        if self.tcp_fid < 0 or self.tcp_fid >= n_fr:
            raise ValueError(f"Frame {tcp_frame!r} not found in URDF (frames={n_fr})")
        jn = joint_names if joint_names is not None else [f"joint{i}" for i in range(6)]
        if len(jn) != 6:
            raise ValueError(f"joint_names must have length 6, got {len(jn)}")
        self._joint_q_indices: list[int] = []
        for name in jn:
            jid = int(self.model.getJointId(name))
            if jid == 0:
                raise ValueError(f"Unknown joint name in URDF: {name!r}")
            joint = self.model.joints[jid]
            if int(joint.nq) != 1:
                raise ValueError(
                    f"Joint {name!r} has nq={joint.nq}; expected a single revolute (nq=1) for this helper."
                )
            self._joint_q_indices.append(int(joint.idx_q))

    def compute(self, q6: np.ndarray) -> np.ndarray:
        """Return (7,) float32 [x,y,z,qx,qy,qz,qw]."""
        if pin is None:  # pragma: no cover
            raise ImportError("pinocchio is not installed")
        q_full = pin.neutral(self.model)
        q6a = np.asarray(q6, dtype=np.float64).reshape(6)
        for i in range(6):
            q_full[self._joint_q_indices[i]] = float(q6a[i])
        pin.forwardKinematics(self.model, self.data, q_full)
        pin.updateFramePlacements(self.model, self.data)
        T = self.data.oMf[int(self.tcp_fid)]
        p = T.translation
        R = T.rotation
        quat = _rot_to_quat_xyzw(R)
        return np.array(
            [float(p[0]), float(p[1]), float(p[2]), float(quat[0]), float(quat[1]), float(quat[2]), float(quat[3])],
            dtype=np.float32,
        )
