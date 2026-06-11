# Medical Waste Management Robot - API Reference

## ROS2 Topics

### Perception Topics

#### `/camera/rgb/image_raw`
**Type**: `sensor_msgs/Image`  
**Direction**: Published by camera driver  
**Frequency**: 30 Hz  
**Description**: Raw RGB image from camera

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()
frame = bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
```

#### `/waste_detection/classification`
**Type**: `std_msgs/String`  
**Direction**: Published by YOLO detector  
**Frequency**: ~10 Hz  
**Description**: Waste classification result

**Message Format**:
```json
{
  "waste_type": "infectious_waste",
  "bin": "bin_2",
  "confidence": 0.95
}
```

**Example Subscriber**:
```python
def callback(msg):
    data = json.loads(msg.data)
    print(f"Waste: {data['waste_type']}, Bin: {data['bin']}")

rospy.Subscriber('/waste_detection/classification', String, callback)
```

#### `/waste_detection/target_pose`
**Type**: `geometry_msgs/Pose`  
**Direction**: Published by YOLO detector  
**Frequency**: ~10 Hz  
**Description**: 3D pose of detected waste

**Message Fields**:
```python
pose.position.x  # meters
pose.position.y  # meters
pose.position.z  # meters
pose.orientation.x  # quaternion
pose.orientation.y
pose.orientation.z
pose.orientation.w
```

### Task Management Topics

#### `/task_coordinator/status`
**Type**: `std_msgs/String`  
**Direction**: Published by task coordinator  
**Frequency**: 5 Hz  
**Description**: Current task status

**Message Format**:
```json
{
  "active_task": {
    "task_id": "abc-123-def",
    "type": "collect_waste",
    "state": "executing",
    "priority": 3
  },
  "queue_length": 5,
  "completed_count": 12,
  "failed_count": 0
}
```

#### `/task_coordinator/queue_status`
**Type**: `std_msgs/String`  
**Direction**: Published by task coordinator  
**Frequency**: 5 Hz  
**Description**: Task queue information

### Manipulation Topics

#### `/bin_management/status`
**Type**: `std_msgs/String`  
**Direction**: Published by bin manager  
**Frequency**: 2 Hz  
**Description**: Current bin status and fill levels

**Message Format**:
```json
{
  "bin_1": {
    "name": "General Waste",
    "fill_percentage": 45.5,
    "capacity_liters": 100,
    "waste_count": 23,
    "status": "operational"
  },
  "bin_2": {
    "name": "Infectious Waste",
    "fill_percentage": 78.2,
    "capacity_liters": 80,
    "waste_count": 45,
    "status": "operational"
  },
  "bin_3": {
    "name": "Sharps/Hazardous",
    "fill_percentage": 92.0,
    "capacity_liters": 50,
    "waste_count": 68,
    "status": "full"
  }
}
```

#### `/bin_management/target_bin`
**Type**: `std_msgs/String`  
**Direction**: Published by bin manager  
**Frequency**: Event-based  
**Description**: Target bin assignment for arm controller

#### `/arm_controller/status`
**Type**: `std_msgs/String`  
**Direction**: Published by arm controller  
**Frequency**: 10 Hz  
**Description**: Arm controller state

**Message Format**:
```json
{
  "state": "idle",
  "ready": true,
  "message": "Waiting for waste classification",
  "current_position": "home"
}
```

### Safety Topics

#### `/safety_monitor/status`
**Type**: `std_msgs/String`  
**Direction**: Published by safety monitor  
**Frequency**: 10 Hz  
**Description**: Safety system status

**Message Format**:
```json
{
  "state": "normal",
  "emergency_triggered": false,
  "closest_obstacle": 1.5,
  "collision_detection": true,
  "force_monitoring": true
}
```

**States**: `normal`, `warning`, `emergency`

#### `/safety_monitor/emergency_stop`
**Type**: `std_msgs/Bool`  
**Direction**: Published by safety monitor  
**Frequency**: Event-based  
**Description**: Emergency stop signal

#### `/safety_monitor/obstacle_alert`
**Type**: `std_msgs/String`  
**Direction**: Published by safety monitor  
**Frequency**: Event-based  
**Description**: Obstacle detection alert

## ROS2 Services

### Safety Services

#### `/safety_monitor/emergency_stop`
**Type**: `std_srvs/SetBool`  
**Description**: Trigger or reset emergency stop

**Usage**:
```python
from std_srvs.srv import SetBool

client = node.create_client(SetBool, '/safety_monitor/emergency_stop')
request = SetBool.Request()
request.data = True  # Trigger emergency stop
response = client.call(request)
```

#### `/safety_monitor/reset`
**Type**: `std_srvs/Trigger`  
**Description**: Reset safety system after emergency

**Usage**:
```python
from std_srvs.srv import Trigger

client = node.create_client(Trigger, '/safety_monitor/reset')
response = client.call(Trigger.Request())
```

### Bin Management Services

#### `/bin_management/empty_bin`
**Type**: `std_srvs/SetBool`  
**Description**: Empty a specific bin

## Python API Examples

### Subscribe to Waste Detection

```python
import rclpy
from std_msgs.msg import String
import json

def waste_callback(msg):
    try:
        data = json.loads(msg.data)
        waste_type = data['waste_type']
        target_bin = data['bin']
        confidence = float(data['confidence'])
        
        print(f"Detected: {waste_type}")
        print(f"Target Bin: {target_bin}")
        print(f"Confidence: {confidence:.2f}")
    except Exception as e:
        print(f"Error: {e}")

node = rclpy.create_node('waste_monitor')
subscriber = node.create_subscription(
    String,
    '/waste_detection/classification',
    waste_callback,
    10
)
rclpy.spin(node)
```

### Monitor Bin Status

```python
import rclpy
from std_msgs.msg import String
import json

def bin_callback(msg):
    data = json.loads(msg.data)
    
    for bin_id, info in data.items():
        fill = info['fill_percentage']
        status = info['status']
        print(f"{info['name']}: {fill:.1f}% ({status})")

node = rclpy.create_node('bin_monitor')
subscriber = node.create_subscription(
    String,
    '/bin_management/status',
    bin_callback,
    10
)
rclpy.spin(node)
```

### Call Emergency Stop Service

```python
import rclpy
from std_srvs.srv import SetBool

async def trigger_emergency_stop():
    node = rclpy.create_node('emergency_handler')
    client = node.create_client(SetBool, '/safety_monitor/emergency_stop')
    
    request = SetBool.Request()
    request.data = True
    
    response = await client.call_async(request)
    print(f"Emergency Stop: {response.success}")
    print(f"Message: {response.message}")

rclpy.spin(trigger_emergency_stop())
```

## Command Line Tools

### List Topics
```bash
ros2 topic list
```

### Echo Topic
```bash
ros2 topic echo /waste_detection/classification
```

### Check Topic Type
```bash
ros2 topic type /waste_detection/classification
```

### Get Topic Info
```bash
ros2 topic info /waste_detection/classification
```

### List Services
```bash
ros2 service list
```

### Call Service
```bash
ros2 service call /safety_monitor/emergency_stop std_srvs/srv/SetBool "data: true"
```

## Performance Benchmarks

| Component | Latency | Frequency |
|-----------|---------|----------|
| YOLO Detection | 50-100ms | 10 Hz |
| Task Assignment | <10ms | Event-based |
| Arm Movement | 2-5 seconds | Varies |
| Safety Check | <10ms | 100 Hz |
| Bin Status | <5ms | 2 Hz |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1 | Detection Failed | Retry |
| 2 | Arm Error | Reset & Retry |
| 3 | Safety Violation | Emergency Stop |
| 4 | Bin Full | Empty Bin |
| 5 | Task Timeout | Abort Task |

## Rate Limiting

- Image processing: 10 Hz max
- Task assignment: Event-based
- Safety monitoring: 100 Hz
- Status publishing: 2-10 Hz

## Version Info

- ROS2: Humble or later
- Python: 3.10+
- YOLO: v8
- PyTorch: 1.13+
