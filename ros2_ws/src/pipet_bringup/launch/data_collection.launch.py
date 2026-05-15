#!/usr/bin/env python3
"""
Data Collection Launch - Full system for collecting demonstration data.

Starts:
  1. Indy7 driver (robot arm)
  2. Mark7 driver (robot hand)
  3. RealSense D435 cameras (wrist + overhead)
  4. Data collector node (synchronized recording)

After launch, run the master teleop node in a separate terminal:
  ros2 run pipet_system_teleop system_teleop_node

For keyboard servo (movetelel) input, run in another TTY terminal:
  ros2 run pipet_system_teleop keyboard_servo_node
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # -- Arguments --

    indy_ip_arg = DeclareLaunchArgument(
        'indy_ip',
        default_value='192.168.1.10',
        description='Indy7 robot IP address',
    )
    indy_type_arg = DeclareLaunchArgument(
        'indy_type', default_value='indy7',
        description='Indy robot type',
    )
    mark7_port_arg = DeclareLaunchArgument(
        'mark7_port', default_value='/dev/ttyACM0',
        description='Mark7 RF dongle serial port',
    )
    use_mock_mark7_arg = DeclareLaunchArgument(
        'use_mock_mark7', default_value='false',
        description='Use mock Mark7 hardware',
    )
    output_dir_arg = DeclareLaunchArgument(
        'output_dir', default_value='episodes',
        description='NPZ output directory',
    )
    camera_fps_arg = DeclareLaunchArgument(
        'camera_fps', default_value='15',
        description='RealSense camera FPS',
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

    # -- 3. RealSense D435 Cameras --

    # Wrist camera (mounted on robot arm endpoint)
    wrist_camera_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='camera',
        namespace='wrist_camera',
        output='screen',
        parameters=[{
            'serial_no': '_844212071939',
            'enable_color': True,
            'enable_depth': False,
            'enable_infra1': False,
            'enable_infra2': False,
            'enable_gyro': False,
            'enable_accel': False,
            'align_depth.enable': False,
            'pointcloud.enable': False,
        }],
    )

    # Overhead camera (top-down view of workspace)
    overhead_camera_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='camera',
        namespace='overhead_camera',
        output='screen',
        parameters=[{
            'serial_no': '_317222074298',
            'enable_color': True,
            'enable_depth': False,
            'enable_infra1': False,
            'enable_infra2': False,
            'enable_gyro': False,
            'enable_accel': False,
            'align_depth.enable': False,
            'pointcloud.enable': False,
        }],
    )

    # -- 4. Grip Preset Node (provides /gripper/grasp, open, press services) --

    grip_preset_node = Node(
        package='pipet_hand_mark7_teleop',
        executable='grip_preset_node',
        name='grip_preset_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([
                FindPackageShare('pipet_hand_mark7_driver'),
                'config', 'grip_presets.yaml',
            ])
        ],
    )

    # -- 5. Data Collector --

    data_collector_node = Node(
        package='pipet_data_collector',
        executable='data_collector_node',
        name='data_collector_node',
        output='screen',
        parameters=[{
            'output_dir': LaunchConfiguration('output_dir'),
            'sync_slop': 1.0,
        }],
    )

    return LaunchDescription([
        indy_ip_arg,
        indy_type_arg,
        mark7_port_arg,
        use_mock_mark7_arg,
        output_dir_arg,
        camera_fps_arg,
        indy_driver_launch,
        mark7_driver_launch,
        grip_preset_node,
        wrist_camera_node,
        overhead_camera_node,
        data_collector_node,
    ])
