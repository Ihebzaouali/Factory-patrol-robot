import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, GroupAction, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('world', default_value='warehouse',
                          description='Gazebo World'),
    DeclareLaunchArgument('auto_start', default_value='true',
                          choices=['true', 'false'],
                          description='Auto-start Gazebo simulation'),
    DeclareLaunchArgument('namespace', default_value='rallp_0000',
                          description='Robot namespace'),
    DeclareLaunchArgument('setup_path', 
                          default_value=os.path.join(os.path.expanduser('~'), 'rallp'),
                          description='Path to rallp setup directory'),
    DeclareLaunchArgument('spawn_x', default_value='0.0',
                          description='Robot spawn X position'),
    DeclareLaunchArgument('spawn_y', default_value='0.0',
                          description='Robot spawn Y position'),
    DeclareLaunchArgument('spawn_z', default_value='0.15',
                          description='Robot spawn Z position'),
    DeclareLaunchArgument('spawn_yaw', default_value='0.0',
                          description='Robot spawn yaw orientation'),
    DeclareLaunchArgument('spawn_delay', default_value='5.0',
                          description='Delay in seconds before spawning robot'),
]

def gz_launch(context, *args, **kwargs):
    # Directories
    pkg_rallp_gz = get_package_share_directory('rallp_gz')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # Paths
    gz_sim_launch = PathJoinSubstitution(
        [pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])
    gui_config = PathJoinSubstitution(
        [pkg_rallp_gz, 'config', 'gui.config'])
    
    auto_start_option = ''
    auto_start = LaunchConfiguration('auto_start').perform(context)
    if (auto_start == 'true'):
        auto_start_option = ' -r'
    
    # Gazebo Simulator
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_sim_launch]),
        launch_arguments=[
            ('gz_args', [LaunchConfiguration('world'),
                         '.sdf',
                         auto_start_option,
                         ' -v 4',
                         ' --gui-config ',
                         gui_config])
        ]
    )
    
    return [gz_sim]

def spawn_robot(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    setup_path = LaunchConfiguration('setup_path').perform(context)
    
    # URDF path resolution
    urdf_file_path = os.path.join(setup_path, 'robot.urdf')
    
    if not os.path.exists(urdf_file_path):
        urdf_file_path = os.path.join(setup_path, 'robot.urdf.xacro')
    
    if not os.path.exists(urdf_file_path):
        raise FileNotFoundError(f"URDF file not found at {urdf_file_path}")
    
    with open(urdf_file_path, 'r') as infp:
        robot_desc = infp.read()
    
    # Robot State Publisher
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
    
    # Launch files for platform and sensors
    launch_file_platform_service = PathJoinSubstitution([
        setup_path, 'platform/launch', 'platform-service.launch.py'])
    
    launch_file_sensors_service = PathJoinSubstitution([
        setup_path, 'sensors/launch', 'sensors-service.launch.py'])
    
    # Spawn group with all robot-related nodes
    spawn_group = GroupAction([
        # Platform Service (Controllers/EKF)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_platform_service])
        ),
        
        # Sensor Service (Lidar/IMU Bridges)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file_sensors_service])
        ),
        
        # Spawner Node
        Node(
            package='ros_gz_sim',
            executable='create',
            namespace=namespace,
            arguments=[
                '-name', 'robot',
                '-topic', 'robot_description',
                '-x', LaunchConfiguration('spawn_x'),
                '-y', LaunchConfiguration('spawn_y'),
                '-z', LaunchConfiguration('spawn_z'),
                '-Y', LaunchConfiguration('spawn_yaw')
            ],
            output='screen'
        ),
    ])
    
    # Add delay before spawning robot (gives Gazebo time to fully start)
    spawn_delay = float(LaunchConfiguration('spawn_delay').perform(context))
    
    return [
        node_robot_state_publisher,
        TimerAction(
            period=spawn_delay,
            actions=[spawn_group]
        )
    ]

def generate_launch_description():
    # Directories
    pkg_rallp_gz = get_package_share_directory('rallp_gz')
    
    # Determine all ros packages that are sourced
    packages_paths = [os.path.join(p, 'share') for p in os.getenv('AMENT_PREFIX_PATH').split(':')]
    
    # Set Gazebo resource path
    gz_sim_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            os.path.join(pkg_rallp_gz, 'worlds') + ':',
            os.path.join(pkg_rallp_gz, 'meshes') + ':',
            ':' + ':'.join(packages_paths)])
    
    # Clock bridge
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ]
    )
    
    # Create launch description
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gz_sim_resource_path)
    ld.add_action(OpaqueFunction(function=gz_launch))
    ld.add_action(clock_bridge)
    ld.add_action(OpaqueFunction(function=spawn_robot))
    
    return ld
