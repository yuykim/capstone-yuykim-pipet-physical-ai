#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDY_SRC_URDF = ROOT / "indy7_urdf" / "indy.urdf"
INDY_VISUAL_MESH_DIR = ROOT / "indy7_urdf" / "meshes" / "indy7" / "visual"
INDY_DST_MESH_DIR = ROOT / "assets" / "indy7"
INDY_DST_URDF = ROOT / "generated" / "indy7_mujoco.urdf"


def _extract_mesh_names(urdf_text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r'filename="([^"]+)"', urdf_text):
        mesh_name = Path(match.group(1)).name
        if mesh_name.lower().endswith(".stl"):
            names.append(mesh_name)
    return sorted(set(names))


def prepare_indy7_model() -> Path:
    if not INDY_SRC_URDF.exists():
        raise FileNotFoundError(f"Indy7 URDF not found: {INDY_SRC_URDF}")
    if not INDY_VISUAL_MESH_DIR.exists():
        raise FileNotFoundError(f"Indy7 visual mesh dir not found: {INDY_VISUAL_MESH_DIR}")

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

    # MuJoCo URDF loader uses basename for mesh files. Keep only basename
    # and provide meshdir through <mujoco><compiler>.
    urdf = re.sub(
        r'filename="[^"]*[/\\\\]([^"/\\\\]+\.stl)"',
        r'filename="\1"',
        urdf,
        flags=re.IGNORECASE,
    )

    if "<mujoco>" not in urdf:
        compiler_block = (
            "  <mujoco>\n"
            "    <compiler meshdir=\"../assets/indy7\" balanceinertia=\"true\"/>\n"
            "  </mujoco>\n"
        )
        urdf = urdf.replace("<robot name=\"indy\">", "<robot name=\"indy\">\n" + compiler_block, 1)

    INDY_DST_URDF.parent.mkdir(parents=True, exist_ok=True)
    INDY_DST_URDF.write_text(urdf, encoding="utf-8")
    return INDY_DST_URDF


if __name__ == "__main__":
    output = prepare_indy7_model()
    print(f"Prepared Indy7 MuJoCo URDF: {output}")
