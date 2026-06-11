# Medical Waste Management Humanoid Robot using ROS2

A comprehensive ROS2-based system for autonomous medical waste management using a humanoid robot platform. This project implements perception, manipulation, navigation, and task coordination for safe handling of medical waste in hospital environments.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [ROS2 Packages](#ros2-packages)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

This project develops an autonomous humanoid robot system for medical waste management in hospitals. The robot is capable of:

- **Autonomous Collection**: Collecting medical waste from patient rooms and operation theaters
- **Waste Classification**: Sorting and categorizing waste (general, infectious, sharps, recyclable)
- **Safe Transport**: Transporting waste to designated disposal points
- **Disinfection**: Performing surface disinfection procedures
- **Human-Robot Interaction**: Safe interaction with hospital staff

The system is built on **ROS2** for distributed, real-time, and robust robotic operations.

## 🏗️ System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│          Medical Waste Management Robot              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  Perception  │  │  Navigation  │                │
│  │   (Vision)   │  │  (Nav2/SLAM) │                │
│  └──────────────┘  └──────────────┘                │
│         │                  │                        │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Manipulation │  │ Task Manager │                │
│  │ (MoveIt2)    │  │              │                │
│  └──────────────┘  └──────────────┘                │
│         │                  │                        │
│  ┌──────────────────────────────────┐              │
│  │   Safety & Emergency Systems     │              │
│  └──────────────────────────────────┘              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Subsystems

1. **Perception System**: Camera-based waste detection and classification
2. **Navigation System**: Autonomous movement in hospital spaces
3. **Manipulation System**: Robotic arm and gripper control
4. **Task Coordination**: Task scheduling and execution
5. **Safety System**: Emergency stops and obstacle detection

## ✨ Features

- ✅ Autonomous navigation in hospital environments
- ✅ Real-time object detection and waste classification
- ✅ Robotic arm manipulation with MoveIt2
- ✅ SLAM-based localization and mapping
- ✅ Task scheduling and priority management
- ✅ Safety protocols and emergency stops
- ✅ Human-robot interaction interface
- ✅ Gazebo simulation environment
- ✅ Comprehensive logging and monitoring
- ✅ Hospital compliance and hygiene standards

## 💾 Hardware Requirements

### Recommended Humanoid Platform
- **TIAGo** (PAL Robotics) - Mobile manipulator with ROS support
- **Pepper** - Social humanoid robot
- **Custom platform** - Based on your requirements

### Sensors
- RGB-D Camera (Intel RealSense D435/D455)
- 2D LiDAR (SICK TIM series)
- Force-Torque sensor (wrist-mounted)
- IMU (Inertial Measurement Unit)
- Bumpers/Safety sensors

### Actuators
- 6-DOF Robotic arm with gripper
- Mobile base with differential drive
- Gripper with force feedback

### Computing
- Industrial PC or edge computing device (Intel NUC, NVIDIA Jetson)
- Minimum: 16GB RAM, 8-core processor
- GPU recommended for vision processing

## 📦 Software Requirements

- **OS**: Ubuntu 20.04/22.04 LTS
- **ROS2 Distribution**: Humble / Iron / Jazzy
- **Python**: 3.10+
- **C++**: C++17 or later
- **Build System**: Colcon

### Key Dependencies
```bash
ros-{distro}-nav2
ros-{distro}-moveit2
ros-{distro}-slam-toolbox
ros-{distro}-opencv
ros-{distro}-pcl
ros-{distro}-gazebo
```

## 🚀 Installation

### Prerequisites
```bash
sudo apt update
sudo apt upgrade -y
```

### Install ROS2
Follow the [official ROS2 installation guide](https://docs.ros.org/en/humble/Installation.html)

### Clone the Repository
```bash
mkdir -p ~/medical_waste_ws/src
cd ~/medical_waste_ws/src
git clone https://github.com/sindhu-krish/Medical-waste-management-Robot-.git .
```

### Install Dependencies
```bash
cd ~/medical_waste_ws
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### Build the Project
```bash
cd ~/medical_waste_ws
colcon build --symlink-install
```

### Source the Environment
```bash
source ~/medical_waste_ws/install/setup.bash
```

## 📁 Project Structure

```
Medical-waste-management-Robot-/
├── README.md
├── LICENSE
├── package.xml
├── setup.py
│
├── src/
│   ├── perception/
│   │   ├── waste_detector_node.py
│   │   ├── waste_classifier_node.py
│   │   └── camera_driver_node.py
│   │
│   ├── navigation/
│   │   ├── nav_config.yaml
│   │   ├── mapper_node.py
│   │   └── path_planner_node.py
│   │
│   ├── manipulation/
│   │   ├── arm_controller_node.py
│   │   ├── gripper_controller_node.py
│   │   └── moveit_config/
│   │
│   ├── task_manager/
│   │   ├── task_coordinator_node.py
│   │   ├── task_scheduler_node.py
│   │   └── waste_collection_node.py
│   │
│   └── safety/
│       ├── emergency_stop_node.py
│       ├── obstacle_detection_node.py
│       └── safety_monitor_node.py
│
├── launch/
│   ├── robot_bringup.launch.py
│   ├── navigation.launch.py
│   ├── manipulation.launch.py
│   └── full_system.launch.py
│
├── config/
│   ├── robot_params.yaml
│   ├── nav2_params.yaml
│   ├── moveit_config.yaml
│   └── waste_classification.yaml
│
├── simulation/
│   ├── gazebo_world/
│   ├── robot_description.urdf
│   └── sim_launcher.launch.py
│
├── tests/
│   ├── test_perception.py
│   ├── test_navigation.py
│   └── test_manipulation.py
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    ├── SETUP_GUIDE.md
    └── TROUBLESHOOTING.md
```

## 🎮 Usage

### Launch the Full System
```bash
ros2 launch medical_waste_robot full_system.launch.py
```

### Launch Specific Subsystems

**Navigation Only:**
```bash
ros2 launch medical_waste_robot navigation.launch.py
```

**Manipulation Only:**
```bash
ros2 launch medical_waste_robot manipulation.launch.py
```

**Simulation:**
```bash
ros2 launch medical_waste_robot sim_launcher.launch.py
```

### Example: Autonomous Waste Collection
```bash
ros2 service call /waste_collection_service medical_waste_robot/CollectWaste "{location: 'room_101'}"
```

### Monitor System Status
```bash
ros2 topic echo /robot/status
ros2 topic echo /waste/classification
```

## 📦 ROS2 Packages

### Custom Packages

1. **medical_waste_perception**
   - Waste detection and classification
   - Camera integration

2. **medical_waste_navigation**
   - Path planning and obstacle avoidance
   - SLAM and localization

3. **medical_waste_manipulation**
   - Arm and gripper control
   - Trajectory planning

4. **medical_waste_task_manager**
   - Task coordination and scheduling
   - State machine management

5. **medical_waste_safety**
   - Safety protocols
   - Emergency handling

### External Packages
- `nav2` - Navigation framework
- `moveit2` - Motion planning
- `slam_toolbox` - SLAM implementation
- `gazebo_ros` - Simulation

## ⚙️ Configuration

### Robot Parameters (`config/robot_params.yaml`)
```yaml
robot:
  name: "medical_waste_robot"
  type: "humanoid"
  max_speed: 1.5  # m/s
  max_angular_velocity: 1.0  # rad/s
  
arm:
  dof: 6
  max_reach: 1.2  # meters
  gripper_force: 100  # N

safety:
  min_obstacle_distance: 0.3  # meters
  emergency_stop_enabled: true
```

## 🧪 Testing

Run unit tests:
```bash
colcon test
```

Run specific test:
```bash
colcon test --packages-select medical_waste_robot
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed system architecture
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - ROS2 API documentation
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Complete setup instructions
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ROS2 naming conventions
- Include docstrings and comments
- Add tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Sindhu Krish** - Initial project development

## 🙏 Acknowledgments

- PAL Robotics for TIAGo platform
- ROS2 community and contributors
- Hospital partners for use case input
- OpenSource robotics projects

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/sindhu-krish/Medical-waste-management-Robot-/issues)
- Start a [Discussion](https://github.com/sindhu-krish/Medical-waste-management-Robot-/discussions)
- Contact: sindhu-krish@example.com

## 🗺️ Roadmap

- [ ] Phase 1: Core perception and navigation (Q1 2024)
- [ ] Phase 2: Manipulation system implementation (Q2 2024)
- [ ] Phase 3: Task coordination and scheduling (Q3 2024)
- [ ] Phase 4: Hospital deployment and testing (Q4 2024)
- [ ] Phase 5: AI-based waste classification optimization (2025)

---

**Last Updated**: June 2026  
**Status**: Active Development
