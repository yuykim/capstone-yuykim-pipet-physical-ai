from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'pipet_dagger_collection'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='SirLab',
    maintainer_email='sirlab@todo.todo',
    description='DAgger correction collection for Indy7 + Mark7 pipette manipulation',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dagger_supervisor_node = pipet_dagger_collection.dagger_supervisor_node:main',
        ],
    },
)
