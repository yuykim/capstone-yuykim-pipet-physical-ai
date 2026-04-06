from setuptools import find_packages, setup

package_name = 'pipet_inference'

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
    description='Inference node for trained AI models (stub)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'inference_node = pipet_inference.inference_node:main',
            'zmq_act_server = pipet_inference.zmq_act_server:main',
        ],
    },
)
