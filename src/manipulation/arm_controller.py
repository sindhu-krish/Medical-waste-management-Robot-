#!/usr/bin/env python3
"""
Robotic Arm Control Node for Waste Placement
Controls the robotic arm to pick waste and place it in the correct bin
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, Point, Quaternion
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
import json
import math
from enum import Enum

class RobotState(Enum):
    IDLE = 0
    PICKING = 1
    TRANSPORTING = 2
    PLACING = 3
    RETURNING = 4

class ArmController(Node):
    """
    ROS2 Node for controlling robotic arm to place waste in correct bins
    """
    
    def __init__(self):
        super().__init__('arm_controller')
        
        # Declare parameters
        self.declare_parameter('arm_name', 'tiago_arm')
        self.declare_parameter('gripper_name', 'tiago_gripper')
        self.declare_parameter('max_velocity', 1.0)
        self.declare_parameter('max_acceleration', 0.5)
        
        # Get parameters
        self.arm_name = self.get_parameter('arm_name').value
        self.gripper_name = self.get_parameter('gripper_name').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.max_acceleration = self.get_parameter('max_acceleration').value
        
        # Define bin positions in workspace
        self.bin_positions = {
            'bin_1': Pose(  # General waste (green)
                position=Point(x=0.3, y=0.4, z=0.0),
                orientation=Quaternion(x=0, y=0.707, z=0, w=0.707)
            ),
            'bin_2': Pose(  # Infectious waste (red)
                position=Point(x=0.3, y=0.0, z=0.0),
                orientation=Quaternion(x=0, y=0.707, z=0, w=0.707)
            ),
            'bin_3': Pose(  # Sharps/Hazardous (orange)
                position=Point(x=0.3, y=-0.4, z=0.0),
                orientation=Quaternion(x=0, y=0.707, z=0, w=0.707)
            )
        }
        
        # Home position (ready state)
        self.home_position = Pose(
            position=Point(x=0.2, y=0.0, z=0.5),
            orientation=Quaternion(x=0, y=0.707, z=0, w=0.707)
        )
        
        # Current state
        self.state = RobotState.IDLE
        self.current_target_bin = None
        self.current_waste_pose = None
        
        # Subscribers
        self.target_bin_sub = self.create_subscription(
            String,
            'bin_management/target_bin',
            self.target_bin_callback,
            10
        )
        
        self.target_pose_sub = self.create_subscription(
            Pose,
            'waste_detection/target_pose',
            self.target_pose_callback,
            10
        )
        
        # Publishers
        self.arm_trajectory_pub = self.create_publisher(
            JointTrajectory,
            f'{self.arm_name}/trajectory_controller/command',
            10
        )
        
        self.gripper_command_pub = self.create_publisher(
            Float64,
            f'{self.gripper_name}/command',
            10
        )
        
        self.arm_status_pub = self.create_publisher(
            String,
            'arm_controller/status',
            10
        )
        
        # Timer for state machine
        self.state_timer = self.create_timer(0.1, self.state_machine)
        
        self.get_logger().info("Arm Controller Node initialized")
    
    def target_bin_callback(self, msg):
        """
        Receive target bin information
        """
        try:
            data = json.loads(msg.data)
            self.current_target_bin = data['bin_id']
            waste_type = data['waste_type']
            confidence = data['confidence']
            
            self.get_logger().info(
                f"Target bin set: {self.current_target_bin} "
                f"for {waste_type} (confidence: {confidence:.2f})"
            )
            
            # Start waste collection sequence
            if self.state == RobotState.IDLE:
                self.state = RobotState.PICKING
        
        except Exception as e:
            self.get_logger().error(f"Error parsing target bin: {e}")
    
    def target_pose_callback(self, msg):
        """
        Receive target pose for waste location
        """
        self.current_waste_pose = msg
        self.get_logger().debug(
            f"Waste location: x={msg.position.x:.3f}, "
            f"y={msg.position.y:.3f}, z={msg.position.z:.3f}"
        )
    
    def state_machine(self):
        """
        State machine for arm control sequences
        """
        if self.state == RobotState.PICKING:
            self.pick_waste()
        
        elif self.state == RobotState.TRANSPORTING:
            self.transport_to_bin()
        
        elif self.state == RobotState.PLACING:
            self.place_waste()
        
        elif self.state == RobotState.RETURNING:
            self.return_to_home()
    
    def pick_waste(self):
        """
        Sequence to pick up waste
        """
        if self.current_waste_pose is None:
            return
        
        self.get_logger().info("🤖 Starting waste pickup sequence...")
        
        # Move arm to waste location
        waste_approach_pose = Pose(
            position=Point(
                x=self.current_waste_pose.position.x,
                y=self.current_waste_pose.position.y,
                z=self.current_waste_pose.position.z + 0.15  # Approach height
            ),
            orientation=self.current_waste_pose.orientation
        )
        
        # Send trajectory
        trajectory = self.pose_to_trajectory(waste_approach_pose)
        self.arm_trajectory_pub.publish(trajectory)
        
        # Open gripper
        self.open_gripper()
        
        # Move to actual waste location
        trajectory = self.pose_to_trajectory(self.current_waste_pose)
        self.arm_trajectory_pub.publish(trajectory)
        
        # Close gripper
        self.close_gripper()
        
        # Move to transport position
        self.state = RobotState.TRANSPORTING
        self.get_logger().info("✓ Waste picked up successfully")
    
    def transport_to_bin(self):
        """
        Transport waste to target bin
        """
        if self.current_target_bin is None:
            self.state = RobotState.IDLE
            return
        
        self.get_logger().info(f"🚚 Transporting waste to {self.current_target_bin}...")
        
        # Get bin position
        bin_pose = self.bin_positions.get(self.current_target_bin)
        if bin_pose is None:
            self.get_logger().error(f"Unknown bin: {self.current_target_bin}")
            self.state = RobotState.IDLE
            return
        
        # Create approach pose above bin
        bin_approach_pose = Pose(
            position=Point(
                x=bin_pose.position.x,
                y=bin_pose.position.y,
                z=bin_pose.position.z + 0.2  # Approach height
            ),
            orientation=bin_pose.orientation
        )
        
        # Send trajectory
        trajectory = self.pose_to_trajectory(bin_approach_pose)
        self.arm_trajectory_pub.publish(trajectory)
        
        self.state = RobotState.PLACING
        self.get_logger().info("✓ Waste transported to bin area")
    
    def place_waste(self):
        """
        Place waste in bin
        """
        if self.current_target_bin is None:
            self.state = RobotState.IDLE
            return
        
        self.get_logger().info(f"📦 Placing waste in {self.current_target_bin}...")
        
        # Get bin position
        bin_pose = self.bin_positions[self.current_target_bin]
        
        # Move to bin opening
        trajectory = self.pose_to_trajectory(bin_pose)
        self.arm_trajectory_pub.publish(trajectory)
        
        # Release waste
        self.open_gripper()
        
        # Retract arm
        bin_retract_pose = Pose(
            position=Point(
                x=bin_pose.position.x - 0.2,
                y=bin_pose.position.y,
                z=bin_pose.position.z + 0.3
            ),
            orientation=bin_pose.orientation
        )
        
        trajectory = self.pose_to_trajectory(bin_retract_pose)
        self.arm_trajectory_pub.publish(trajectory)
        
        self.state = RobotState.RETURNING
        self.get_logger().info(f"✓ Waste placed in {self.current_target_bin}")
    
    def return_to_home(self):
        """
        Return arm to home position
        """
        self.get_logger().info("🏠 Returning to home position...")
        
        trajectory = self.pose_to_trajectory(self.home_position)
        self.arm_trajectory_pub.publish(trajectory)
        
        # Reset state
        self.state = RobotState.IDLE
        self.current_target_bin = None
        self.current_waste_pose = None
        
        self.get_logger().info("✓ Ready for next waste item")
        
        # Publish status
        status_msg = String()
        status_msg.data = json.dumps({
            'state': 'idle',
            'ready': True,
            'message': 'Waiting for waste classification'
        })
        self.arm_status_pub.publish(status_msg)
    
    def pose_to_trajectory(self, pose):
        """
        Convert Pose to JointTrajectory
        In a real implementation, use IK solver to convert Cartesian pose to joint angles
        """
        trajectory = JointTrajectory()
        trajectory.joint_names = [
            'arm_1_joint', 'arm_2_joint', 'arm_3_joint',
            'arm_4_joint', 'arm_5_joint', 'arm_6_joint',
            'arm_7_joint'
        ]
        
        point = JointTrajectoryPoint()
        
        # Simplified IK - in reality, use proper IK solver
        point.positions = [
            0.0, -1.57, 1.57, -1.57, -1.57, 0.0, 0.0
        ]
        point.velocities = [0.0] * 7
        point.time_from_start.sec = 2  # 2 seconds to reach pose
        
        trajectory.points.append(point)
        
        return trajectory
    
    def open_gripper(self):
        """
        Open gripper
        """
        from std_msgs.msg import Float64
        msg = Float64()
        msg.data = 0.0  # Open position
        self.gripper_command_pub.publish(msg)
    
    def close_gripper(self):
        """
        Close gripper
        """
        from std_msgs.msg import Float64
        msg = Float64()
        msg.data = 1.0  # Closed position
        self.gripper_command_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    controller = ArmController()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
