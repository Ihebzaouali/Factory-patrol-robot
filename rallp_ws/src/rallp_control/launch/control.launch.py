#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from rallp_config.common.utils.dictionary import unflatten_dict
from rallp_config.common.utils.yaml import read_yaml

REMAPPINGS = [
    ('joint_states', 'platform/joint_states'),
    ('dynamic_joint_states', 'platform/dynamic_joint_states'),
    ('platform_velocity_controller/odom', 'platform/odom'),
    ('platform_velocity_controller/odometry', 'platform/odom'),
    ('platform_velocity_controller/cmd_vel', 'platform/cmd_vel'),
    ('platform_velocity_controller/cmd_vel_out', 'platform/cmd_vel_out'),
    ('platform_velocity_controller/reference', 'platform/cmd_vel'),
    ('platform_velocity_controller/transition_event', 'platform/transition_event'),
    ('/diagnostics', 'diagnostics'),
    ('/tf', 'tf'),
    ('/tf_static', 'tf_static'),
    ('~/robot_description', 'robot_description'),
]


def launch_setup(context, *args, **kwargs):
    setup_path = LaunchConfiguration('setup_path')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Controllers
    config_control = PathJoinSubstitution([
        setup_path, 'platform/config/control.yaml'])

    context_control = unflatten_dict(read_yaml(config_control.perform(context)))

    controllers = []

    # Add Controller Manager
    controllers.append(Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[config_control],
        output={
            'stdout': 'screen',
            'stderr': 'screen',
        },
        remappings=REMAPPINGS,
        condition=UnlessCondition(use_sim_time)
    ))
    # Add Joint State Broadcaster
    controllers.append(Node(
        package='controller_manager',
        executable='spawner',
        arguments=['--controller-manager-timeout', '60', 'joint_state_broadcaster'],
        output='screen',
        additional_env={'ROS_SUPER_CLIENT': 'True'},
    ))
    # Add Platform Velocity Controller
    controllers.append(Node(
        package='controller_manager',
        executable='spawner',
        arguments=['--controller-manager-timeout', '60', 'platform_velocity_controller'],
        output='screen',
        additional_env={'ROS_SUPER_CLIENT': 'True'},
    ))
    # If Simulation, Add All Listed Controllers
    for namespace in context_control:
        for controller in context_control[namespace]:
            if ('controller' not in controller or
                    'manager' in controller or
                    'platform' in controller):
                continue
            controllers.append(Node(
                name=controller,
                package='controller_manager',
                executable='spawner',
                arguments=['--controller-manager-timeout', '60', controller],
                output='screen',
                additional_env={'ROS_SUPER_CLIENT': 'True'},
                condition=IfCondition(use_sim_time),
            ))
    return [GroupAction(controllers)]


def generate_launch_description():
    # Launch Configurations
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

    ld = LaunchDescription([
        arg_setup_path,
        arg_use_sim_time
    ])
    ld.add_action(OpaqueFunction(function=launch_setup))
    return ld
