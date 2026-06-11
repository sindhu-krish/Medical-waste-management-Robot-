# Medical Waste Management Robot - System Architecture

## Overview

This document describes the complete system architecture for the Medical Waste Management Robot, including hardware components, software modules, communication protocols, and data flow.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Medical Waste Management Robot                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   PERCEPTION    │  │   NAVIGATION     │  │  MANIPULATION   │ │
│  ├─────────────────┤  ├──────────────────┤  ├─────────────────┤ │
│  │ • YOLO Detector │  │ • Nav2 Stack     │  │ • Arm Control   │ │
│  │ • Camera Driver │  │ • SLAM Toolbox   │  │ • Gripper Ctrl  │ │
│  │ • Classification│  │ • Path Planning  │  │ • Trajectory    │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
│         │                    │                      │             │
│         └────────────────────┴──────────────────────┘             │
│                              │                                     │
│         ┌────────────────────┴────────────────────┐              │
│         │                                         │               │
│  ┌─────────────────────┐            ┌──────────────────────┐    │
│  │  TASK MANAGEMENT    │            │  SAFETY MONITORING   │    │
│  ├─────────────────────┤            ├──────────────────────┤    │
│  │ • Task Coordinator  │            │ • Emergency Stop     │    │
│  │ • Task Scheduler    │            │ • Collision Detect   │    │
│  │ • Priority Queue    │            │ • Force Monitoring   │    │
│  │ • Retry Logic       │            │ • LiDAR Monitoring   │    │
│  └─────────────────────┘            └──────────────────────┘    │
│         │                                    │                    │
│  ┌──────────────────────────────────────────────────┐            │
│  │         BIN MANAGEMENT SYSTEM                    │            │
│  ├──────────────────────────────────────────────────┤            │
│  │ • Bin_1: General Waste (Green) - 100L            │            │
│  │ • Bin_2: Infectious Waste (Red) - 80L            │            │
│  │ • Bin_3: Sharps/Hazardous (Orange) - 50L         │            │
│  │ • Capacity Tracking & Alerts                      │            │
│  └──────────────────────────────────────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Hardware Components

### Mobile Base
- **Platform**: TIAGo (PAL Robotics) or custom differential drive
- **Dimensions**: ~0.5m x 0.5m x 1.5m (height)
- **Weight**: ~100 kg
- **Max Speed**: 1.5 m/s
- **Battery**: Li-ion, 8-10 hour runtime

### Sensors

| Sensor | Model | Purpose | Topic |
|--------|-------|---------|-------|
| RGB-D Camera | Intel RealSense D435 | Waste detection | `/camera/rgb/image_raw` |
| 2D LiDAR | SICK TIM781S | Obstacle detection | `/scan` |
| IMU | MPU-9250 | Orientation tracking | `/imu/data` |
| Force-Torque Sensor | ATI Mini45 | Gripper feedback | `/ft_sensor` |

### Actuators

| Actuator | Specs | Purpose |
|----------|-------|----------|
| Robotic Arm | 7-DOF, 1.2m reach | Waste manipulation |
| Gripper | Parallel jaw, 100N | Waste grasping |
| Mobile Base | Differential drive | Navigation |

## Software Architecture

### ROS2 Nodes

```
1. PERCEPTION LAYER
   └─ yolo_waste_detector.py
      - Subscribes: /camera/rgb/image_raw
      - Publishes: /waste_detection/classification
      - Publishes: /waste_detection/target_pose
      - Publishes: /waste_detection/annotated_image

2. TASK MANAGEMENT LAYER
   └─ task_coordinator.py
      - Subscribes: /waste_detection/classification
      - Subscribes: /arm_controller/status
      - Publishes: /task_coordinator/assignment
      - Publishes: /task_coordinator/status

3. MANIPULATION LAYER
   ├─ arm_controller.py
   │  - Subscribes: /bin_management/target_bin
   │  - Subscribes: /waste_detection/target_pose
   │  - Publishes: /arm_controller/status
   │  - Publishes: /arm/trajectory_controller/command
   │
   └─ bin_manager.py
      - Subscribes: /waste_detection/classification
      - Publishes: /bin_management/status
      - Publishes: /bin_management/target_bin

4. SAFETY LAYER
   └─ safety_monitor.py
      - Subscribes: /scan (LiDAR)
      - Subscribes: /arm/joint_states
      - Publishes: /safety_monitor/status
      - Publishes: /safety_monitor/emergency_stop
      - Service: /safety_monitor/emergency_stop

5. NAVIGATION LAYER
   └─ nav2_bringup.launch.py
      - Manages Nav2 stack
      - Localization & mapping
      - Path planning
```

## Data Flow

### Waste Collection Workflow

```
1. DETECTION PHASE
   Camera Feed → YOLO Model → Classification
   Output: waste_type, confidence, 3D pose

2. TASK CREATION PHASE
   Classification → Task Coordinator → Queue Management
   Output: Task ID, Priority, Status

3. SAFETY CHECK PHASE
   LiDAR Scan → Safety Monitor → Collision Check
   Output: Safe/Unsafe Status

4. ASSIGNMENT PHASE
   Task → Arm Controller → Trajectory Planning
   Output: Joint commands

5. EXECUTION PHASE
   Joint Commands → Arm Actuators → Waste Pickup
   Force Feedback → Safety Monitor (continuous)

6. TRANSPORT PHASE
   Arm moves waste to bin
   Safety Monitor: Continuous obstacle checking

7. PLACEMENT PHASE
   Waste → Correct Bin → Bin Manager Updated
   Output: Bin status, fill level

8. RETURN PHASE
   Arm returns to home position
   Task marked as completed
```

## Communication Protocols

### ROS2 Topics

**Image Topics**:
- `/camera/rgb/image_raw` (sensor_msgs/Image) - 30 FPS
- `/waste_detection/annotated_image` (sensor_msgs/Image) - Debug

**Detection Topics**:
- `/waste_detection/classification` (std_msgs/String) - Detection results
- `/waste_detection/target_pose` (geometry_msgs/Pose) - 3D location

**Control Topics**:
- `/arm/trajectory_controller/command` (trajectory_msgs/JointTrajectory)
- `/gripper/command` (std_msgs/Float64)

**Status Topics**:
- `/arm_controller/status` (std_msgs/String) - Arm state
- `/bin_management/status` (std_msgs/String) - Bin levels
- `/safety_monitor/status` (std_msgs/String) - Safety state
- `/task_coordinator/status` (std_msgs/String) - Task info

**Sensor Topics**:
- `/scan` (sensor_msgs/LaserScan) - LiDAR data
- `/imu/data` (sensor_msgs/Imu) - IMU data
- `/arm/joint_states` (sensor_msgs/JointState) - Joint feedback

### Message Formats

**Classification Message**:
```json
{
  "waste_type": "infectious_waste",
  "bin": "bin_2",
  "confidence": 0.95,
  "timestamp": "2024-06-11T10:30:45.123Z"
}
```

**Bin Status Message**:
```json
{
  "bin_1": {
    "name": "General Waste",
    "fill_percentage": 45.5,
    "capacity_liters": 100,
    "status": "operational"
  },
  "bin_2": {
    "name": "Infectious Waste",
    "fill_percentage": 78.2,
    "capacity_liters": 80,
    "status": "operational"
  },
  "bin_3": {
    "name": "Sharps/Hazardous",
    "fill_percentage": 92.0,
    "capacity_liters": 50,
    "status": "full"
  }
}
```

## Safety Architecture

### Safety Levels

1. **Level 0: Normal Operation**
   - All systems active
   - Continuous monitoring
   - Obstacle distance > 0.5m

2. **Level 1: Warning**
   - Obstacle distance 0.3-0.5m
   - Reduced speed
   - Enhanced monitoring

3. **Level 2: Emergency Stop**
   - Obstacle distance < 0.3m
   - Immediate stop
   - Force exceeds limit
   - Manual emergency button

### Safety Checks

```
┌─────────────────────────────────┐
│    Continuous Monitoring        │
├─────────────────────────────────┤
│ • LiDAR: 10 Hz                  │
│ • Joint State: 50 Hz            │
│ • Force-Torque: 100 Hz          │
│ • Safety Decision: 100 Hz       │
├─────────────────────────────────┤
│ SAFETY CHECKS                   │
│ ├─ Obstacle Too Close?          │
│ ├─ Joint Torque Exceeded?       │
│ ├─ Gripper Force High?          │
│ ├─ Temperature Warning?         │
│ └─ Battery Low?                 │
├─────────────────────────────────┤
│ ACTIONS                         │
│ ├─ Emergency Stop               │
│ ├─ Reduce Speed                 │
│ ├─ Alert User                   │
│ └─ Log Event                    │
└─────────────────────────────────┘
```

## Configuration Files

### robot_params.yaml
- Robot dimensions and capabilities
- Bin positions and capacities
- Safety thresholds
- Arm specifications

### nav2_params.yaml
- Navigation parameters
- Costmap configuration
- Path planning settings
- Behavior parameters

### yolo_training_config.yaml
- Model configuration
- Training parameters
- Learning rate schedule
- Data augmentation settings

## Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Waste Detection Accuracy | >90% | TBD |
| Detection Latency | <100ms | TBD |
| Task Completion Time | <5min | TBD |
| Safety Response Time | <100ms | TBD |
| Uptime | >98% | TBD |

## Scalability Considerations

1. **Multi-Robot System**
   - Shared task coordinator
   - Load balancing
   - Collision avoidance

2. **Multiple Bins**
   - Extensible bin manager
   - Dynamic bin registration
   - Bin capacity scaling

3. **Hospital Integration**
   - Web dashboard
   - Mobile app
   - Notification system

## Future Enhancements

1. **AI/ML Improvements**
   - Transfer learning from other datasets
   - On-device learning
   - Federated learning for multiple robots

2. **Hardware Upgrades**
   - Faster gripper
   - Improved sensors
   - Enhanced computing

3. **System Features**
   - Multi-robot coordination
   - Hospital integration APIs
   - Advanced analytics
   - Predictive maintenance
