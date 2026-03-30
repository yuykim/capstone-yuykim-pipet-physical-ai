from setuptools import find_packages, setup

package_name = 'pipet_system_teleop'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='SirLab',
    maintainer_email='sirlab@todo.todo',
    description='Integrated keyboard teleop for Indy7 + Mark7',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'system_teleop_node = pipet_system_teleop.system_teleop_node:main',
        ],
    },
)
