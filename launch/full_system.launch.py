#!/usr/bin/env python3
"""
Full System Launch File for Medical Waste Management Robot
Launches all nodes: perception, navigation, manipulation, task management, safety
"""

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # Get paths
    pkg_share = FindPackageShare('medical_waste_robot')
    config_dir = PathJoinSubstitution([pkg_share, 'config'])
    launch_dir = PathJoinSubstitution([pkg_share, 'launch'])
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    return LaunchDescription([
        # Declare arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        
        # YOLO Waste Detector Node
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
        ),
        
        # Bin Management System Node
        Node(
            package='medical_waste_robot',
            executable='bin_manager.py',
            name='bin_management_system',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time},
                {'bin_full_threshold': 0.9},
                {'waste_unit_volume': 0.5}
            ]
        ),
        
        # Arm Controller Node
        Node(
            package='medical_waste_robot',
            executable='arm_controller.py',
            name='arm_controller',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time}
            ]
        ),
        
        # Safety Monitor Node
        Node(
            package='medical_waste_robot',
            executable='safety_monitor.py',
            name='safety_monitor',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time},
                {'emergency_stop_enabled': True}
            ]
        ),
        
        # Task Coordinator Node
        Node(
            package='medical_waste_robot',
            executable='task_coordinator.py',
            name='task_coordinator',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time}
            ]
        ),
    ])


if __name__ == '__main__':
    generate_launch_description()
