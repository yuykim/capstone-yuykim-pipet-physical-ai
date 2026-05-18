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

  control_mode:=joint 는 JointTrajectory + MSG_TELE_JOINT_ABS(data=6)를 사용한다.
  control_mode:=cartesian 은 /indy/teleop_pose + MSG_TELE_TASK_RLT(data=5)를 사용한다.
  inference_node가 indy_prep_joint_teleop:=true(기본)일 때 자동으로 indy_srv를 호출한다.

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
        default_value="/home/sirlab-pwd-0000/2026capstone2_ws/pipet-physical-ai/ai/models/act/checkpoints/last",
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
    control_mode_arg = DeclareLaunchArgument(
        "control_mode",
        default_value="joint",
        description="joint=action[:6]을 관절 delta(rad), cartesian=action[:6]을 delta EE pose(mm/deg)로 해석",
    )
    cartesian_pose_topic_arg = DeclareLaunchArgument(
        "cartesian_pose_topic",
        default_value="/indy/teleop_pose",
        description="control_mode:=cartesian 일 때 누적 relative task pose를 발행할 토픽",
    )
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
    indy_prep_joint_teleop_arg = DeclareLaunchArgument(
        "indy_prep_joint_teleop",
        default_value="true",
        description="true면 control_mode에 맞춰 indy_srv 텔레옵 모드로 자동 전환",
    )
    indy_prep_joint_teleop_code_arg = DeclareLaunchArgument(
        "indy_prep_joint_teleop_code",
        default_value="6",
        description="indy_define.MSG_TELE_JOINT_ABS (드라이버 포크면 indy_define.py 확인)",
    )
    indy_prep_task_teleop_code_arg = DeclareLaunchArgument(
        "indy_prep_task_teleop_code",
        default_value="5",
        description="indy_define.MSG_TELE_TASK_RLT. cartesian action 추론에서 /indy/teleop_pose를 쓰기 위한 모드.",
    )
    action_delta_scale_arg = DeclareLaunchArgument(
        "action_delta_scale",
        default_value="1.0",
        description="모델 action[:6]에 곱함. joint는 rad, cartesian은 mm/deg 출력에 적용.",
    )
    grasp_delay_steps_arg = DeclareLaunchArgument(
        "grasp_delay_steps",
        default_value="0",
        description="첫 grasp 예측 후 이 tick 수만큼 그리퍼를 늦게 닫음. 20Hz에서 10~20은 0.5~1.0초.",
    )
    pre_grasp_delta_scale_arg = DeclareLaunchArgument(
        "pre_grasp_delta_scale",
        default_value="1.0",
        description="grasp delay 중에만 모델 action[:6]에 추가 배율 적용. 전체 action_delta_scale보다 보수적인 late-grasp 보정.",
    )
    grasp_confirm_steps_arg = DeclareLaunchArgument(
        "grasp_confirm_steps",
        default_value="0",
        description="grasp 예측이 이 tick 수만큼 연속 유지되어야 닫음. 0이면 delta 조건만 사용.",
    )
    grasp_max_delta_norm_arg = DeclareLaunchArgument(
        "grasp_max_delta_norm",
        default_value="0.0",
        description="grasp 실행 허용 최대 delta norm. joint는 rad, cartesian은 mm/deg 혼합 norm. 0이면 비활성.",
    )
    grasp_min_elapsed_steps_arg = DeclareLaunchArgument(
        "grasp_min_elapsed_steps",
        default_value="0",
        description="시작 후 이 tick 수 전에는 grasp를 보류. 20Hz에서 40은 2초.",
    )
    grasp_min_motion_rad_arg = DeclareLaunchArgument(
        "grasp_min_motion_rad",
        default_value="0.0",
        description="시작 관절 위치 대비 이만큼 움직이기 전에는 grasp를 보류. 0이면 비활성.",
    )
    enable_gripper_arg = DeclareLaunchArgument(
        "enable_gripper",
        default_value="true",
        description="false면 모델이 grasp/open 등을 내도 그리퍼 서비스 호출을 차단.",
    )
    max_joint_speed_arg = DeclareLaunchArgument(
        "max_joint_speed_rad_s",
        default_value="0.0",
        description="관절 속도 상한(rad/s). 0이면 비활성. 활성 시 tick당 delta를 speed*dt로 추가 제한.",
    )
    max_delta_mm_arg = DeclareLaunchArgument(
        "max_delta_mm",
        default_value="2.0",
        description="cartesian 모드 tick당 translation delta 클립(mm).",
    )
    max_delta_deg_arg = DeclareLaunchArgument(
        "max_delta_deg",
        default_value="2.0",
        description="cartesian 모드 tick당 rotation delta 클립(deg).",
    )
    max_cartesian_speed_arg = DeclareLaunchArgument(
        "max_cartesian_speed_mm_s",
        default_value="0.0",
        description="cartesian translation 속도 상한(mm/s). 0이면 비활성.",
    )
    max_angular_speed_arg = DeclareLaunchArgument(
        "max_angular_speed_deg_s",
        default_value="0.0",
        description="cartesian rotation 속도 상한(deg/s). 0이면 비활성.",
    )
    image_target_height_arg = DeclareLaunchArgument(
        "image_target_height",
        default_value="0",
        description="0이면 리사이즈 안 함. act_360_idle 등 360 학습이면 360",
    )
    image_target_width_arg = DeclareLaunchArgument(
        "image_target_width",
        default_value="0",
        description="0이면 리사이즈 안 함. 360 학습이면 480",
    )
    state_target_dim_arg = DeclareLaunchArgument(
        "state_target_dim",
        default_value="0",
        description="observation.state 차원 강제(0=기본 18). extended 모델(26) 추론 시 26 권장.",
    )
    ee_pose_topic_arg = DeclareLaunchArgument(
        "ee_pose_topic",
        default_value="/indy/ee_pose",
        description="cartesian state의 ee_pose 6D를 받을 Indy native pose 토픽.",
    )
    use_tf_ee_pose_arg = DeclareLaunchArgument(
        "use_tf_ee_pose",
        default_value="true",
        description="state 26D일 때 ee_pose(7)를 TF로 채움. false면 fk_urdf_path Pinocchio만.",
    )
    ee_tf_parent_frame_arg = DeclareLaunchArgument(
        "ee_tf_parent_frame",
        default_value="world",
        description="TCP pose TF parent (lookup: parent <- child).",
    )
    ee_tf_child_frame_arg = DeclareLaunchArgument(
        "ee_tf_child_frame",
        default_value="tcp",
        description="TCP link frame id (Neuromeka robot_state_publisher 기본 tcp).",
    )
    fk_urdf_path_arg = DeclareLaunchArgument(
        "fk_urdf_path",
        default_value="",
        description="Indy7 URDF 절대경로: TF 실패 시 Pinocchio FK fallback (변환 시 --fk_urdf와 동일 파일 권장).",
    )
    fk_tcp_frame_arg = DeclareLaunchArgument("fk_tcp_frame", default_value="tcp")
    fk_joint_names_arg = DeclareLaunchArgument(
        "fk_joint_names",
        default_value="joint0,joint1,joint2,joint3,joint4,joint5",
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
                "control_mode": LaunchConfiguration("control_mode"),
                "cartesian_pose_topic": LaunchConfiguration("cartesian_pose_topic"),
                "dry_run": ParameterValue(LaunchConfiguration("dry_run"), value_type=bool),
                "autonomy_enabled": ParameterValue(
                    LaunchConfiguration("autonomy_enabled"), value_type=bool
                ),
                "use_zmq_sidecar": ParameterValue(
                    LaunchConfiguration("use_zmq_sidecar"), value_type=bool
                ),
                "zmq_endpoint": LaunchConfiguration("zmq_endpoint"),
                "indy_prep_joint_teleop": ParameterValue(
                    LaunchConfiguration("indy_prep_joint_teleop"), value_type=bool
                ),
                "indy_prep_joint_teleop_code": ParameterValue(
                    LaunchConfiguration("indy_prep_joint_teleop_code"), value_type=int
                ),
                "indy_prep_task_teleop_code": ParameterValue(
                    LaunchConfiguration("indy_prep_task_teleop_code"), value_type=int
                ),
                "action_delta_scale": LaunchConfiguration("action_delta_scale"),
                "grasp_delay_steps": ParameterValue(
                    LaunchConfiguration("grasp_delay_steps"), value_type=int
                ),
                "pre_grasp_delta_scale": LaunchConfiguration("pre_grasp_delta_scale"),
                "grasp_confirm_steps": ParameterValue(
                    LaunchConfiguration("grasp_confirm_steps"), value_type=int
                ),
                "grasp_max_delta_norm": LaunchConfiguration("grasp_max_delta_norm"),
                "grasp_min_elapsed_steps": ParameterValue(
                    LaunchConfiguration("grasp_min_elapsed_steps"), value_type=int
                ),
                "grasp_min_motion_rad": LaunchConfiguration("grasp_min_motion_rad"),
                "enable_gripper": ParameterValue(
                    LaunchConfiguration("enable_gripper"), value_type=bool
                ),
                "max_joint_speed_rad_s": LaunchConfiguration("max_joint_speed_rad_s"),
                "max_delta_mm": LaunchConfiguration("max_delta_mm"),
                "max_delta_deg": LaunchConfiguration("max_delta_deg"),
                "max_cartesian_speed_mm_s": LaunchConfiguration("max_cartesian_speed_mm_s"),
                "max_angular_speed_deg_s": LaunchConfiguration("max_angular_speed_deg_s"),
                "image_target_height": ParameterValue(
                    LaunchConfiguration("image_target_height"), value_type=int
                ),
                "image_target_width": ParameterValue(
                    LaunchConfiguration("image_target_width"), value_type=int
                ),
                "state_target_dim": ParameterValue(
                    LaunchConfiguration("state_target_dim"), value_type=int
                ),
                "ee_pose_topic": LaunchConfiguration("ee_pose_topic"),
                "use_tf_ee_pose": ParameterValue(LaunchConfiguration("use_tf_ee_pose"), value_type=bool),
                "ee_tf_parent_frame": LaunchConfiguration("ee_tf_parent_frame"),
                "ee_tf_child_frame": LaunchConfiguration("ee_tf_child_frame"),
                "fk_urdf_path": LaunchConfiguration("fk_urdf_path"),
                "fk_tcp_frame": LaunchConfiguration("fk_tcp_frame"),
                "fk_joint_names": LaunchConfiguration("fk_joint_names"),
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
            control_mode_arg,
            cartesian_pose_topic_arg,
            dry_run_arg,
            autonomy_enabled_arg,
            use_zmq_sidecar_arg,
            zmq_endpoint_arg,
            indy_prep_joint_teleop_arg,
            indy_prep_joint_teleop_code_arg,
            indy_prep_task_teleop_code_arg,
            action_delta_scale_arg,
            grasp_delay_steps_arg,
            pre_grasp_delta_scale_arg,
            grasp_confirm_steps_arg,
            grasp_max_delta_norm_arg,
            grasp_min_elapsed_steps_arg,
            grasp_min_motion_rad_arg,
            enable_gripper_arg,
            max_joint_speed_arg,
            max_delta_mm_arg,
            max_delta_deg_arg,
            max_cartesian_speed_arg,
            max_angular_speed_arg,
            image_target_height_arg,
            image_target_width_arg,
            state_target_dim_arg,
            ee_pose_topic_arg,
            use_tf_ee_pose_arg,
            ee_tf_parent_frame_arg,
            ee_tf_child_frame_arg,
            fk_urdf_path_arg,
            fk_tcp_frame_arg,
            fk_joint_names_arg,
            indy_driver_launch,
            mark7_driver_launch,
            grip_preset_node,
            wrist_camera_node,
            overhead_camera_node,
            inference_node,
        ]
    )
