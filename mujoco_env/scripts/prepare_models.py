#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDY_SRC_URDF = ROOT / "indy7_urdf" / "indy.urdf"
INDY_VISUAL_MESH_DIR = ROOT / "indy7_urdf" / "meshes" / "indy7" / "visual"
INDY_DST_MESH_DIR = ROOT / "assets" / "indy7"
MARK7_DST_MESH_DIR = ROOT / "assets" / "mark7"
INDY_DST_URDF = ROOT / "generated" / "indy7_mujoco.urdf"

GRIPPER_START_MARKER = "<!-- MARK7_REAL_START -->"
GRIPPER_END_MARKER = "<!-- MARK7_REAL_END -->"


def _resolve_mark7_source_paths() -> tuple[Path, Path]:
    candidates = [
        ROOT.parent / "ros2_ws" / "src" / "mark7" / "pipet_hand_mark7_description",
        ROOT.parent / "external" / "pipet_gripper_Mark7" / "src" / "pipet_hand_mark7_description",
        ROOT.parent / "pipet_gripper_Mark7" / "src" / "pipet_hand_mark7_description",
    ]
    for base in candidates:
        xacro_path = base / "urdf" / "pipet_hand_mark7.xacro"
        mesh_dir = base / "meshes"
        if xacro_path.exists() and mesh_dir.exists():
            return xacro_path, mesh_dir
    raise FileNotFoundError(
        "Could not find Mark7 description. Expected one of: "
        "ros2_ws/src/mark7/pipet_hand_mark7_description or "
        "pipet_gripper_Mark7/src/pipet_hand_mark7_description"
    )


def _extract_mesh_names(urdf_text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r'filename="([^"]+)"', urdf_text):
        mesh_name = Path(match.group(1)).name
        if mesh_name.lower().endswith(".stl"):
            names.append(mesh_name)
    return sorted(set(names))


def _render_mark7_urdf(mark7_src_xacro: Path) -> str:
    if not mark7_src_xacro.exists():
        raise FileNotFoundError(f"Mark7 xacro not found: {mark7_src_xacro}")
    proc = subprocess.run(
        ["xacro", str(mark7_src_xacro)],
        check=True,
        capture_output=True,
        text=True,
    )
    text = proc.stdout

    # Keep only inner robot content.
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<robot[^>]*>", "", text)
    text = text.replace("</robot>", "")

    # Remove ROS/Gazebo-specific tags that MuJoCo does not use.
    text = re.sub(r"<gazebo[\s\S]*?</gazebo>", "", text)
    text = re.sub(r"<transmission[\s\S]*?</transmission>", "", text)
    text = re.sub(r"<ros2_control[\s\S]*?</ros2_control>", "", text)

    # Route mark7 meshes through mujoco_env/assets/mark7.
    text = re.sub(
        r'package://pipet_hand_mark7_description/meshes/([^"]+)',
        r"mark7/\1",
        text,
    )

    # Prefix links/joints to avoid accidental name collisions.
    text = re.sub(r'link="([^"]+)"', r'link="mark7_\1"', text)
    text = re.sub(r'<link name="([^"]+)"', r'<link name="mark7_\1"', text)
    text = re.sub(r'<joint name="([^"]+)"', r'<joint name="mark7_\1"', text)
    text = re.sub(r'joint="([^"]+)"', r'joint="mark7_\1"', text)

    # Mount transformed Mark7 base to Indy link6.
    mount_joint = (
        '  <joint name="mark7_mount_joint" type="fixed">\n'
        '    <parent link="link6" />\n'
        '    <child link="mark7_base_link" />\n'
        '    <origin xyz="0.000 0.000 0.085" rpy="0 0 0" />\n'
        "  </joint>\n"
    )
    return f"  {GRIPPER_START_MARKER}\n{mount_joint}\n{text}\n  {GRIPPER_END_MARKER}\n"


def prepare_indy7_model() -> Path:
    mark7_src_xacro, mark7_src_mesh_dir = _resolve_mark7_source_paths()

    if not INDY_SRC_URDF.exists():
        raise FileNotFoundError(f"Indy7 URDF not found: {INDY_SRC_URDF}")
    if not INDY_VISUAL_MESH_DIR.exists():
        raise FileNotFoundError(f"Indy7 visual mesh dir not found: {INDY_VISUAL_MESH_DIR}")
    if not mark7_src_mesh_dir.exists():
        raise FileNotFoundError(f"Mark7 mesh dir not found: {mark7_src_mesh_dir}")

    urdf = INDY_SRC_URDF.read_text(encoding="utf-8")
    mesh_names = _extract_mesh_names(urdf)
    if not mesh_names:
        raise RuntimeError("No STL meshes found in Indy7 URDF.")

    INDY_DST_MESH_DIR.mkdir(parents=True, exist_ok=True)

    for mesh_name in mesh_names:
        src_mesh = INDY_VISUAL_MESH_DIR / mesh_name
        if not src_mesh.exists():
            raise FileNotFoundError(f"Expected mesh missing: {src_mesh}")
        shutil.copy2(src_mesh, INDY_DST_MESH_DIR / mesh_name)

    MARK7_DST_MESH_DIR.mkdir(parents=True, exist_ok=True)
    for stl in mark7_src_mesh_dir.glob("*.stl"):
        shutil.copy2(stl, MARK7_DST_MESH_DIR / stl.name)

    # MuJoCo URDF loader uses compiler meshdir. Use ../assets root with per-robot subdirs.
    urdf = re.sub(
        r'filename="[^"]*[/\\\\]([^"/\\\\]+\.stl)"',
        r'filename="indy7/\1"',
        urdf,
        flags=re.IGNORECASE,
    )

    if "<mujoco>" not in urdf:
        compiler_block = (
            "  <mujoco>\n"
            "    <compiler meshdir=\"../assets\" balanceinertia=\"true\"/>\n"
            "  </mujoco>\n"
        )
        urdf = urdf.replace("<robot name=\"indy\">", "<robot name=\"indy\">\n" + compiler_block, 1)
    else:
        urdf = re.sub(
            r'<compiler\s+meshdir="[^"]+"',
            '<compiler meshdir="../assets"',
            urdf,
        )

    # Keep this idempotent by replacing any previously injected gripper block.
    if GRIPPER_START_MARKER in urdf and GRIPPER_END_MARKER in urdf:
        start_idx = urdf.index(GRIPPER_START_MARKER)
        end_idx = urdf.index(GRIPPER_END_MARKER) + len(GRIPPER_END_MARKER)
        urdf = urdf[:start_idx] + urdf[end_idx:]

    mark7_inner = _render_mark7_urdf(mark7_src_xacro)
    urdf = urdf.replace("</robot>", mark7_inner + "\n</robot>")

    INDY_DST_URDF.parent.mkdir(parents=True, exist_ok=True)
    INDY_DST_URDF.write_text(urdf, encoding="utf-8")
    return INDY_DST_URDF


if __name__ == "__main__":
    output = prepare_indy7_model()
    print(f"Prepared Indy7 MuJoCo URDF: {output}")
