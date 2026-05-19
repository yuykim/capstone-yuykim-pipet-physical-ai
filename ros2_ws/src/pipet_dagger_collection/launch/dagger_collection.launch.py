#!/usr/bin/env python3
"""Launch DAgger correction collection without modifying existing pipelines."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


REPO_ROOT = os.path.expanduser('~/2026capstone2_ws/pipet-physical-ai')


def generate_launch_description():
    model_pose_topic = '/dagger/model_teleop_pose'

    return LaunchDescription(
        [
            DeclareLaunchArgument('indy_ip', default_value='192.168.1.10'),
            DeclareLaunchArgument('mark7_port', default_value='/dev/ttyACM0'),
            DeclareLaunchArgument('use_mock_mark7', default_value='false'),
            DeclareLaunchArgument(
                'model_path',
                default_value=os.path.join(
                    REPO_ROOT,
                    'ai/models/act_remove_grasp_focus_3s2s_cartesian_360_v2/checkpoints/070000',
                ),
            ),
            DeclareLaunchArgument(
                'dataset_root',
                default_value=os.path.join(
                    REPO_ROOT,
                    'ai/datasets/remove_grasp_focus_3s2s_cartesian_360_v2',
                ),
            ),
            DeclareLaunchArgument('dataset_repo_id', default_value='pipet_remove_grasp_focus_3s2s_v2'),
            DeclareLaunchArgument('task', default_value='Remove the pipette from the holder'),
            DeclareLaunchArgument('output_dir', default_value='episodes'),
            DeclareLaunchArgument('dagger_task_name', default_value='remove_dagger'),
            DeclareLaunchArgument('input_backend', default_value='linuxevdev'),
            DeclareLaunchArgument('event_device', default_value=''),
            DeclareLaunchArgument('joystick_device', default_value='/dev/input/js0'),
            DeclareLaunchArgument('joystick_index', default_value='0'),
            DeclareLaunchArgument('linear_step_mm', default_value='1.0'),
            DeclareLaunchArgument('angular_step_deg', default_value='1.0'),
            DeclareLaunchArgument('deadzone', default_value='0.18'),
            DeclareLaunchArgument('max_delta_mm', default_value='1.0'),
            DeclareLaunchArgument('max_delta_deg', default_value='1.0'),
            DeclareLaunchArgument('max_cartesian_speed_mm_s', default_value='8.0'),
            DeclareLaunchArgument('max_angular_speed_deg_s', default_value='8.0'),
            DeclareLaunchArgument('debug_input', default_value='false'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [FindPackageShare('pipet_bringup'), 'launch', 'inference.launch.py']
                        )
                    ]
                ),
                launch_arguments={
                    'indy_ip': LaunchConfiguration('indy_ip'),
                    'mark7_port': LaunchConfiguration('mark7_port'),
                    'use_mock_mark7': LaunchConfiguration('use_mock_mark7'),
                    'model_path': LaunchConfiguration('model_path'),
                    'dataset_repo_id': LaunchConfiguration('dataset_repo_id'),
                    'dataset_root': LaunchConfiguration('dataset_root'),
                    'task': LaunchConfiguration('task'),
                    'control_mode': 'cartesian',
                    'cartesian_pose_topic': model_pose_topic,
                    'image_target_height': '360',
                    'image_target_width': '480',
                    'state_target_dim': '18',
                    'max_delta_mm': LaunchConfiguration('max_delta_mm'),
                    'max_delta_deg': LaunchConfiguration('max_delta_deg'),
                    'max_cartesian_speed_mm_s': LaunchConfiguration('max_cartesian_speed_mm_s'),
                    'max_angular_speed_deg_s': LaunchConfiguration('max_angular_speed_deg_s'),
                    'dry_run': 'false',
                    'autonomy_enabled': 'true',
                    # The supervisor records only human correction commands.
                    # Keeping model gripper disabled prevents wrong autonomous grasp labels.
                    'enable_gripper': 'false',
                }.items(),
            ),
            Node(
                package='pipet_data_collector',
                executable='data_collector_node',
                name='dagger_data_collector',
                output='screen',
                parameters=[
                    {
                        'output_dir': LaunchConfiguration('output_dir'),
                        'task_name': LaunchConfiguration('dagger_task_name'),
                        'sync_slop': 1.0,
                        'camera_setup': 'wrist+overhead_rgb',
                    }
                ],
            ),
            Node(
                package='pipet_dagger_collection',
                executable='dagger_supervisor_node',
                name='dagger_supervisor_node',
                output='screen',
                parameters=[
                    {
                        'model_pose_topic': model_pose_topic,
                        'output_pose_topic': '/indy/teleop_pose',
                        'task_name': LaunchConfiguration('dagger_task_name'),
                        'input_backend': LaunchConfiguration('input_backend'),
                        'event_device': LaunchConfiguration('event_device'),
                        'joystick_device': LaunchConfiguration('joystick_device'),
                        'joystick_index': ParameterValue(
                            LaunchConfiguration('joystick_index'), value_type=int
                        ),
                        'linear_step_mm': ParameterValue(
                            LaunchConfiguration('linear_step_mm'), value_type=float
                        ),
                        'angular_step_deg': ParameterValue(
                            LaunchConfiguration('angular_step_deg'), value_type=float
                        ),
                        'deadzone': ParameterValue(
                            LaunchConfiguration('deadzone'), value_type=float
                        ),
                        'debug_input': ParameterValue(
                            LaunchConfiguration('debug_input'), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
