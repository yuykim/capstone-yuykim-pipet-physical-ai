#!/usr/bin/env python3
"""
Indy7 Only Launch - Direct teaching without Mark7 or camera.

Starts Indy7 driver only. Use the existing indy7_gripper_teleop for control:
  ros2 run indy7_gripper_teleop teaching_control.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    indy_ip_arg = DeclareLaunchArgument(
        'indy_ip', default_value='192.168.1.100',
        description='Indy7 robot IP address',
    )
    indy_type_arg = DeclareLaunchArgument(
        'indy_type', default_value='indy7',
    )
    launch_rviz_arg = DeclareLaunchArgument(
        'launch_rviz', default_value='true',
    )

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
            'launch_rviz': LaunchConfiguration('launch_rviz'),
        }.items(),
    )

    return LaunchDescription([
        indy_ip_arg,
        indy_type_arg,
        launch_rviz_arg,
        indy_driver_launch,
    ])
