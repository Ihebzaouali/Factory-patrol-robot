#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # Launch Configurations
    setup_path = LaunchConfiguration('setup_path')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Launch Arguments
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
    config_twist_mux = [
        dir_platform_config,
        '/twist_mux.yaml'
    ]

    config_interactive_markers = [
        dir_platform_config,
        '/teleop_interactive_markers.yaml'
    ]

    node_interactive_marker_twist_server = Node(
        package='interactive_marker_twist_server',
        executable='marker_server',
        name='twist_server_node',
        remappings=[('cmd_vel', 'twist_marker_server/cmd_vel'),
                    ('twist_server/feedback', 'twist_marker_server/feedback'),
                    ('twist_server/update', 'twist_marker_server/update')],
        parameters=[
            config_interactive_markers,
            {'use_sim_time': use_sim_time},
            {'use_stamped_msgs': True},
        ],
        output='screen',
    )

    node_twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        remappings={
            ('cmd_vel_out', 'platform/cmd_vel'),
            ('/diagnostics', 'diagnostics'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
        },
        parameters=[
            config_twist_mux,
            {'use_sim_time': use_sim_time},
            {'use_stamped': True},
        ]
    )

    ld = LaunchDescription()
    ld.add_action(arg_setup_path)
    ld.add_action(arg_use_sim_time)
    ld.add_action(node_interactive_marker_twist_server)
    ld.add_action(node_twist_mux)
    return ld
