import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # 1. Dynamically determine the user's home directory
    home_dir = os.path.expanduser('~')
    
    # 2. Construct the absolute paths to the sub-launch files
    # This resolves to /home/username/rallp/sensors/launch/...
    launch_file_lidar2d_0 = os.path.join(home_dir, 'rallp', 'sensors', 'launch', 'lidar2d_0.launch.py')
    launch_file_imu_0 = os.path.join(home_dir, 'rallp', 'sensors', 'launch', 'imu_0.launch.py')
    launch_file_camera_0 = os.path.join(home_dir, 'rallp', 'sensors', 'launch', 'camera_0.launch.py')
    
    # 3. Include the launch files
    launch_lidar2d_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_lidar2d_0]),
    )
    
    launch_imu_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_imu_0]),
    )
    
    launch_camera_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_camera_0]),
    )
    
    # 4. Create and return the LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_lidar2d_0)
    ld.add_action(launch_imu_0)
    ld.add_action(launch_camera_0)
    
    return ld
