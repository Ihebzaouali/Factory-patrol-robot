import os

from setuptools import setup


package_name = 'rallp_config'

# Samples
samples = []
for path, dirs, files in os.walk(os.path.join(package_name, 'sample')):
    for file in files:
        samples.append(os.path.join(path, file))

setup(
    name=package_name,
    version='2.7.3',
    packages=[
        package_name,
        package_name + '.common',
        package_name + '.common.types',
        package_name + '.common.utils',
        package_name + '.links',
        package_name + '.links.types',
        package_name + '.manipulators',
        package_name + '.manipulators.types',
        package_name + '.mounts',
        package_name + '.mounts.types',
        package_name + '.platform',
        package_name + '.platform.attachments',
        package_name + '.platform.types',
        package_name + '.sensors',
        package_name + '.sensors.types',
        package_name + '.system',
    ],
    data_files=[
        # Install marker file in the package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Include the package.xml file
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'sample'), samples),
    ],
    install_requires=[
        'setuptools',
        'requests',
        "importlib-metadata; python_version == '3.8'",
    ],
    zip_safe=True,
    maintainer='Mohamed Ali Zouari',
    maintainer_email='mohamedalizouari.ai@mail.ru',
    description='Rallp Configuration YAML Parser and Writer',
    license='BSD-3',
    extras_require={
        'test': [
            'pytest',
        ],
    },
)
