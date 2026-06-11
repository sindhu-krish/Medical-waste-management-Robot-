#!/usr/bin/env python3
"""
Bin Management System Node
Manages three waste bins:
1. General Waste Bin (Green)
2. Infectious Waste Bin (Red)
3. Sharps/Hazardous Waste Bin (Orange)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool
import json
from datetime import datetime

class BinManagementSystem(Node):
    """
    ROS2 Node for managing waste bins and tracking waste disposal
    """
    
    def __init__(self):
        super().__init__('bin_management_system')
        
        # Initialize bin states
        self.bins = {
            'bin_1': {
                'name': 'General Waste',
                'color': 'green',
                'capacity': 100,  # liters
                'current_level': 0,
                'waste_count': 0,
                'waste_items': []
            },
            'bin_2': {
                'name': 'Infectious Waste',
                'color': 'red',
                'capacity': 80,
                'current_level': 0,
                'waste_count': 0,
                'waste_items': []
            },
            'bin_3': {
                'name': 'Sharps/Hazardous Waste',
                'color': 'orange',
                'capacity': 50,
                'current_level': 0,
                'waste_count': 0,
                'waste_items': []
            }
        }
        
        # Declare parameters
        self.declare_parameter('bin_full_threshold', 0.9)  # 90% full
        self.declare_parameter('waste_unit_volume', 0.5)    # liters per waste item
        
        # Get parameters
        self.bin_full_threshold = self.get_parameter('bin_full_threshold').value
        self.waste_unit_volume = self.get_parameter('waste_unit_volume').value
        
        # Subscribers
        self.waste_classification_sub = self.create_subscription(
            String,
            'waste_detection/classification',
            self.classification_callback,
            10
        )
        
        self.target_pose_sub = self.create_subscription(
            Pose,
            'waste_detection/target_pose',
            self.pose_callback,
            10
        )
        
        self.arm_state_sub = self.create_subscription(
            JointState,
            'arm/joint_states',
            self.arm_state_callback,
            10
        )
        
        # Publishers
        self.bin_status_pub = self.create_publisher(
            String,
            'bin_management/status',
            10
        )
        
        self.bin_full_alert_pub = self.create_publisher(
            String,
            'bin_management/full_alert',
            10
        )
        
        self.target_bin_pub = self.create_publisher(
            String,
            'bin_management/target_bin',
            10
        )
        
        # Services
        self.empty_bin_service = self.create_service(
            SetBool,
            'bin_management/empty_bin',
            self.empty_bin_callback
        )
        
        # Timer for publishing bin status
        self.timer = self.create_timer(2.0, self.publish_bin_status)
        
        # Store current waste info
        self.current_waste = None
        self.current_target_bin = None
        self.arm_at_target = False
        
        self.get_logger().info("Bin Management System initialized")
        self.print_bin_info()
    
    def classification_callback(self, msg):
        """
        Handle waste classification results
        """
        try:
            # Parse classification data
            data = {}
            for item in msg.data.split(','):
                key, value = item.split(':')
                data[key] = value
            
            waste_type = data.get('waste_type', 'unknown')
            target_bin = data.get('bin', 'unknown')
            confidence = float(data.get('confidence', 0))
            
            self.current_waste = {
                'type': waste_type,
                'target_bin': target_bin,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            self.get_logger().info(
                f"Waste Classified: {waste_type} -> {target_bin} "
                f"(Confidence: {confidence:.2f})"
            )
            
            # Publish target bin information
            bin_msg = String()
            bin_msg.data = json.dumps({
                'bin_id': target_bin,
                'waste_type': waste_type,
                'confidence': confidence
            })
            self.target_bin_pub.publish(bin_msg)
            
            self.current_target_bin = target_bin
            
        except Exception as e:
            self.get_logger().error(f"Error parsing classification: {e}")
    
    def pose_callback(self, msg):
        """
        Handle target pose for waste placement
        """
        self.get_logger().debug(
            f"Received target pose: "
            f"x={msg.position.x:.3f}, y={msg.position.y:.3f}, z={msg.position.z:.3f}"
        )
    
    def arm_state_callback(self, msg):
        """
        Monitor arm state to detect when waste is placed
        """
        # Check if arm has returned to home position (waste placement complete)
        if len(msg.position) > 0 and all(p < 0.1 for p in msg.position[:3]):
            self.arm_at_target = False
            self.attempt_waste_placement()
    
    def attempt_waste_placement(self):
        """
        Process waste placement in target bin
        """
        if self.current_waste and self.current_target_bin:
            bin_id = self.current_target_bin
            
            if bin_id in self.bins:
                bin_info = self.bins[bin_id]
                
                # Update bin status
                waste_volume = self.waste_unit_volume
                bin_info['current_level'] += waste_volume
                bin_info['waste_count'] += 1
                bin_info['waste_items'].append({
                    'type': self.current_waste['type'],
                    'confidence': self.current_waste['confidence'],
                    'timestamp': self.current_waste['timestamp']
                })
                
                self.get_logger().info(
                    f"Waste placed in {bin_info['name']}: "
                    f"Level: {bin_info['current_level']:.1f}/{bin_info['capacity']}L"
                )
                
                # Check if bin is full
                fill_percentage = bin_info['current_level'] / bin_info['capacity']
                if fill_percentage >= self.bin_full_threshold:
                    self.publish_bin_full_alert(bin_id, fill_percentage)
            
            # Reset current waste
            self.current_waste = None
            self.current_target_bin = None
    
    def publish_bin_status(self):
        """
        Publish current bin status
        """
        status_data = {}
        
        for bin_id, bin_info in self.bins.items():
            fill_percentage = (bin_info['current_level'] / bin_info['capacity']) * 100
            status_data[bin_id] = {
                'name': bin_info['name'],
                'color': bin_info['color'],
                'capacity_liters': bin_info['capacity'],
                'current_level_liters': bin_info['current_level'],
                'fill_percentage': fill_percentage,
                'waste_count': bin_info['waste_count'],
                'status': 'full' if fill_percentage >= 100 else 'operational'
            }
        
        status_msg = String()
        status_msg.data = json.dumps(status_data, indent=2)
        self.bin_status_pub.publish(status_msg)
    
    def publish_bin_full_alert(self, bin_id, fill_percentage):
        """
        Publish alert when bin is full
        """
        alert_msg = String()
        alert_data = {
            'bin_id': bin_id,
            'bin_name': self.bins[bin_id]['name'],
            'fill_percentage': fill_percentage * 100,
            'timestamp': datetime.now().isoformat(),
            'action': 'bin_needs_emptying'
        }
        alert_msg.data = json.dumps(alert_data)
        self.bin_full_alert_pub.publish(alert_msg)
        
        self.get_logger().warn(
            f"⚠️  BIN FULL ALERT: {self.bins[bin_id]['name']} "
            f"({fill_percentage*100:.1f}%) needs emptying!"
        )
    
    def empty_bin_callback(self, request, response):
        """
        Service callback to empty a bin
        """
        try:
            bin_id = request.data  # This would need modification for actual data
            
            if bin_id in self.bins:
                self.bins[bin_id]['current_level'] = 0
                self.bins[bin_id]['waste_items'] = []
                
                self.get_logger().info(f"Emptied bin: {bin_id}")
                response.success = True
                response.message = f"Successfully emptied {bin_id}"
            else:
                response.success = False
                response.message = f"Unknown bin: {bin_id}"
                
        except Exception as e:
            response.success = False
            response.message = str(e)
        
        return response
    
    def print_bin_info(self):
        """
        Print bin configuration information
        """
        self.get_logger().info("\n" + "="*60)
        self.get_logger().info("WASTE BIN CONFIGURATION")
        self.get_logger().info("="*60)
        
        for bin_id, bin_info in self.bins.items():
            self.get_logger().info(
                f"\n{bin_id}: {bin_info['name']} ({bin_info['color']})\n"
                f"  Capacity: {bin_info['capacity']} liters\n"
                f"  Full Threshold: {self.bin_full_threshold*100:.0f}%"
            )
        
        self.get_logger().info("="*60 + "\n")


def main(args=None):
    rclpy.init(args=args)
    bin_manager = BinManagementSystem()
    
    try:
        rclpy.spin(bin_manager)
    except KeyboardInterrupt:
        pass
    finally:
        bin_manager.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
