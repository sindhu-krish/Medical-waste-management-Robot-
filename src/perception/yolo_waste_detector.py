#!/usr/bin/env python3
"""
YOLO-based Medical Waste Detection and Classification Node
Detects and classifies medical waste into categories:
- General Waste
- Infectious Waste
- Sharps/Hazardous Waste
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO
import torch

# Waste categories mapping
WASTE_CATEGORIES = {
    0: {'name': 'general_waste', 'bin': 'bin_1', 'color': (0, 255, 0)},      # Green
    1: {'name': 'infectious_waste', 'bin': 'bin_2', 'color': (0, 0, 255)},    # Red
    2: {'name': 'sharps_hazardous', 'bin': 'bin_3', 'color': (0, 165, 255)}   # Orange
}

class YOLOWasteDetector(Node):
    """
    ROS2 Node for YOLO-based medical waste detection and classification
    """
    
    def __init__(self):
        super().__init__('yolo_waste_detector')
        
        # Initialize parameters
        self.declare_parameter('model_path', 'models/waste_detector.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('input_image_size', 640)
        self.declare_parameter('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        
        # Get parameters
        model_path = self.get_parameter('model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.image_size = self.get_parameter('input_image_size').value
        self.device = self.get_parameter('device').value
        
        self.get_logger().info(f"Loading YOLO model from: {model_path}")
        self.get_logger().info(f"Using device: {self.device}")
        
        # Load YOLO model
        try:
            self.model = YOLO(model_path)
            self.get_logger().info("YOLO model loaded successfully")
        except Exception as e:
            self.get_logger().error(f"Failed to load YOLO model: {e}")
            raise
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Subscribers
        self.image_subscription = self.create_subscription(
            Image,
            'camera/rgb/image_raw',
            self.image_callback,
            10
        )
        
        # Publishers
        self.detection_pub = self.create_publisher(
            String,
            'waste_detection/classification',
            10
        )
        
        self.annotated_image_pub = self.create_publisher(
            Image,
            'waste_detection/annotated_image',
            10
        )
        
        self.waste_pose_pub = self.create_publisher(
            Pose,
            'waste_detection/target_pose',
            10
        )
        
        self.get_logger().info("YOLO Waste Detector Node initialized")
    
    def image_callback(self, msg):
        """
        Callback function to process incoming images
        """
        try:
            # Convert ROS Image message to OpenCV image
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Run YOLO inference
            results = self.model(frame, conf=self.confidence_threshold, device=self.device)
            
            # Process results
            detections = results[0]
            
            if len(detections.boxes) > 0:
                # Get the first (highest confidence) detection
                box = detections.boxes[0]
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Classify waste
                waste_info = WASTE_CATEGORIES.get(class_id, {
                    'name': 'unknown',
                    'bin': 'unknown',
                    'color': (128, 128, 128)
                })
                
                self.get_logger().info(
                    f"Detected: {waste_info['name']} | "
                    f"Confidence: {confidence:.2f} | "
                    f"Target Bin: {waste_info['bin']}"
                )
                
                # Publish classification result
                classification_msg = String()
                classification_msg.data = (
                    f"waste_type:{waste_info['name']},"
                    f"bin:{waste_info['bin']},"
                    f"confidence:{confidence:.2f}"
                )
                self.detection_pub.publish(classification_msg)
                
                # Calculate target pose for robotic arm
                target_pose = self.calculate_target_pose(
                    frame, x1, y1, x2, y2, waste_info['bin']
                )
                self.waste_pose_pub.publish(target_pose)
                
                # Draw annotation on frame
                frame = self.annotate_frame(
                    frame, x1, y1, x2, y2, 
                    waste_info['name'], confidence, waste_info['color']
                )
            
            # Publish annotated image
            annotated_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.annotated_image_pub.publish(annotated_msg)
            
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")
    
    def annotate_frame(self, frame, x1, y1, x2, y2, class_name, confidence, color):
        """
        Add bounding box and labels to frame
        """
        # Convert coordinates to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label text
        label = f"{class_name}: {confidence:.2f}"
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.rectangle(
            frame,
            (x1, y1 - label_size[1] - 10),
            (x1 + label_size[0], y1),
            color,
            -1
        )
        
        # Put label text
        cv2.putText(
            frame,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        return frame
    
    def calculate_target_pose(self, frame, x1, y1, x2, y2, bin_id):
        """
        Calculate 3D target pose for robotic arm based on 2D detection
        
        In a real scenario, this would use depth information to calculate
        the actual 3D coordinates. For now, we'll use a simplified approach.
        """
        from geometry_msgs.msg import Pose, Point, Quaternion
        
        pose = Pose()
        
        # Get center of bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Normalize to image dimensions
        h, w = frame.shape[:2]
        norm_x = center_x / w
        norm_y = center_y / h
        
        # Map to workspace coordinates (example values)
        # These should be calibrated based on your actual robot setup
        pose.position.x = 0.3 + (norm_x - 0.5) * 0.5  # X coordinate
        pose.position.y = 0.2 + (norm_y - 0.5) * 0.3  # Y coordinate
        pose.position.z = 0.1  # Z coordinate (height above waste)
        
        # Set default orientation (quaternion)
        pose.orientation.x = 0.0
        pose.orientation.y = 0.707
        pose.orientation.z = 0.0
        pose.orientation.w = 0.707
        
        return pose


def main(args=None):
    rclpy.init(args=args)
    detector = YOLOWasteDetector()
    
    try:
        rclpy.spin(detector)
    except KeyboardInterrupt:
        pass
    finally:
        detector.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
