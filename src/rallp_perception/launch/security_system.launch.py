from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        DeclareLaunchArgument('namespace',       default_value='rallp_0000'),
        DeclareLaunchArgument('gmail_sender',    default_value='your_robot@gmail.com'),
        DeclareLaunchArgument('gmail_password',  default_value='your_app_password'),
        DeclareLaunchArgument('gmail_recipient', default_value='security_team@gmail.com'),
        DeclareLaunchArgument('location',        default_value='Warehouse Zone A'),
        DeclareLaunchArgument('lidar_topic',     default_value='/rallp_0000/sensors/lidar2d_0/scan'),

        # ── Security Manager ────────────────────────────────────────────
        Node(
            package='rallp_perception',
            executable='security_manager_node',
            name='security_manager_node',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            parameters=[{
                'namespace':            LaunchConfiguration('namespace'),
                'lidar_topic':          LaunchConfiguration('lidar_topic'),
                'safe_stop_distance':   1.2,
                'detection_confidence': 0.5,
                'rfid_timeout':         30.0,
                'approach_speed':       0.3,
                'detection_cooldown':   5.0,
                'approach_timeout':     15.0,
            }]
        ),

        # ── RFID Simulator ──────────────────────────────────────────────
        Node(
            package='rallp_perception',
            executable='rfid_simulator_node',
            name='rfid_simulator_node',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            prefix='xterm -e',
            parameters=[{
                'namespace': LaunchConfiguration('namespace'),
            }]
        ),

        # ── Alert Node ──────────────────────────────────────────────────
        Node(
            package='rallp_perception',
            executable='alert_node',
            name='alert_node',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            parameters=[{
                'namespace':       LaunchConfiguration('namespace'),
                'gmail_sender':    LaunchConfiguration('gmail_sender'),
                'gmail_password':  LaunchConfiguration('gmail_password'),
                'gmail_recipient': LaunchConfiguration('gmail_recipient'),
                'robot_name':      'RALLP Security Robot',
                'location':        LaunchConfiguration('location'),
                'alarm_duration':  5.0,
                'alarm_frequency': 880.0,
            }]
        ),
    ])
