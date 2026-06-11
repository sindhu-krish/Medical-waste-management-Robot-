#!/usr/bin/env python3
"""
Manipulation System Launch File
Launches arm and gripper controllers
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
        
        # Arm Controller Node
        Node(
            package='medical_waste_robot',
            executable='arm_controller.py',
            name='arm_controller',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time},
                {'arm_name': 'tiago_arm'},
                {'gripper_name': 'tiago_gripper'}
            ]
        ),
        
        # Gripper Controller Node
        Node(
            package='medical_waste_robot',
            executable='gripper_controller.py',
            name='gripper_controller',
            output='screen',
            parameters=[
                PathJoinSubstitution([config_dir, 'robot_params.yaml']),
                {'use_sim_time': use_sim_time}
            ]
        )
    ])


if __name__ == '__main__':
    generate_launch_description()
