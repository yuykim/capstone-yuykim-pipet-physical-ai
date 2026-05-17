# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Context

This is a physical AI project for pipette manipulation using:

- Neuromeka Indy7 arm
- Mand.ro Mark7 hand
- Intel RealSense D435 cameras
- ROS2 Humble on Ubuntu 22.04
- LeRobot-based data conversion, training, and inference experiments

The main data path is:

```text
ROS2 teleop/data collection -> episode_*.npz -> LeRobotDataset -> training -> ROS2 inference
```

## Repository Map

- `ros2_ws/src/`: ROS2 workspace and runtime packages.
- `ros2_ws/src/pipet_bringup/`: integrated launch files.
- `ros2_ws/src/pipet_data_collector/`: synchronized NPZ recording.
- `ros2_ws/src/pipet_system_teleop/`: keyboard teleop and recording control.
- `ros2_ws/src/pipet_inference/`: trained-policy inference nodes and helpers.
- `ros2_ws/src/mark7/`: Mark7 messages, driver, description, and teleop.
- `ai/`: data conversion, LeRobot training wrappers, logs, and vendored/reference LeRobot source.
- `mujoco_env/`: experimental MuJoCo workspace. It was intended to simulate Indy7 and the Mark7 gripper interacting in a virtual scene, but it is not a working production path yet.
- `docs/`: architecture, interface, history, Mark7, and AI notes.

## Working Rules

- Prefer small, focused changes. Do not merge broad branch differences when only one feature is needed.
- Be especially careful with `mujoco_env/`: it contains large mesh assets. Do not delete, move, or regenerate these files unless explicitly requested.
- Do not assume `mujoco_env/` is functional. Treat it as an incomplete prototype unless the user explicitly asks to revive or debug it.
- Be especially careful with `ai/lerobot_source/`: it is vendored/reference upstream code. Avoid editing it unless the task specifically requires a LeRobot patch.
- Do not commit datasets, checkpoints, cache, or runtime logs. Expected generated paths include `episodes/`, `ai/datasets/`, `ai/models/`, `ai/.cache/`, `build/`, `install/`, and `log/`.
- Preserve the NPZ contract used by conversion and training unless updating every dependent path together.
- For branch integration, inspect diff scope first. Cherry-pick or manually port targeted commits when another branch contains unrelated deletions or regressions.
- Keep ROS topic/service names stable unless the interface docs and all call sites are updated together.

## ROS2 Commands

Build:

```bash
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
colcon build --symlink-install
source install/setup.bash
```

Build one package:

```bash
colcon build --symlink-install --packages-select <package_name>
```

Data collection:

```bash
ros2 launch pipet_bringup data_collection.launch.py indy_ip:=192.168.1.10
ros2 run pipet_system_teleop system_teleop_node
```

## Verification

For Python-only edits, at minimum run an AST parse when ROS dependencies are unavailable:

```bash
python -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8-sig'), filename=p) for p in ['path/to/file.py']]"
```

For ROS package changes, prefer `colcon build --symlink-install --packages-select <package_name>` in a sourced ROS2 Humble environment.

## Data Contract

Collected NPZ episodes are expected to contain:

- `timestamps`: `(N,)`
- `task_name`: scalar string metadata such as `remove` or `insert`
- `joint_positions`: `(N, 6)`
- `joint_velocities`: `(N, 6)`
- `wrist_rgb_images`: `(N, H, W, 3)`
- `overhead_rgb_images`: `(N, H, W, 3)`
- `gripper_actions`: `(N,)`, where `0=hold`, `1=grasp`, `2=open`, `3=press`, `4=release`
- `final_gripper_action`: scalar int8
- `quality_warnings`: `(M,)` string warnings

Episodes may be stored under `episodes/<task_name>/success/`, `episodes/<task_name>/fail/`, or `episodes/<task_name>/unlabeled/`. Legacy/manual episodes may still be stored directly under `episodes/success/`, `episodes/fail/`, or `episodes/unlabeled/`.
