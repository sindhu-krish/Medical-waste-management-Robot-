from setuptools import setup

package_name = 'medical_waste_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[
        'perception',
        'bin_management',
        'manipulation',
        'task_manager',
        'safety'
    ],
    package_dir={
        '': 'src'
    },
    py_modules=[
        'perception.yolo_waste_detector',
        'bin_management.bin_manager',
        'manipulation.arm_controller',
        'task_manager.task_coordinator',
        'safety.safety_monitor'
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'ultralytics>=8.0.0',
        'torch>=1.13.0',
        'opencv-python>=4.7.0',
        'numpy>=1.23.0',
        'pyyaml>=6.0',
        'matplotlib>=3.7.0',
        'pandas>=1.5.0',
    ],
    entry_points={
        'console_scripts': [
            'yolo_detector=perception.yolo_waste_detector:main',
            'bin_manager=bin_management.bin_manager:main',
            'arm_controller=manipulation.arm_controller:main',
            'task_coordinator=task_manager.task_coordinator:main',
            'safety_monitor=safety.safety_monitor:main',
        ],
    },
    author='Sindhu Krish',
    author_email='sindhukrish1604@gmail.com',
    maintainer='Sindhu Krish',
    maintainer_email='sindhukrish1604@gmail.com',
    url='https://github.com/sindhu-krish/Medical-waste-management-Robot-',
    description='Autonomous Medical Waste Management Robot using ROS2 and YOLO',
    long_description='A complete ROS2-based system for autonomous medical waste detection, classification, and management using deep learning.',
    license='MIT',
    python_requires='>=3.10',
)
