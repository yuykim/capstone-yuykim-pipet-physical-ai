#!/usr/bin/env python3
"""
Inference Launch — Indy7 + Mark7 + RealSense(손목·오버헤드) + LeRobot ACT (ZMQ 사이드카).

ROS Humble = Python 3.10, LeRobot conda = 3.12+ 이므로 추론은 별도 프로세스에서 실행한다.

  터미널 A (conda lerobot, ros2_ws 디렉터리):
    source /opt/ros/humble/setup.bash && source install/setup.bash
    export PYTHONPATH="$PWD/install/pipet_inference/lib/python3.10/site-packages:$PYTHONPATH"
    conda activate lerobot
    python -m pipet_inference.zmq_act_server \\
      --bind tcp://127.0.0.1:5560 \\
      --model-path /절대경로/.../checkpoints/last

  터미널 B:
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    ros2 launch pipet_bringup inference.launch.py indy_ip:=192.168.1.10 autonomy_enabled:=true

기본 autonomy_enabled:=false. grip_preset / inference_node 가 Ctrl+C 시 exit code -2 는 SIGINT 로 정상.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    indy_ip_arg = DeclareLaunchArgument(
        "indy_ip",
        default_value="192.168.1.10",
        description="Indy7 robot IP address",
    )
    indy_type_arg = DeclareLaunchArgument("indy_type", default_value="indy7")
    mark7_port_arg = DeclareLaunchArgument("mark7_port", default_value="/dev/ttyACM0")
    use_mock_mark7_arg = DeclareLaunchArgument("use_mock_mark7", default_value="false")

    model_path_arg = DeclareLaunchArgument(
        "model_path",
        default_value="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/pipet_train_outputs/act/checkpoints/last",
        description="checkpoints/last 또는 .../pretrained_model 절대 경로",
    )
    dataset_root_arg = DeclareLaunchArgument(
        "dataset_root",
        default_value="",
        description="LeRobot v3 루트(비우면 체크포인트 train_config.json의 dataset.root 사용)",
    )
    dataset_repo_id_arg = DeclareLaunchArgument("dataset_repo_id", default_value="pipet_dataset")
    task_arg = DeclareLaunchArgument("task", default_value="Pick up the pipette")
    device_arg = DeclareLaunchArgument("device", default_value="cuda")
    model_type_arg = DeclareLaunchArgument("model_type", default_value="lerobot")
    inference_hz_arg = DeclareLaunchArgument("inference_hz", default_value="20.0")
    sync_slop_arg = DeclareLaunchArgument("sync_slop", default_value="0.08")
    dry_run_arg = DeclareLaunchArgument(
        "dry_run",
        default_value="false",
        description="true면 추론만 하고 토픽/서비스 미전송",
    )
    autonomy_enabled_arg = DeclareLaunchArgument(
        "autonomy_enabled",
        default_value="false",
        description="false면 모델은 돌지만 로봇에 명령 안 냄",
    )
    use_zmq_sidecar_arg = DeclareLaunchArgument(
        "use_zmq_sidecar",
        default_value="true",
        description="true면 zmq_act_server(conda)에 추론 위임",
    )
    zmq_endpoint_arg = DeclareLaunchArgument(
        "zmq_endpoint",
        default_value="tcp://127.0.0.1:5560",
        description="inference_node ↔ zmq_act_server",
    )

    indy_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [FindPackageShare("indy_driver"), "launch", "indy_bringup.launch.py"]
                )
            ]
        ),
        launch_arguments={
            "indy_ip": LaunchConfiguration("indy_ip"),
            "indy_type": LaunchConfiguration("indy_type"),
            "launch_rviz": "false",
        }.items(),
    )

    mark7_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [FindPackageShare("pipet_hand_mark7_driver"), "launch", "mark7_hardware.launch.py"]
                )
            ]
        ),
        launch_arguments={
            "port": LaunchConfiguration("mark7_port"),
            "use_mock_hardware": LaunchConfiguration("use_mock_mark7"),
            "use_rviz": "false",
        }.items(),
    )

    wrist_camera_node = Node(
        package="realsense2_camera",
        executable="realsense2_camera_node",
        name="camera",
        namespace="wrist_camera",
        output="screen",
        parameters=[
            {
                "serial_no": "_844212071939",
                "enable_color": True,
                "enable_depth": True,
                "enable_infra1": False,
                "enable_infra2": False,
                "enable_gyro": False,
                "enable_accel": False,
                "align_depth.enable": True,
                "pointcloud.enable": False,
            }
        ],
    )

    overhead_camera_node = Node(
        package="realsense2_camera",
        executable="realsense2_camera_node",
        name="camera",
        namespace="overhead_camera",
        output="screen",
        parameters=[
            {
                "serial_no": "_317222074298",
                "enable_color": True,
                "enable_depth": True,
                "enable_infra1": False,
                "enable_infra2": False,
                "enable_gyro": False,
                "enable_accel": False,
                "align_depth.enable": True,
                "pointcloud.enable": False,
            }
        ],
    )

    grip_preset_node = Node(
        package="pipet_hand_mark7_teleop",
        executable="grip_preset_node",
        name="grip_preset_node",
        output="screen",
        parameters=[
            PathJoinSubstitution(
                [FindPackageShare("pipet_hand_mark7_driver"), "config", "grip_presets.yaml"]
            )
        ],
    )

    inference_node = Node(
        package="pipet_inference",
        executable="inference_node",
        name="inference_node",
        output="screen",
        parameters=[
            {
                "model_path": LaunchConfiguration("model_path"),
                "model_type": LaunchConfiguration("model_type"),
                "dataset_repo_id": LaunchConfiguration("dataset_repo_id"),
                "dataset_root": LaunchConfiguration("dataset_root"),
                "task": LaunchConfiguration("task"),
                "device": LaunchConfiguration("device"),
                "inference_hz": LaunchConfiguration("inference_hz"),
                "sync_slop": LaunchConfiguration("sync_slop"),
                "dry_run": ParameterValue(LaunchConfiguration("dry_run"), value_type=bool),
                "autonomy_enabled": ParameterValue(
                    LaunchConfiguration("autonomy_enabled"), value_type=bool
                ),
                "use_zmq_sidecar": ParameterValue(
                    LaunchConfiguration("use_zmq_sidecar"), value_type=bool
                ),
                "zmq_endpoint": LaunchConfiguration("zmq_endpoint"),
            }
        ],
    )

    return LaunchDescription(
        [
            indy_ip_arg,
            indy_type_arg,
            mark7_port_arg,
            use_mock_mark7_arg,
            model_path_arg,
            dataset_root_arg,
            dataset_repo_id_arg,
            task_arg,
            device_arg,
            model_type_arg,
            inference_hz_arg,
            sync_slop_arg,
            dry_run_arg,
            autonomy_enabled_arg,
            use_zmq_sidecar_arg,
            zmq_endpoint_arg,
            indy_driver_launch,
            mark7_driver_launch,
            grip_preset_node,
            wrist_camera_node,
            overhead_camera_node,
            inference_node,
        ]
    )
