from setuptools import find_packages, setup
import os
from glob import glob
from pathlib import Path
home_dir = Path.home()
venv_path = Path('/home/ubuntu/my_vision_env/bin/python3')

package_name = 'rallp_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='iheb',
    maintainer_email='iheb@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'person_detection_node = rallp_perception.person_detection_node:main',
            'security_manager_node = rallp_perception.security_manager_node:main',
            'rfid_simulator_node   = rallp_perception.rfid_simulator_node:main',
            'alert_node            = rallp_perception.alert_node:main',
        ],
    },
    options={
        'build_scripts': {
            'executable': str(venv_path),
        },
    },
)
