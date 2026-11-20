from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    # Launch Configurations
    setup_path = LaunchConfiguration('setup_path')
    use_sim_time = LaunchConfiguration('use_sim_time')

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
    config_teleop_joy = [
        dir_platform_config,
        '/teleop_joy.yaml'
    ]


    node_joy = Node(
        package='joy_linux',
        executable='joy_linux_node',
        output='screen',
        name='joy_node',
        parameters=[
            config_teleop_joy,
            {'use_sim_time': use_sim_time},
        ],
        remappings=[
            ('/diagnostics', 'diagnostics'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('joy', 'joy_teleop/joy'),
            ('joy/set_feedback', 'joy_teleop/joy/set_feedback'),
        ],
        respawn=True,
    )

    node_teleop_twist_joy = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        output='screen',
        name='teleop_twist_joy_node',
        parameters=[
            config_teleop_joy,
            {'use_sim_time': use_sim_time},
            {'publish_stamped_twist': True},
        ],
        remappings=[
            ('joy', 'joy_teleop/joy'),
            ('cmd_vel', 'joy_teleop/cmd_vel'),
        ]
    )

    #node_twist_mux = Node(
    #    package='twist_mux',
    #    executable='twist_mux',
    #    output='screen',
    #    name='teleop_cutoff_mux',
    #    remappings={
    #        ('cmd_vel_out', 'joy_teleop/cmd_vel'),
    #        ('/diagnostics', 'diagnostics'),
    #        ('/tf', 'tf'),
    #        ('/tf_static', 'tf_static'),
    #    },
    #    parameters=[
    #        {'use_sim_time': use_sim_time},
    #        {'use_stamped': True},
    #        {'topics.joy.topic': 'joy_teleop/_cmd_vel'},
    #        {'topics.joy.timeout': 0.5},
    #        {'topics.joy.priority': 10},
    #        {'locks.bt_quality.topic': 'joy_teleop/bt_quality_stop'},
    #        {'locks.bt_quality.timeout': 1.0},
    #        {'locks.bt_quality.priority': 255},
    #    ]
    #)


    # Create launch description and add actions
    ld = LaunchDescription()
    ld.add_action(arg_setup_path)
    ld.add_action(arg_use_sim_time)
    #ld.add_action(node_bt_cutoff)
    ld.add_action(node_joy)
    ld.add_action(node_teleop_twist_joy)
    #ld.add_action(node_twist_mux)
    return ld
