#!/usr/bin/env python3
"""
Safety Monitor Node for Medical Waste Management Robot
Handles emergency stops, collision detection, and force monitoring
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import JointState, LaserScan
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, Trigger
import json
from enum import Enum

class SafetyState(Enum):
    NORMAL = 0
    WARNING = 1
    EMERGENCY = 2

class SafetyMonitor(Node):
    """
    ROS2 Node for monitoring robot safety
    """
    
    def __init__(self):
        super().__init__('safety_monitor')
        
        # Declare parameters
        self.declare_parameter('min_obstacle_distance', 0.3)
        self.declare_parameter('emergency_stop_enabled', True)
        self.declare_parameter('collision_detection', True)
        self.declare_parameter('force_torque_monitoring', True)
        self.declare_parameter('max_joint_torque', 150.0)
        self.declare_parameter('warning_threshold', 0.5)  # meters
        
        # Get parameters
        self.min_obstacle_distance = self.get_parameter('min_obstacle_distance').value
        self.emergency_stop_enabled = self.get_parameter('emergency_stop_enabled').value
        self.collision_detection = self.get_parameter('collision_detection').value
        self.force_monitoring = self.get_parameter('force_torque_monitoring').value
        self.max_joint_torque = self.get_parameter('max_joint_torque').value
        self.warning_threshold = self.get_parameter('warning_threshold').value
        
        # Safety state
        self.safety_state = SafetyState.NORMAL
        self.emergency_triggered = False
        self.closest_obstacle_distance = float('inf')
        
        # Subscribers
        self.lidar_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.lidar_callback,
            10
        )
        
        self.joint_state_sub = self.create_subscription(
            JointState,
            'arm/joint_states',
            self.joint_state_callback,
            10
        )
        
        # Publishers
        self.safety_status_pub = self.create_publisher(
            String,
            'safety_monitor/status',
            10
        )
        
        self.emergency_stop_pub = self.create_publisher(
            Bool,
            'safety_monitor/emergency_stop',
            10
        )
        
        self.obstacle_alert_pub = self.create_publisher(
            String,
            'safety_monitor/obstacle_alert',
            10
        )
        
        # Services
        self.emergency_stop_service = self.create_service(
            SetBool,
            'safety_monitor/emergency_stop',
            self.emergency_stop_callback
        )
        
        self.reset_safety_service = self.create_service(
            Trigger,
            'safety_monitor/reset',
            self.reset_safety_callback
        )
        
        # Timer for monitoring
        self.timer = self.create_timer(0.1, self.monitor_safety)
        
        self.get_logger().info("Safety Monitor Node initialized")
        self.print_safety_config()
    
    def lidar_callback(self, msg):
        """
        Process LiDAR scan data for obstacle detection
        """
        if len(msg.ranges) == 0:
            return
        
        try:
            # Find closest obstacle
            valid_ranges = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
            
            if valid_ranges:
                self.closest_obstacle_distance = min(valid_ranges)
                
                # Check for collision or warning
                if self.closest_obstacle_distance < self.min_obstacle_distance:
                    if not self.emergency_triggered and self.collision_detection:
                        self.get_logger().warn(
                            f"⚠️  COLLISION WARNING: Obstacle detected at {self.closest_obstacle_distance:.2f}m"
                        )
                        self.trigger_emergency_stop()
                
                elif self.closest_obstacle_distance < self.warning_threshold:
                    self.safety_state = SafetyState.WARNING
                    self.publish_obstacle_alert()
        
        except Exception as e:
            self.get_logger().error(f"Error processing LiDAR data: {e}")
    
    def joint_state_callback(self, msg):
        """
        Monitor joint states and torques
        """
        try:
            # Check for high torques (if available in effort field)
            if len(msg.effort) > 0:
                max_effort = max(msg.effort)
                
                if max_effort > self.max_joint_torque and self.force_monitoring:
                    self.get_logger().warn(
                        f"⚠️  HIGH TORQUE DETECTED: {max_effort:.1f} Nm "
                        f"(limit: {self.max_joint_torque} Nm)"
                    )
                    self.trigger_emergency_stop()
        
        except Exception as e:
            self.get_logger().error(f"Error processing joint states: {e}")
    
    def trigger_emergency_stop(self):
        """
        Trigger emergency stop sequence
        """
        if not self.emergency_triggered:
            self.emergency_triggered = True
            self.safety_state = SafetyState.EMERGENCY
            
            self.get_logger().error("🛑 EMERGENCY STOP TRIGGERED!")
            
            # Publish emergency stop signal
            stop_msg = Bool()
            stop_msg.data = True
            self.emergency_stop_pub.publish(stop_msg)
            
            # Publish alert
            alert = String()
            alert.data = json.dumps({
                'event': 'emergency_stop',
                'reason': 'collision_or_high_force',
                'closest_obstacle': self.closest_obstacle_distance
            })
            self.obstacle_alert_pub.publish(alert)
    
    def publish_obstacle_alert(self):
        """
        Publish obstacle warning
        """
        alert = String()
        alert.data = json.dumps({
            'event': 'obstacle_warning',
            'distance': self.closest_obstacle_distance,
            'threshold': self.warning_threshold
        })
        self.obstacle_alert_pub.publish(alert)
    
    def monitor_safety(self):
        """
        Periodic safety monitoring
        """
        status = {
            'state': self.safety_state.name,
            'emergency_triggered': self.emergency_triggered,
            'closest_obstacle': self.closest_obstacle_distance,
            'collision_detection': self.collision_detection,
            'force_monitoring': self.force_monitoring
        }
        
        status_msg = String()
        status_msg.data = json.dumps(status)
        self.safety_status_pub.publish(status_msg)
    
    def emergency_stop_callback(self, request, response):
        """
        Service callback for emergency stop
        """
        if request.data:
            self.trigger_emergency_stop()
            response.success = True
            response.message = "Emergency stop activated"
        else:
            self.reset_emergency_stop()
            response.success = True
            response.message = "Emergency stop deactivated"
        
        return response
    
    def reset_safety_callback(self, request, response):
        """
        Reset safety system after emergency
        """
        self.reset_emergency_stop()
        response.success = True
        response.message = "Safety system reset"
        return response
    
    def reset_emergency_stop(self):
        """
        Reset emergency stop
        """
        self.emergency_triggered = False
        self.safety_state = SafetyState.NORMAL
        self.get_logger().info("✓ Emergency stop reset")
        
        stop_msg = Bool()
        stop_msg.data = False
        self.emergency_stop_pub.publish(stop_msg)
    
    def print_safety_config(self):
        """
        Print safety configuration
        """
        self.get_logger().info("\n" + "="*60)
        self.get_logger().info("SAFETY MONITOR CONFIGURATION")
        self.get_logger().info("="*60)
        self.get_logger().info(
            f"Min Obstacle Distance: {self.min_obstacle_distance} m\n"
            f"Warning Threshold: {self.warning_threshold} m\n"
            f"Emergency Stop: {'Enabled' if self.emergency_stop_enabled else 'Disabled'}\n"
            f"Collision Detection: {'Enabled' if self.collision_detection else 'Disabled'}\n"
            f"Force Monitoring: {'Enabled' if self.force_monitoring else 'Disabled'}\n"
            f"Max Joint Torque: {self.max_joint_torque} Nm"
        )
        self.get_logger().info("="*60 + "\n")


def main(args=None):
    rclpy.init(args=args)
    monitor = SafetyMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
