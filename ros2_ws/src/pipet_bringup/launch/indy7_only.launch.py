#!/usr/bin/env python3
"""
Indy7 Only Launch - Direct teaching without Mark7 or camera.

Starts Indy7 driver only. Use system_teleop for control:
  ros2 run pipet_system_teleop system_teleop_node
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    indy_ip_arg = DeclareLaunchArgument(
        'indy_ip', default_value='192.168.1.10',
        description='Indy7 robot IP address',
    )
    indy_type_arg = DeclareLaunchArgument(
        'indy_type', default_value='indy7',
    )
    launch_rviz_arg = DeclareLaunchArgument(
        'launch_rviz', default_value='true',
    )
    enable_cartesian_servo_arg = DeclareLaunchArgument(
        'enable_cartesian_servo',
        default_value='false',
        description='Launch indy_moveit MoveIt Servo for Cartesian teleop',
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

    moveit_servo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('indy_moveit'),
                'launch', 'moveit.launch.py',
            ])
        ]),
        condition=IfCondition(LaunchConfiguration('enable_cartesian_servo')),
        launch_arguments={
            'indy_type': LaunchConfiguration('indy_type'),
            'servo_mode': 'true',
            'launch_rviz_moveit': 'false',
        }.items(),
    )

    return LaunchDescription([
        indy_ip_arg,
        indy_type_arg,
        launch_rviz_arg,
        enable_cartesian_servo_arg,
        indy_driver_launch,
        moveit_servo_launch,
    ])
