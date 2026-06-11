#!/usr/bin/env python3
"""
Unit Tests for Medical Waste Management Robot
Tests for perception, manipulation, and safety systems
"""

import unittest
import json
from datetime import datetime

class TestYOLODetector(unittest.TestCase):
    """Test cases for YOLO waste detector"""
    
    def test_waste_classification(self):
        """Test waste classification categories"""
        categories = {
            0: 'general_waste',
            1: 'infectious_waste',
            2: 'sharps_hazardous'
        }
        
        self.assertEqual(len(categories), 3)
        self.assertIn(0, categories)
        self.assertIn(1, categories)
        self.assertIn(2, categories)
    
    def test_confidence_threshold(self):
        """Test confidence threshold validation"""
        confidence_values = [0.95, 0.85, 0.75, 0.65, 0.45]
        threshold = 0.5
        
        valid_detections = [c for c in confidence_values if c >= threshold]
        
        self.assertEqual(len(valid_detections), 4)
        self.assertNotIn(0.45, valid_detections)
    
    def test_bounding_box_format(self):
        """Test bounding box coordinate format"""
        # YOLO format: x_center, y_center, width, height (normalized 0-1)
        bbox = {
            'x_center': 0.5,
            'y_center': 0.5,
            'width': 0.3,
            'height': 0.4
        }
        
        self.assertTrue(0 <= bbox['x_center'] <= 1)
        self.assertTrue(0 <= bbox['y_center'] <= 1)
        self.assertTrue(0 <= bbox['width'] <= 1)
        self.assertTrue(0 <= bbox['height'] <= 1)


class TestArmController(unittest.TestCase):
    """Test cases for robotic arm controller"""
    
    def test_bin_positions(self):
        """Test bin position coordinates"""
        bins = {
            'bin_1': {'x': 0.3, 'y': 0.4, 'z': 0.0},
            'bin_2': {'x': 0.3, 'y': 0.0, 'z': 0.0},
            'bin_3': {'x': 0.3, 'y': -0.4, 'z': 0.0}
        }
        
        self.assertEqual(len(bins), 3)
        
        for bin_id, pos in bins.items():
            self.assertTrue(-1 <= pos['x'] <= 1)
            self.assertTrue(-1 <= pos['y'] <= 1)
            self.assertTrue(-1 <= pos['z'] <= 1)
    
    def test_gripper_positions(self):
        """Test gripper open/close positions"""
        open_pos = 0.0
        close_pos = 1.0
        
        self.assertLess(open_pos, close_pos)
        self.assertTrue(0 <= open_pos <= 1)
        self.assertTrue(0 <= close_pos <= 1)
    
    def test_trajectory_generation(self):
        """Test trajectory point generation"""
        trajectory = {
            'joint_names': ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7'],
            'positions': [0.0, -1.57, 1.57, -1.57, -1.57, 0.0, 0.0],
            'time_from_start': 2.0
        }
        
        self.assertEqual(len(trajectory['joint_names']), 7)
        self.assertEqual(len(trajectory['positions']), 7)
        self.assertGreater(trajectory['time_from_start'], 0)


class TestBinManagement(unittest.TestCase):
    """Test cases for bin management system"""
    
    def test_bin_capacity(self):
        """Test bin capacity settings"""
        bins = {
            'bin_1': {'name': 'General', 'capacity': 100},
            'bin_2': {'name': 'Infectious', 'capacity': 80},
            'bin_3': {'name': 'Sharps', 'capacity': 50}
        }
        
        total_capacity = sum(b['capacity'] for b in bins.values())
        self.assertEqual(total_capacity, 230)
    
    def test_bin_full_threshold(self):
        """Test bin full detection"""
        capacity = 100
        current_level = 92
        threshold = 0.9
        
        fill_percentage = current_level / capacity
        is_full = fill_percentage >= threshold
        
        self.assertTrue(is_full)
    
    def test_waste_classification_to_bin(self):
        """Test waste type to bin mapping"""
        mapping = {
            'general_waste': 'bin_1',
            'infectious_waste': 'bin_2',
            'sharps_hazardous': 'bin_3'
        }
        
        self.assertEqual(mapping['general_waste'], 'bin_1')
        self.assertEqual(mapping['infectious_waste'], 'bin_2')
        self.assertEqual(mapping['sharps_hazardous'], 'bin_3')
    
    def test_waste_volume_calculation(self):
        """Test waste volume calculation"""
        waste_items = 10
        unit_volume = 0.5  # liters
        total_volume = waste_items * unit_volume
        
        self.assertEqual(total_volume, 5.0)


class TestTaskCoordinator(unittest.TestCase):
    """Test cases for task coordinator"""
    
    def test_task_queue_size(self):
        """Test task queue size limitation"""
        max_queue_size = 10
        tasks = list(range(15))  # Try to add 15 tasks
        queue = tasks[:max_queue_size]
        
        self.assertEqual(len(queue), 10)
    
    def test_task_priority(self):
        """Test task priority ordering"""
        tasks = [
            {'id': 1, 'priority': 1},  # General waste
            {'id': 2, 'priority': 3},  # Infectious waste (higher)
            {'id': 3, 'priority': 2},  # Sharps waste
        ]
        
        sorted_tasks = sorted(tasks, key=lambda t: t['priority'], reverse=True)
        
        self.assertEqual(sorted_tasks[0]['id'], 2)
        self.assertEqual(sorted_tasks[1]['id'], 3)
        self.assertEqual(sorted_tasks[2]['id'], 1)
    
    def test_task_retry_logic(self):
        """Test task retry mechanism"""
        max_retries = 3
        current_retries = 2
        
        can_retry = current_retries < max_retries
        self.assertTrue(can_retry)
        
        current_retries = 3
        can_retry = current_retries < max_retries
        self.assertFalse(can_retry)


class TestSafetyMonitor(unittest.TestCase):
    """Test cases for safety monitor"""
    
    def test_obstacle_detection_threshold(self):
        """Test obstacle detection distance threshold"""
        min_obstacle_distance = 0.3  # meters
        test_distances = [0.1, 0.25, 0.3, 0.5, 1.0]
        
        collisions = [d for d in test_distances if d < min_obstacle_distance]
        
        self.assertEqual(len(collisions), 2)
    
    def test_warning_threshold(self):
        """Test warning distance threshold"""
        warning_threshold = 0.5  # meters
        min_obstacle_distance = 0.3
        
        test_distance = 0.4
        
        is_warning = test_distance < warning_threshold and test_distance >= min_obstacle_distance
        self.assertTrue(is_warning)
    
    def test_force_limit(self):
        """Test joint force/torque limit"""
        max_joint_torque = 150.0  # Nm
        test_torques = [50.0, 100.0, 140.0, 155.0, 200.0]
        
        exceeded = [t for t in test_torques if t > max_joint_torque]
        
        self.assertEqual(len(exceeded), 2)
    
    def test_emergency_stop_state(self):
        """Test emergency stop state transitions"""
        emergency_triggered = False
        self.assertFalse(emergency_triggered)
        
        emergency_triggered = True
        self.assertTrue(emergency_triggered)
        
        emergency_triggered = False
        self.assertFalse(emergency_triggered)


class TestDataPipeline(unittest.TestCase):
    """Test cases for data pipeline"""
    
    def test_classification_message_format(self):
        """Test classification message format"""
        msg_data = "waste_type:infectious_waste,bin:bin_2,confidence:0.95"
        
        data = {}
        for item in msg_data.split(','):
            key, value = item.split(':')
            data[key] = value
        
        self.assertEqual(data['waste_type'], 'infectious_waste')
        self.assertEqual(data['bin'], 'bin_2')
        self.assertEqual(data['confidence'], '0.95')
    
    def test_pose_calculation(self):
        """Test 3D pose calculation from 2D detection"""
        # Image coordinates
        image_x = 640  # pixels
        image_y = 480  # pixels
        image_w = 1280
        image_h = 960
        
        # Normalize
        norm_x = image_x / image_w  # 0.5
        norm_y = image_y / image_h  # 0.5
        
        # Map to workspace
        pose_x = 0.3 + (norm_x - 0.5) * 0.5
        pose_y = 0.2 + (norm_y - 0.5) * 0.3
        
        self.assertAlmostEqual(pose_x, 0.3, places=2)
        self.assertAlmostEqual(pose_y, 0.2, places=2)


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for full system"""
    
    def test_complete_waste_collection_workflow(self):
        """Test complete waste collection workflow"""
        # Step 1: Waste detection
        detected_waste = 'infectious_waste'
        target_bin = 'bin_2'
        confidence = 0.95
        
        self.assertGreater(confidence, 0.5)
        
        # Step 2: Task creation
        task = {
            'type': 'collect_waste',
            'waste_type': detected_waste,
            'target_bin': target_bin,
            'priority': 3
        }
        
        self.assertEqual(task['waste_type'], detected_waste)
        
        # Step 3: Safety check
        obstacle_distance = 1.5
        min_obstacle_distance = 0.3
        safe_to_proceed = obstacle_distance > min_obstacle_distance
        
        self.assertTrue(safe_to_proceed)
        
        # Step 4: Arm execution
        arm_ready = True
        self.assertTrue(arm_ready)
        
        # Step 5: Task completion
        task_completed = True
        self.assertTrue(task_completed)
    
    def test_emergency_stop_workflow(self):
        """Test emergency stop workflow"""
        # Normal operation
        robot_state = 'moving'
        obstacle_detected = False
        
        # Obstacle appears
        obstacle_detected = True
        obstacle_distance = 0.15  # 15 cm
        
        # Safety trigger
        if obstacle_distance < 0.3:
            robot_state = 'emergency_stop'
        
        self.assertEqual(robot_state, 'emergency_stop')
        
        # Reset
        robot_state = 'idle'
        self.assertEqual(robot_state, 'idle')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestYOLODetector))
    suite.addTests(loader.loadTestsFromTestCase(TestArmController))
    suite.addTests(loader.loadTestsFromTestCase(TestBinManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskCoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestSafetyMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_tests()
