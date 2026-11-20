import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Dynamically determine the home directory and config path
    home_dir = os.path.expanduser('~')
    # This creates: /home/<user>/rallp/sensors/config/imu_0.yaml
    imu_config_path = os.path.join(home_dir, 'rallp', 'sensors', 'config', 'imu_0.yaml')

    launch_arg_prefix = DeclareLaunchArgument(
        'prefix',
        default_value='',
        description='')

    prefix = LaunchConfiguration('prefix')

    # Nodes
    node_imu_0_gz_bridge = Node(
        name='imu_0_gz_bridge',
        executable='parameter_bridge',
        package='ros_gz_bridge',
        namespace='rallp_0000/sensors/',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                # Using the dynamic path here
                'config_file': imu_config_path,
            }
        ],
    )

    node_imu_0_static_tf = Node(
        name='imu_0_static_tf',
        executable='static_transform_publisher',
        package='tf2_ros',
        namespace='rallp_0000',
        output='screen',
        arguments=[
            '--frame-id', 'imu_0_link',
            '--child-frame-id', 'rallp_0000/robot/base_link/imu_0',
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
        ],
        parameters=[{'use_sim_time': True}],
    )

    # Create LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_arg_prefix)
    ld.add_action(node_imu_0_gz_bridge)
    ld.add_action(node_imu_0_static_tf)
    return ld