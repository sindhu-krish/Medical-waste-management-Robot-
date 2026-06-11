#!/usr/bin/env python3
"""
Perception System Launch File
Launches camera driver and YOLO waste detector
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    pkg_share = FindPackageShare('medical_waste_robot')
    config_dir = PathJoinSubstitution([pkg_share, 'config'])
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        
        # Camera Driver Node
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            output='screen',
            parameters=[{
                'enable_depth': True,
                'enable_color': True,
                'enable_infra1': False,
                'enable_infra2': False,
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '1280x960x30'
            }]
        ),
        
        # YOLO Waste Detector
        Node(
            package='medical_waste_robot',
            executable='yolo_waste_detector.py',
            name='yolo_waste_detector',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time},
                {'model_path': 'models/waste_detector.pt'},
                {'confidence_threshold': 0.5}
            ]
        )
    ])


if __name__ == '__main__':
    generate_launch_description()
