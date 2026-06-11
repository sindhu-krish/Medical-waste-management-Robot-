# Medical Waste Management Robot - Troubleshooting Guide

## Common Issues and Solutions

### 1. Build and Installation Issues

#### Error: "Could not find the package specification for 'ros-humble-...'"

**Cause**: ROS2 repository not properly configured

**Solution**:
```bash
# Re-add ROS2 repository
sudo curl -sSL https://raw.githubusercontent.com/ros/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

sudo apt update
sudo apt install ros-humble-desktop
```

#### Error: "ModuleNotFoundError: No module named 'ultralytics'"

**Cause**: YOLO not installed

**Solution**:
```bash
pip install ultralytics>=8.0.0
pip install torch torchvision
```

#### Error: "colcon command not found"

**Cause**: Colcon not installed

**Solution**:
```bash
sudo apt install python3-colcon-common-extensions
```

### 2. Hardware Connection Issues

#### Camera Not Detected

**Symptoms**: Camera topic not publishing

**Diagnosis**:
```bash
# Check USB connection
lsusb | grep Intel

# Check RealSense SDK
rs-enumerate-devices
```

**Solutions**:
```bash
# Reinstall RealSense drivers
sudo apt remove librealsense2-dkms librealsense2-utils
sudo apt install librealsense2-dkms librealsense2-utils

# Reload kernel module
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

#### LiDAR Port Permission Denied

**Error**: "Permission denied to open port '/dev/ttyUSB0'"

**Solution**:
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in
exit

# Or apply immediately
newgrp dialout
```

#### No Serial Port Detected

**Diagnosis**:
```bash
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*
```

**Solutions**:
```bash
# Install brltty (often conflicts with serial)
sudo apt remove brltty

# Restart udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3. ROS2 Communication Issues

#### Topics Not Visible

**Symptom**: `ros2 topic list` shows no topics

**Solution**:
```bash
# Check ROS daemon
ros2 daemon status

# Restart daemon
ros2 daemon stop
ros2 daemon start

# Check environment variables
echo $ROS_DOMAIN_ID
echo $ROS_LOCALHOST_ONLY
```

#### Nodes Not Communicating

**Solution**:
```bash
# Source workspace again
source ~/medical_waste_ws/install/setup.bash

# Check node list
ros2 node list

# Check node info
ros2 node info /node_name

# Set network interface
export ROS_LOCALHOST_ONLY=0  # For network communication
```

#### "Cannot import rclpy" Error

**Solution**:
```bash
# Source ROS2 setup
source /opt/ros/humble/setup.bash

# Or add to bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/medical_waste_ws/install/setup.bash" >> ~/.bashrc
```

### 4. YOLO Detection Issues

#### YOLO Model Not Loading

**Error**: "OSError: Can't find model. Model not found locally and auto-download is disabled"

**Solution**:
```bash
# Download model manually
python3 -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"

# Place custom model
cp your_model.pt ~/medical_waste_ws/models/waste_detector.pt
```

#### Low Detection Confidence

**Symptom**: Detections but with <50% confidence

**Solutions**:
```bash
# Check image quality
# - Ensure good lighting
# - Check camera focus
# - Verify object visibility

# Lower confidence threshold
# Edit yolo_waste_detector.py
confidence_threshold = 0.3  # Instead of 0.5

# Retrain model with more data
python3 scripts/train_yolo.py --train
```

#### GPU Out of Memory

**Error**: "CUDA out of memory"

**Solutions**:
```bash
# Reduce batch size
# Edit train_yolo.py
batch = 8  # Instead of 16

# Reduce image size
imgsz = 416  # Instead of 640

# Use CPU instead
device = 'cpu'  # In config
```

### 5. Safety System Issues

#### Emergency Stop Not Triggering

**Diagnosis**:
```bash
ros2 topic echo /scan  # Check LiDAR data
ros2 topic echo /safety_monitor/status  # Check safety state
```

**Solutions**:
```bash
# Verify LiDAR connection
ros2 launch sick_tim tim.launch.py

# Check safety monitor is running
ros2 node list | grep safety

# Manually trigger
ros2 service call /safety_monitor/emergency_stop std_srvs/srv/SetBool "data: true"
```

#### High False Positives in Obstacle Detection

**Symptom**: Robot stops frequently without obstacles

**Solutions**:
```bash
# Increase obstacle distance threshold
# Edit config/robot_params.yaml
min_obstacle_distance: 0.5  # Instead of 0.3

# Clean LiDAR
# Remove dust/dirt from sensor

# Recalibrate
# Place robot in open space and restart
```

### 6. Arm and Gripper Issues

#### Arm Not Moving

**Diagnosis**:
```bash
ros2 topic echo /arm/joint_states
ros2 topic echo /arm_controller/status
```

**Solutions**:
```bash
# Check arm is powered on
# Verify USB/serial connection

# Reset arm
ros2 service call /arm/reset std_srvs/srv/Trigger

# Check trajectory controller
ros2 topic pub /arm/trajectory_controller/command trajectory_msgs/JointTrajectory \
  "header: {frame_id: 'arm_base'} joint_names: ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7'] points: [{positions: [0, -1.57, 1.57, -1.57, -1.57, 0, 0], time_from_start: {sec: 2}}]"
```

#### Gripper Not Closing

**Solutions**:
```bash
# Check gripper power
# Verify servo connection

# Manual test
ros2 topic pub /gripper/command std_msgs/Float64 'data: 1.0'

# Check gripper limits
# Edit config/robot_params.yaml
open_position: 0.0
close_position: 1.0
```

#### High Gripper Torque Alert

**Symptom**: Force monitoring triggers emergency

**Solutions**:
```bash
# Lower force threshold
# Edit config/robot_params.yaml
max_joint_torque: 120.0  # Instead of 150.0

# Check for obstacles during picking
# Ensure clear workspace
```

### 7. Task Coordination Issues

#### Tasks Not Processing

**Diagnosis**:
```bash
ros2 topic echo /task_coordinator/status
ros2 topic echo /task_coordinator/queue_status
```

**Solutions**:
```bash
# Verify task coordinator running
ros2 node list | grep coordinator

# Check task queue
ros2 topic echo /task_coordinator/queue_status

# Manual task creation
ros2 topic pub /waste_detection/classification std_msgs/String 'data: "waste_type:general_waste,bin:bin_1,confidence:0.9"'
```

#### Task Timeout

**Solutions**:
```bash
# Increase timeout
# Edit config/robot_params.yaml
task_timeout: 600  # Instead of 300

# Check arm is responsive
ros2 topic echo /arm/joint_states
```

### 8. Performance Issues

#### High CPU Usage

**Diagnosis**:
```bash
top -b -n 1 | head -20
```

**Solutions**:
```bash
# Reduce YOLO inference frequency
# Edit perception.launch.py
# Lower frame rate

# Use smaller YOLO model
model_size: 'n'  # nano instead of medium

# Disable unnecessary nodes
```

#### Memory Leak

**Solution**:
```bash
# Monitor memory
watch -n 1 free -m

# Restart nodes
ros2 lifecycle set /yolo_waste_detector shutdown
ros2 lifecycle set /yolo_waste_detector configure
ros2 lifecycle set /yolo_waste_detector activate
```

#### Lag in Topic Delivery

**Solutions**:
```bash
# Check network bandwidth
ibw  # Install: sudo apt install iftop

# Reduce message rate
# Edit node parameters
# Decrease publish frequency

# Check for dropped frames
ros2 topic hz /camera/rgb/image_raw
```

### 9. Sensor Calibration Issues

#### Camera Intrinsics Not Set

**Solution**:
```bash
# Calibrate camera
ros2 run camera_calibration cameracalibrator.py --size 8x6 --square 0.024 image:=/camera/rgb/image_raw camera:=/camera

# Save calibration
# Follow on-screen instructions
```

#### LiDAR Offset

**Solution**:
```bash
# Check transformation
ros2 run tf2_tools view_frames

# View TF tree
ros2 run rqt_tf_tree rqt_tf_tree
```

### 10. Deployment Issues

#### Robot Stuck After Emergency Stop

**Solution**:
```bash
# Reset safety system
ros2 service call /safety_monitor/reset std_srvs/srv/Trigger

# Reset arm
ros2 service call /arm/reset std_srvs/srv/Trigger

# Clear all tasks
ros2 topic pub /task_coordinator/clear_queue std_msgs/Empty '{}'
```

#### System Crash on Startup

**Solutions**:
```bash
# Check for conflicting nodes
ros2 node list
ros2 node kill /node_name

# Start nodes one by one
ros2 run medical_waste_robot yolo_waste_detector.py

# Check logs
cat ~/.ros/log/latest/
```

## Log Files

```bash
# ROS2 logs
cat ~/.ros/log/latest/*.log

# Specific node logs
ros2 run medical_waste_robot yolo_waste_detector.py 2>&1 | tee detector.log
```

## Getting Help

1. **Check Documentation**
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [API_REFERENCE.md](API_REFERENCE.md)
   - [SETUP_GUIDE.md](SETUP_GUIDE.md)

2. **Community Resources**
   - ROS2 Discourse: https://discourse.ros.org
   - YOLO Docs: https://docs.ultralytics.com
   - GitHub Issues: https://github.com/sindhu-krish/Medical-waste-management-Robot-/issues

3. **Debug Commands**
   ```bash
   # Complete system check
   ros2 doctor --report
   
   # Node diagnostics
   ros2 doctor
   ```

## Performance Optimization

### For Real-time Processing
```bash
# Set CPU priority
nice -n -19 ros2 launch medical_waste_robot full_system.launch.py

# Disable frequency scaling
sudo cpupower frequency-set -g performance
```

### For Battery Life
```bash
# Reduce update rates
# Edit launch files
# Lower frequency parameters

# Disable unused sensors
```
