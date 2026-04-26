#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np


class CartesianTeleopState:
    def __init__(self, linear_speed: float, qvel_gain: float) -> None:
        self.linear_speed = linear_speed
        self.qvel_gain = qvel_gain
        self.frame = "world"
        self.v_cmd = np.zeros(3, dtype=np.float64)
        self.last_input_time = 0.0
        self.timeout_sec = 0.18
        self.running = True
        self.home_requested = False
        self.teleop_start_requested = False
        self.gripper_target = "open"

    def consume_if_stale(self) -> None:
        if (time.time() - self.last_input_time) > self.timeout_sec:
            self.v_cmd[:] = 0.0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keyboard Cartesian teleop for Indy7 in MuJoCo (X/Y/Z jog)."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "generated" / "indy7_mujoco.urdf",
        help="Path to MuJoCo-loadable URDF/MJCF model.",
    )
    parser.add_argument(
        "--ee-body-name",
        type=str,
        default="",
        help="Optional end-effector body name. Uses last body if omitted.",
    )
    parser.add_argument(
        "--linear-speed",
        type=float,
        default=0.16,
        help="Cartesian linear speed in m/s.",
    )
    parser.add_argument(
        "--damping",
        type=float,
        default=1.0e-4,
        help="Damped least-squares factor for pseudo-inverse.",
    )
    parser.add_argument(
        "--qvel-gain",
        type=float,
        default=3.0,
        help="Multiplier for solved joint velocity (higher feels stronger).",
    )
    parser.add_argument(
        "--max-qvel",
        type=float,
        default=2.5,
        help="Absolute per-joint velocity clamp in rad/s.",
    )
    parser.add_argument(
        "--dynamic",
        action="store_true",
        help="Use dynamic stepping (can sag under gravity). Default is kinematic.",
    )
    parser.add_argument(
        "--home-qpos",
        type=str,
        default="0,-0.436,2.007,0,1.571,0",
        help=(
            "Comma-separated home joint positions in rad for first 6 joints "
            "(e.g. 0,-0.436,2.007,0,1.571,0)."
        ),
    )
    parser.add_argument(
        "--teleop-start-qpos",
        type=str,
        default="0,0.611,-2.618,0,0.436,0",
        help=(
            "Comma-separated teleop-start joint positions in rad for first 6 joints "
            "(e.g. 0,0.611,-2.618,0,0.436,0)."
        ),
    )
    return parser


def _resolve_ee_body(model: mujoco.MjModel, ee_body_name: str) -> int:
    if ee_body_name:
        try:
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, ee_body_name)
        except Exception as exc:
            raise ValueError(f"Failed to resolve body name '{ee_body_name}'") from exc
        if body_id < 0:
            raise ValueError(f"Body '{ee_body_name}' not found in model.")
        return int(body_id)
    return int(model.nbody - 1)


def _print_help() -> None:
    print("\n" + "=" * 64)
    print(" Indy7 MuJoCo Cartesian Keyboard Teleop")
    print("=" * 64)
    print(" Arrow Up/Down or W/S : +X / -X")
    print(" Arrow Left/Right or A/D : +Y / -Y")
    print(" ; / . or Q/E : +Z / -Z")
    print(" Numpad-style 8/2/4/6 : +X/-X/+Y/-Y (fallback)")
    print(" [ / ] : speed down / up")
    print(" - / = : joint velocity gain down / up")
    print(" H : go to controller home pose")
    print(" Shift+H : go to teleop start pose")
    print(" G/O : grasp/open (real Mark7 preset)")
    print(" P/R : press/release (real Mark7 preset)")
    print(" B / T : frame world / tool")
    print(" Space : stop")
    print(" Q : quit")
    print("=" * 64 + "\n")


def _make_key_callback(state: CartesianTeleopState):
    def key_callback(keycode: int) -> None:
        raw_key = chr(keycode) if 0 <= keycode < 128 else ""
        key = raw_key.lower()
        state.v_cmd[:] = 0.0

        # Arrow key codes in MuJoCo GLFW callback.
        if keycode == 265 or key in ("w", "8"):  # UP
            state.v_cmd[0] = +state.linear_speed
        elif keycode == 264 or key in ("s", "2"):  # DOWN
            state.v_cmd[0] = -state.linear_speed
        elif keycode == 263 or key in ("a", "4"):  # LEFT
            state.v_cmd[1] = +state.linear_speed
        elif keycode == 262 or key in ("d", "6"):  # RIGHT
            state.v_cmd[1] = -state.linear_speed
        elif key in (";", "q"):
            state.v_cmd[2] = +state.linear_speed
        elif key in (".", "e"):
            state.v_cmd[2] = -state.linear_speed
        elif key == "[":
            state.linear_speed = max(0.01, state.linear_speed - 0.01)
            print(f"[speed] {state.linear_speed:.2f} m/s")
        elif key == "]":
            state.linear_speed = min(0.25, state.linear_speed + 0.01)
            print(f"[speed] {state.linear_speed:.2f} m/s")
        elif key == "-":
            state.qvel_gain = max(0.5, state.qvel_gain - 0.25)
            print(f"[qvel-gain] {state.qvel_gain:.2f}")
        elif key == "=":
            state.qvel_gain = min(8.0, state.qvel_gain + 0.25)
            print(f"[qvel-gain] {state.qvel_gain:.2f}")
        elif key == "b":
            state.frame = "world"
            print("[frame] world")
        elif key == "t":
            state.frame = "tool"
            print("[frame] tool")
        elif key == " ":
            pass
        elif key == "h":
            if raw_key == "H":
                state.teleop_start_requested = True
                print("[teleop-start] requested")
            else:
                state.home_requested = True
                print("[home] requested")
        elif key == "g":
            state.gripper_target = "grasp"
            print("[gripper] grasp")
        elif key == "o":
            state.gripper_target = "open"
            print("[gripper] open")
        elif key == "p":
            state.gripper_target = "press"
            print("[gripper] press")
        elif key == "r":
            state.gripper_target = "release"
            print("[gripper] release")
        elif key == "q":
            state.running = False

        state.last_input_time = time.time()

    return key_callback


def _solve_qvel(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    ee_body_id: int,
    v_cmd_world: np.ndarray,
    damping: float,
) -> np.ndarray:
    jacp = np.zeros((3, model.nv), dtype=np.float64)
    jacr = np.zeros((3, model.nv), dtype=np.float64)
    mujoco.mj_jacBodyCom(model, data, jacp, jacr, ee_body_id)

    jt = jacp.T
    jj_t = jacp @ jt
    reg = (damping * damping) * np.eye(3)
    qvel = jt @ np.linalg.solve(jj_t + reg, v_cmd_world)
    return qvel


def _tool_to_world_velocity(data: mujoco.MjData, ee_body_id: int, v_tool: np.ndarray) -> np.ndarray:
    xmat = data.xmat[ee_body_id].reshape(3, 3)
    return xmat @ v_tool


def _parse_home_qpos(text: str, nq: int) -> np.ndarray:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    vals = np.array([float(p) for p in parts], dtype=np.float64)
    if vals.size == 0:
        raise ValueError("--home-qpos must contain at least one value.")
    home = np.zeros((nq,), dtype=np.float64)
    n_copy = min(nq, vals.size)
    home[:n_copy] = vals[:n_copy]
    return home


def _apply_home_pose(model: mujoco.MjModel, data: mujoco.MjData, home_qpos: np.ndarray) -> None:
    data.qpos[:] = home_qpos
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)


def _joint_qpos_address(model: mujoco.MjModel, joint_name: str) -> int | None:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
    if joint_id < 0:
        return None
    return int(model.jnt_qposadr[joint_id])


def _drive_gripper(
    data: mujoco.MjData,
    joint_adrs: dict[str, int],
    target_mode: str,
    dt: float,
) -> None:
    if not joint_adrs:
        return
    # Real Mark7 preset source:
    # ros2_ws/src/mark7/pipet_hand_mark7_driver/config/grip_presets.yaml
    # order = [ThumbFlex, Index, Middle, Ring, Pinky, ThumbAb]
    preset_steps = {
        "open": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "grasp": [0.0, 0.0, 350.0, 350.0, 350.0, 0.0],
        "press": [150.0, 0.0, 350.0, 350.0, 350.0, 0.0],
        "release": [0.0, 0.0, 350.0, 350.0, 350.0, 0.0],
    }
    steps = preset_steps.get(target_mode, preset_steps["open"])

    def _to_rad_open_close(step: float, max_step: float = 300.0, max_rad: float = 1.396) -> float:
        s = np.clip(step, 0.0, max_step)
        return float((s / max_step) * max_rad)

    def _to_rad_thumb_flex(step: float, max_step: float = 187.0, max_rad: float = 0.872665) -> float:
        # thumb_bottom_middle_rev has range [-0.872665, 0.0]
        s = np.clip(step, 0.0, max_step)
        return float(-(s / max_step) * max_rad)

    target = {
        "mark7_thumb_bottom_middle_rev": _to_rad_thumb_flex(steps[0]),
        "mark7_base_index": _to_rad_open_close(steps[1]),
        "mark7_base_middle": _to_rad_open_close(steps[2]),
        "mark7_base_ringer": _to_rad_open_close(steps[3]),
        "mark7_base_pinky": _to_rad_open_close(steps[4]),
        "mark7_base_thumb": _to_rad_open_close(steps[5]),
    }
    speed = 1.8  # rad/s
    max_step = speed * dt
    for jname, jtarget in target.items():
        adr = joint_adrs.get(jname)
        if adr is None:
            continue
        curr = float(data.qpos[adr])
        delta = np.clip(jtarget - curr, -max_step, max_step)
        data.qpos[adr] = curr + delta

    # MuJoCo URDF import may ignore <mimic>. Mirror the coupled joints manually.
    mimic_pairs = [
        ("mark7_base_index", "mark7_index_bottom_top_rev"),
        ("mark7_base_middle", "mark7_middle_bottom_top_rev"),
        ("mark7_base_ringer", "mark7_ringer_bottom_top_rev"),
        ("mark7_base_pinky", "mark7_pinky_bottom_top"),
        ("mark7_thumb_bottom_middle_rev", "mark7_thumb_middle_top_rev"),
    ]
    for src_name, dst_name in mimic_pairs:
        src_adr = joint_adrs.get(src_name)
        dst_adr = joint_adrs.get(dst_name)
        if src_adr is None or dst_adr is None:
            continue
        data.qpos[dst_adr] = data.qpos[src_adr]


def main() -> None:
    args = _build_parser().parse_args()
    if not args.model.exists():
        raise FileNotFoundError(f"Model not found: {args.model}")

    model = mujoco.MjModel.from_xml_path(str(args.model))
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)
    mujoco.mj_forward(model, data)
    home_qpos = _parse_home_qpos(args.home_qpos, model.nq)
    teleop_start_qpos = _parse_home_qpos(args.teleop_start_qpos, model.nq)
    _apply_home_pose(model, data, home_qpos)

    ee_body_id = _resolve_ee_body(model, args.ee_body_name)
    mark7_joint_names = [
        "mark7_base_index",
        "mark7_index_bottom_top_rev",
        "mark7_base_middle",
        "mark7_middle_bottom_top_rev",
        "mark7_base_ringer",
        "mark7_ringer_bottom_top_rev",
        "mark7_base_pinky",
        "mark7_pinky_bottom_top",
        "mark7_base_thumb",
        "mark7_thumb_bottom_middle_rev",
        "mark7_thumb_middle_top_rev",
    ]
    mark7_joint_adrs = {
        name: adr
        for name in mark7_joint_names
        if (adr := _joint_qpos_address(model, name)) is not None
    }
    ee_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, ee_body_id) or f"id={ee_body_id}"
    print(f"[info] End-effector body: {ee_name}")
    if mark7_joint_adrs:
        print(f"[info] Mark7 joint control enabled ({len(mark7_joint_adrs)} joints)")
    else:
        print("[warn] Mark7 gripper joints not found in model")
    _print_help()

    state = CartesianTeleopState(
        linear_speed=args.linear_speed,
        qvel_gain=args.qvel_gain,
    )
    key_callback = _make_key_callback(state)

    with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as viewer:
        while viewer.is_running() and state.running:
            if state.home_requested:
                _apply_home_pose(model, data, home_qpos)
                state.home_requested = False
            if state.teleop_start_requested:
                _apply_home_pose(model, data, teleop_start_qpos)
                state.teleop_start_requested = False

            state.consume_if_stale()
            v_cmd = state.v_cmd.copy()
            if state.frame == "tool":
                v_cmd = _tool_to_world_velocity(data, ee_body_id, v_cmd)

            qvel = _solve_qvel(
                model=model,
                data=data,
                ee_body_id=ee_body_id,
                v_cmd_world=v_cmd,
                damping=args.damping,
            )
            qvel = np.clip(state.qvel_gain * qvel, -args.max_qvel, args.max_qvel)
            data.qvel[:] = qvel

            if not args.dynamic:
                # Kinematic teleop: integrate commanded joint velocities directly
                # so the arm does not sag under gravity when command is zero.
                data.qpos[:6] = data.qpos[:6] + data.qvel[:6] * model.opt.timestep
                _drive_gripper(
                    data=data,
                    joint_adrs=mark7_joint_adrs,
                    target_mode=state.gripper_target,
                    dt=model.opt.timestep,
                )
                mujoco.mj_forward(model, data)
            else:
                _drive_gripper(
                    data=data,
                    joint_adrs=mark7_joint_adrs,
                    target_mode=state.gripper_target,
                    dt=model.opt.timestep,
                )
                mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(model.opt.timestep)


if __name__ == "__main__":
    main()
