#!/usr/bin/env python3
"""Operator GUI for model inference, HOME, and live camera views."""

from __future__ import annotations

import argparse
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import rclpy
from cv_bridge import CvBridge
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QKeyEvent, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from rclpy.node import Node
from sensor_msgs.msg import Image


DEFAULT_MODEL_REL = (
    "ai/models/act_remove_grasp_focus_3s2s_cartesian_360_v2/checkpoints/070000"
)
DEFAULT_ENDPOINT = "tcp://127.0.0.1:5560"


def _repo_root_from_file() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "run_scripts").is_dir() and (parent / "ros2_ws").is_dir():
            return parent
    return Path.cwd()


def parse_args() -> argparse.Namespace:
    repo = _repo_root_from_file()
    parser = argparse.ArgumentParser(description="Pipet operator GUI")
    parser.add_argument("--repo-root", default=str(repo))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--indy-ip", default="192.168.1.10")
    parser.add_argument("--mark7-port", default="/dev/ttyACM0")
    parser.add_argument("--fk-urdf-path", default="")
    parser.add_argument("--state-target-dim", default="18")
    parser.add_argument("--zmq-endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--conda-env", default="lerobot")
    parser.add_argument(
        "--conda-setup",
        default="/home/sirlab/miniconda3/etc/profile.d/conda.sh",
    )
    parser.add_argument("--home-vel-ratio", default="5")
    parser.add_argument("--home-acc-ratio", default="5")
    parser.add_argument("--disable-gripper", action="store_true")
    parser.add_argument("--model-start-delay-ms", type=int, default=4000)
    return parser.parse_args()


class CameraNode(Node):
    def __init__(self) -> None:
        super().__init__("pipet_operator_gui")
        self._bridge = CvBridge()
        self.frames: dict[str, Optional[np.ndarray]] = {
            "wrist": None,
            "overhead": None,
        }
        self.frame_wall_time = {"wrist": 0.0, "overhead": 0.0}
        self.frame_count = {"wrist": 0, "overhead": 0}

        self.create_subscription(
            Image,
            "/wrist_camera/camera/color/image_raw",
            lambda msg: self._image_cb("wrist", msg),
            10,
        )
        self.create_subscription(
            Image,
            "/overhead_camera/camera/color/image_raw",
            lambda msg: self._image_cb("overhead", msg),
            10,
        )

    def _image_cb(self, name: str, msg: Image) -> None:
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
        except Exception as exc:
            self.get_logger().warn(f"{name} image conversion failed: {exc}")
            return
        self.frames[name] = np.ascontiguousarray(frame)
        self.frame_wall_time[name] = time.monotonic()
        self.frame_count[name] += 1


class OperatorWindow(QMainWindow):
    def __init__(self, args: argparse.Namespace, node: CameraNode) -> None:
        super().__init__()
        self.args = args
        self.node = node
        self.repo_root = Path(args.repo_root).expanduser().resolve()
        self.model_path = (
            Path(args.model_path).expanduser().resolve()
            if args.model_path
            else self.repo_root / DEFAULT_MODEL_REL
        )

        self.model_proc: Optional[subprocess.Popen[bytes]] = None
        self.inference_proc: Optional[subprocess.Popen[bytes]] = None
        self.home_proc: Optional[subprocess.Popen[bytes]] = None
        self._log_handles = []

        self.setWindowTitle("Pipet Operator")
        self.resize(1280, 760)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        controls = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.home_button = QPushButton("Home")
        self.stop_button = QPushButton("Stop")
        self.status_label = QLabel("Idle")
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        controls.addWidget(self.start_button)
        controls.addWidget(self.home_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.status_label)
        layout.addLayout(controls)

        cameras = QHBoxLayout()
        self.wrist_label = self._make_camera_label("Wrist camera")
        self.overhead_label = self._make_camera_label("Overhead camera")
        cameras.addWidget(self.wrist_label)
        cameras.addWidget(self.overhead_label)
        layout.addLayout(cameras, stretch=1)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(200)
        self.log_view.setMaximumHeight(140)
        layout.addWidget(self.log_view)

        self.start_button.clicked.connect(self.start_stack)
        self.home_button.clicked.connect(self.move_home)
        self.stop_button.clicked.connect(self.stop_stack)

        self.spin_timer = QTimer(self)
        self.spin_timer.timeout.connect(self._spin_ros_once)
        self.spin_timer.start(15)

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._refresh)
        self.frame_timer.start(80)

        self._log("Ready")

    def _make_camera_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(480, 320)
        label.setStyleSheet("background-color: #111; color: #ddd;")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return label

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key_A:
            self.start_stack()
            return
        if event.key() == Qt.Key_H:
            self.move_home()
            return
        if event.key() == Qt.Key_S:
            self.stop_stack()
            return
        super().keyPressEvent(event)

    def _spin_ros_once(self) -> None:
        rclpy.spin_once(self.node, timeout_sec=0.0)

    def _refresh(self) -> None:
        self._set_camera_pixmap("wrist", self.wrist_label)
        self._set_camera_pixmap("overhead", self.overhead_label)
        self._refresh_process_status()

    def _set_camera_pixmap(self, name: str, label: QLabel) -> None:
        frame = self.node.frames.get(name)
        if frame is None:
            return
        height, width, channels = frame.shape
        qimg = QImage(
            frame.data,
            width,
            height,
            channels * width,
            QImage.Format_RGB888,
        ).copy()
        pixmap = QPixmap.fromImage(qimg).scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        label.setPixmap(pixmap)

    def _refresh_process_status(self) -> None:
        model = "model:on" if self._proc_alive(self.model_proc) else "model:off"
        infer = "robot:on" if self._proc_alive(self.inference_proc) else "robot:off"
        wrist_age = self._frame_age("wrist")
        overhead_age = self._frame_age("overhead")
        self.status_label.setText(
            f"{model} | {infer} | wrist {wrist_age} | overhead {overhead_age}"
        )

    def _frame_age(self, name: str) -> str:
        stamp = self.node.frame_wall_time.get(name, 0.0)
        if stamp <= 0.0:
            return "no frame"
        age = time.monotonic() - stamp
        return f"{age:.1f}s"

    def start_stack(self) -> None:
        if not self.model_path.exists():
            self._log(f"Model path not found: {self.model_path}")
            return
        self._start_model_server()
        QTimer.singleShot(self.args.model_start_delay_ms, self._start_inference_launch)

    def _start_model_server(self) -> None:
        if self._proc_alive(self.model_proc):
            self._log("Model server already running")
            return

        py_paths = [
            self.repo_root / "ros2_ws/src/pipet_inference",
            self.repo_root / "install/pipet_inference/lib/python3.10/site-packages",
            self.repo_root
            / "ros2_ws/install/pipet_inference/lib/python3.10/site-packages",
        ]
        py_path = ":".join(str(p) for p in py_paths if p.exists())
        setup = Path(self.args.conda_setup)
        setup_line = (
            f"source {shlex.quote(str(setup))}"
            if setup.exists()
            else "source ~/miniconda3/etc/profile.d/conda.sh"
        )
        command = f"""
set -e
cd {shlex.quote(str(self.repo_root))}
source /opt/ros/humble/setup.bash
if [ -f {shlex.quote(str(self.repo_root / "install/setup.bash"))} ]; then
  source {shlex.quote(str(self.repo_root / "install/setup.bash"))}
fi
{setup_line}
conda activate {shlex.quote(self.args.conda_env)}
export PYTHONPATH={shlex.quote(py_path)}:${{PYTHONPATH:-}}
python -m pipet_inference.zmq_act_server \
  --bind {shlex.quote(self.args.zmq_endpoint)} \
  --model-path {shlex.quote(str(self.model_path))}
"""
        self.model_proc = self._popen(
            ["bash", "-lc", command],
            "operator_gui_model_server.log",
        )
        self._log(f"Model server starting: pid={self.model_proc.pid}")

    def _start_inference_launch(self) -> None:
        if self._proc_alive(self.inference_proc):
            self._log("Robot inference already running")
            return

        script = self.repo_root / "run_scripts/40_inference_ros.sh"
        extra = [
            "autonomy_enabled:=true",
            "use_zmq_sidecar:=true",
            f"zmq_endpoint:={self.args.zmq_endpoint}",
            "control_mode:=cartesian",
            "image_target_height:=360",
            "image_target_width:=480",
            "grasp_min_elapsed_steps:=50",
            "grasp_delay_steps:=12",
            "grasp_confirm_steps:=12",
            "max_delta_mm:=1.0",
            "max_delta_deg:=1.0",
            "max_cartesian_speed_mm_s:=10.0",
            "max_angular_speed_deg_s:=10.0",
        ]
        if self.args.disable_gripper:
            extra.append("enable_gripper:=false")

        cmd = [
            str(script),
            str(self.model_path),
            self.args.indy_ip,
            self.args.mark7_port,
            self.args.fk_urdf_path,
            str(self.args.state_target_dim),
            *extra,
        ]
        self.inference_proc = self._popen(cmd, "operator_gui_inference.log")
        self._log(f"Robot inference starting: pid={self.inference_proc.pid}")

    def move_home(self) -> None:
        if self._proc_alive(self.home_proc):
            self._log("HOME command already running")
            return
        cmd = [
            "/usr/bin/python3",
            str(self.repo_root / "tools/control_indy7/indy7/move_home.py"),
            "--ip",
            self.args.indy_ip,
            "--stop-teleop",
            "--stop-before",
            "--servo-on",
            "--vel-ratio",
            str(self.args.home_vel_ratio),
            "--acc-ratio",
            str(self.args.home_acc_ratio),
        ]
        self.home_proc = self._popen(cmd, "operator_gui_home.log")
        self._log(f"HOME command sent: pid={self.home_proc.pid}")

    def stop_stack(self) -> None:
        self._stop_proc("robot inference", self.inference_proc)
        self._stop_proc("model server", self.model_proc)
        self.inference_proc = None
        self.model_proc = None

    def _popen(self, cmd: list[str], log_name: str) -> subprocess.Popen[bytes]:
        log_dir = self.repo_root / "log"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / log_name
        handle = log_path.open("a", buffering=1)
        self._log_handles.append(handle)
        handle.write(f"\n\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] $ {' '.join(cmd)}\n")
        return subprocess.Popen(
            cmd,
            cwd=str(self.repo_root),
            stdout=handle,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )

    def _stop_proc(
        self, label: str, proc: Optional[subprocess.Popen[bytes]], timeout: float = 8.0
    ) -> None:
        if not self._proc_alive(proc):
            return
        assert proc is not None
        self._log(f"Stopping {label}: pid={proc.pid}")
        try:
            os.killpg(proc.pid, signal.SIGINT)
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    @staticmethod
    def _proc_alive(proc: Optional[subprocess.Popen[bytes]]) -> bool:
        return proc is not None and proc.poll() is None

    def _log(self, message: str) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {message}"
        self.log_view.appendPlainText(line)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.stop_stack()
        for handle in self._log_handles:
            try:
                handle.close()
            except Exception:
                pass
        event.accept()


def main() -> None:
    args = parse_args()
    rclpy.init(args=None)
    node = CameraNode()
    app = QApplication(sys.argv[:1])
    window = OperatorWindow(args, node)
    window.show()
    try:
        exit_code = app.exec_()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
