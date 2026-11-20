#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # Launch Configurations
    enable_ekf = LaunchConfiguration('enable_ekf')
    setup_path = LaunchConfiguration('setup_path')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Launch Arguments
    arg_enable_ekf = DeclareLaunchArgument(
        'enable_ekf',
        default_value='true',
        choices=['true', 'false'],
        description='Enable localization via EKF node'
    )
    arg_setup_path = DeclareLaunchArgument(
        'setup_path',
        default_value='/etc/rallp/'
    )
    arg_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        choices=['true', 'false'],
        default_value='false',
        description='Use simulation time'
    )

    # Paths
    dir_platform_config = PathJoinSubstitution([
        setup_path, 'platform/config'])

    # Configs
    config_localization = [
        dir_platform_config,
        '/localization.yaml'
    ]

    # Localization
    node_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[config_localization],
        remappings=[
            ('odometry/filtered', 'platform/odom/filtered'),
            ('/diagnostics', 'diagnostics'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
        ],
        condition=IfCondition(enable_ekf),
    )

    ld = LaunchDescription()
    ld.add_action(arg_enable_ekf)
    ld.add_action(arg_setup_path)
    ld.add_action(arg_use_sim_time)
    ld.add_action(node_localization)
    return ld
