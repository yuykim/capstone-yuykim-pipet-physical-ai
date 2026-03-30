#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Indy7 digital twin in MuJoCo viewer.")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "generated" / "indy7_mujoco.urdf",
        help="Path to URDF/MJCF model.",
    )
    args = parser.parse_args()

    model = mujoco.MjModel.from_xml_path(str(args.model))
    data = mujoco.MjData(model)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        t0 = time.time()
        while viewer.is_running():
            t = time.time() - t0
            for j in range(model.nq):
                data.qpos[j] = 0.35 * np.sin(0.8 * t + 0.4 * j)
            mujoco.mj_forward(model, data)
            viewer.sync()
            time.sleep(model.opt.timestep)


if __name__ == "__main__":
    main()
