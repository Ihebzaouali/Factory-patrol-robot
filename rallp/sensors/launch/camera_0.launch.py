import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    # Get namespace from launch configuration
    namespace = LaunchConfiguration('namespace', default='rallp_0000')
    
    # Camera image bridge (Gazebo -> ROS2)
    camera_image_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_0_image_bridge',
        namespace=namespace,
        output='screen',
        arguments=[
            '/camera_0/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        remappings=[
            ('/camera_0/image_raw', 'camera_0/image_raw'),
        ]
    )
    
    # Camera info bridge (Gazebo -> ROS2)
    camera_info_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_0_info_bridge',
        namespace=namespace,
        output='screen',
        arguments=[
            '/camera_0/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        remappings=[
            ('/camera_0/camera_info', 'camera_0/camera_info'),
        ]
    )
    
    # Static transform publisher for camera optical frame
    camera_static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_0_static_tf',
        namespace=namespace,
        output='screen',
        arguments=[
            '0', '0', '0',  # x, y, z
            '0', '0', '0', '1',  # qx, qy, qz, qw
            'camera_0_link',
            f'{namespace}/robot/chassis_link/camera_0'
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='rallp_0000'),
        camera_image_bridge,
        camera_info_bridge,
        camera_static_tf,
    ])
