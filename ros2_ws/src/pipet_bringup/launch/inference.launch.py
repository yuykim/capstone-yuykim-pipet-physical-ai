#!/usr/bin/env python3
"""
Inference Launch - Autonomous operation with a trained model.

Starts:
  1. Indy7 driver (robot arm)
  2. Mark7 driver (robot hand)
  3. RealSense D435 camera
  4. Inference node (loads trained model)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # -- Arguments --

    indy_ip_arg = DeclareLaunchArgument(
        'indy_ip', default_value='192.168.1.10',
        description='Indy7 robot IP address',
    )
    indy_type_arg = DeclareLaunchArgument(
        'indy_type', default_value='indy7',
    )
    mark7_port_arg = DeclareLaunchArgument(
        'mark7_port', default_value='/dev/ttyACM0',
    )
    use_mock_mark7_arg = DeclareLaunchArgument(
        'use_mock_mark7', default_value='false',
    )
    model_path_arg = DeclareLaunchArgument(
        'model_path', description='Path to trained model file',
    )
    model_type_arg = DeclareLaunchArgument(
        'model_type', default_value='lerobot',
        description='Model type: lerobot / robomimic',
    )
    inference_hz_arg = DeclareLaunchArgument(
        'inference_hz', default_value='15.0',
    )

    # -- 1. Indy7 Driver --

    indy_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('indy_driver'),
                'launch', 'indy_bringup.launch.py',
            ])
        ]),
        launch_arguments={
            'indy_ip': LaunchConfiguration('indy_ip'),
            'indy_type': LaunchConfiguration('indy_type'),
            'launch_rviz': 'false',
        }.items(),
    )

    # -- 2. Mark7 Driver --

    mark7_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('pipet_hand_mark7_driver'),
                'launch', 'mark7_hardware.launch.py',
            ])
        ]),
        launch_arguments={
            'port': LaunchConfiguration('mark7_port'),
            'use_mock_hardware': LaunchConfiguration('use_mock_mark7'),
            'use_rviz': 'false',
        }.items(),
    )

    # -- 3. RealSense D435 Camera --

    realsense_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='camera',
        namespace='camera',
        output='screen',
        parameters=[{
            'enable_color': True,
            'enable_depth': True,
            'enable_infra1': False,
            'enable_infra2': False,
            'align_depth.enable': True,
            'pointcloud.enable': False,
        }],
    )

    # -- 4. Inference Node --

    inference_node = Node(
        package='pipet_inference',
        executable='inference_node',
        name='inference_node',
        output='screen',
        parameters=[{
            'model_path': LaunchConfiguration('model_path'),
            'model_type': LaunchConfiguration('model_type'),
            'inference_hz': LaunchConfiguration('inference_hz'),
        }],
    )

    return LaunchDescription([
        indy_ip_arg,
        indy_type_arg,
        mark7_port_arg,
        use_mock_mark7_arg,
        model_path_arg,
        model_type_arg,
        inference_hz_arg,
        indy_driver_launch,
        mark7_driver_launch,
        realsense_node,
        inference_node,
    ])
