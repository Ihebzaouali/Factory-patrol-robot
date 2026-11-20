import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Configuration
    # Based on your logs, your namespace is 'rallp_0000'
    namespace = 'rallp_0000'
    setup_path = LaunchConfiguration('setup_path', default=os.path.join(os.path.expanduser('~'), 'rallp'))

    # FIXING THE URDF PATH: 
    # rallp generators usually put the URDF here:
    urdf_file_path = os.path.join(os.path.expanduser('~'), 'rallp', 'robot.urdf')
    
    # If the file isn't there, check '~/rallp/description/robot.urdf'
    if not os.path.exists(urdf_file_path):
        urdf_file_path = os.path.join(os.path.expanduser('~'), 'rallp', 'robot.urdf.xacro')

    with open(urdf_file_path, 'r') as infp:
        robot_desc = infp.read()

    # 2. Nodes
    
    # Robot State Publisher - Provides the URDF to the system
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=namespace,
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True,
            'frame_prefix': f'{namespace}/'
        }]
    )

    # 3. Inclusion of generated services
    # These were created by the 'generator' node previously
    launch_file_platform_service = PathJoinSubstitution([
        setup_path, 'platform/launch', 'platform-service.launch.py'])
    
    launch_file_sensors_service = PathJoinSubstitution([
        setup_path, 'sensors/launch', 'sensors-service.launch.py'])

    spawn_group = GroupAction([
        # Start Platform Service (Controllers/EKF)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_platform_service])
        ),
        
        # Start Sensor Service (Lidar/IMU Bridges)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_sensors_service])
        ),

        # The Spawner Node
        Node(
            package='ros_gz_sim',
            executable='create',
            namespace=namespace,
            arguments=[
                '-name', 'robot',
                '-topic', 'robot_description',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.15',
                '-Y', '0.0'
            ],
            output='screen'
        ),
    ])

    return LaunchDescription([
        node_robot_state_publisher,
        spawn_group
    ])