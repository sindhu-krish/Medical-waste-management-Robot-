from setuptools import setup, find_packages

setup(
    name='medical_waste_robot',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'ultralytics>=8.0.0',
        'torch>=1.13.0',
        'opencv-python>=4.7.0',
        'numpy>=1.23.0',
    ],
    entry_points={
        'console_scripts': [
            'yolo_detector=perception.yolo_waste_detector:main',
            'bin_manager=bin_management.bin_manager:main',
            'arm_controller=manipulation.arm_controller:main',
        ],
    },
    author='Sindhu Krish',
    description='Medical Waste Management Humanoid Robot using ROS2',
    url='https://github.com/sindhu-krish/Medical-waste-management-Robot-',
)
