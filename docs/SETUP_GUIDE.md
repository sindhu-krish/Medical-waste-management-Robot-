# Medical Waste Management Robot - Setup Guide

## Prerequisites

- Ubuntu 20.04 LTS or 22.04 LTS
- ROS2 Humble or later
- NVIDIA GPU (recommended for YOLO inference)
- 16GB RAM minimum
- 50GB free disk space

## Step 1: Install ROS2

### Install ROS2 Humble on Ubuntu 22.04

```bash
# Set locale
locale  # check for UTF-8

# Install software-properties-common
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe

# Add ROS2 GPG key
sudo curl -sSL https://raw.githubusercontent.com/ros/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS2 repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update and install ROS2
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop

# Source setup script
source /opt/ros/humble/setup.bash

# Add to bashrc for automatic sourcing
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

## Step 2: Set Up Workspace

```bash
# Create workspace
mkdir -p ~/medical_waste_ws/src
cd ~/medical_waste_ws

# Clone repository
cd src
git clone https://github.com/sindhu-krish/Medical-waste-management-Robot-.git .

# Install rosdep
sudo apt install python3-rosdep
sudo rosdep init
rosdep update

# Install dependencies
cd ~/medical_waste_ws
rosdep install --from-paths src --ignore-src -r -y
```

## Step 3: Install Python Dependencies

```bash
# Navigate to workspace
cd ~/medical_waste_ws

# Install requirements
pip install -r requirements.txt

# Verify installations
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')"
python3 -c "import ultralytics; print(f'Ultralytics: {ultralytics.__version__}')"
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
```

## Step 4: Build the Project

```bash
# Navigate to workspace
cd ~/medical_waste_ws

# Build with colcon
colcon build --symlink-install

# Source workspace
source install/setup.bash

# Add to bashrc for automatic sourcing
echo "source ~/medical_waste_ws/install/setup.bash" >> ~/.bashrc
```

## Step 5: Prepare Dataset

```bash
# Navigate to workspace
cd ~/medical_waste_ws

# Prepare dataset structure
python3 scripts/prepare_dataset.py --dataset-root ./waste_detection_dataset

# Output: Dataset structure ready at ./waste_detection_dataset
```

## Step 6: Train YOLO Model (Optional)

```bash
# Create default training config
python3 scripts/train_yolo.py --create-config --config config/yolo_training_config.yaml

# Start training (requires collected dataset)
python3 scripts/train_yolo.py --train --config config/yolo_training_config.yaml

# Training will save model to ./models/waste_detector_final.pt
```

## Step 7: Verify Installation

```bash
# Run tests
cd ~/medical_waste_ws
python3 tests/test_system.py

# Expected output: OK (all tests pass)
```

## Step 8: Configure Hardware

### Camera Setup (Intel RealSense)

```bash
# Install RealSense SDK
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6B6D786A
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key D6FB2970

sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u
sudo apt install librealsense2-dkms librealsense2-utils

# Install ROS2 wrapper
sudo apt install ros-humble-realsense2-camera
```

### LiDAR Setup (SICK TIM)

```bash
# Install LiDAR driver
sudo apt install ros-humble-sick-tim

# Test connection
ls -la /dev/ttyUSB*  # Check USB connection
```

### Configure Serial Ports

```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# Logout and login for changes to take effect
```

## Step 9: Launch System

```bash
# Terminal 1: Start ROS2 core (optional, auto-started by launch)
ros2 launch medical_waste_robot full_system.launch.py

# Terminal 2: Monitor system (optional)
ros2 launch medical_waste_robot perception.launch.py

# Terminal 3: Check topics
ros2 topic list

# Terminal 4: View waste detection
ros2 topic echo /waste_detection/classification
```

## Step 10: Configuration

### Edit Robot Parameters

```bash
# Open robot configuration
nano ~/medical_waste_ws/src/config/robot_params.yaml

# Key parameters to configure:
# - robot_name
# - max_speed
# - bin_positions
# - safety thresholds
```

### Edit Navigation Parameters

```bash
# Open Nav2 configuration
nano ~/medical_waste_ws/src/config/nav2_params.yaml

# Key parameters:
# - map_name
# - navigation_frame
# - costmap_size
```

## Troubleshooting

### Build Errors

```bash
# Clean build
cd ~/medical_waste_ws
rm -rf build install log
colcon build --symlink-install
```

### Missing Dependencies

```bash
# Reinstall rosdep
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### Camera Not Detected

```bash
# Check USB connection
lsusb

# Check RealSense
rs-enumerate-devices
```

### ROS2 Topic Issues

```bash
# Check if master is running
ros2 daemon status

# List all topics
ros2 topic list

# Echo specific topic
ros2 topic echo /topic_name
```

## Performance Tuning

### GPU Acceleration

```bash
# Check GPU availability
python3 -c "import torch; print(torch.cuda.is_available())"

# Enable GPU for YOLO
# Edit yolo_waste_detector.py and set device=0
```

### CPU Optimization

```bash
# Set CPU affinity for better performance
echo "kernel.sched_autogroup_task_new = 0" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Memory Management

```bash
# Monitor memory usage
htop

# Reduce batch size if out of memory
# Edit train_yolo.py: batch_size parameter
```

## Testing

```bash
# Run all tests
python3 tests/test_system.py

# Run specific test
python3 -m unittest tests.test_system.TestYOLODetector

# Test with coverage
pip install coverage
coverage run -m unittest tests.test_system
coverage report
```

## Next Steps

1. Collect medical waste dataset (1000+ images per class)
2. Annotate dataset using Labelimg or Roboflow
3. Train YOLO model: `python3 scripts/train_yolo.py --train`
4. Deploy model: Copy to `./models/waste_detector.pt`
5. Run full system: `ros2 launch medical_waste_robot full_system.launch.py`
6. Monitor with: `ros2 topic echo /bin_management/status`

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [API_REFERENCE.md](API_REFERENCE.md)
- Create GitHub issue: https://github.com/sindhu-krish/Medical-waste-management-Robot-/issues
