# Robotics / ROS2 Domain Guide

## ROS2 Workspace Conventions

### Package Naming Pattern
Robotics projects typically split concerns across convention-named packages:

| Suffix | Purpose | Example |
|--------|---------|---------|
| `_description` | URDF/Xacro models, mesh files, visual assets | `myrobot_description` |
| `_bringup` | Launch files, parameter YAMLs, node composition | `myrobot_bringup` |
| `_control` | Controller configuration, joint trajectory controllers | `myrobot_control` |
| `_navigation` | Nav2 configuration, planners, costmap parameters | `myrobot_navigation` |
| `_perception` | Sensor processing pipelines, detection nodes | `myrobot_perception` |
| `_msgs` | Custom message/service/action definitions | `myrobot_msgs` |
| `_simulation` | Gazebo plugins, world files, simulation config | `myrobot_simulation` |

### Build System
- **Build tool**: colcon (`colcon build --symlink-install`)
- **Dependency management**: rosdep for system deps, `.repos` for workspace sources
- **Workspace setup**: `source /opt/ros/{distro}/setup.bash && source install/setup.bash`
- **Test**: `colcon test --packages-select {pkg}`

### Custom Interfaces
- Messages: `.msg` files in `msg/` directory
- Services: `.srv` files in `srv/` directory
- Actions: `.action` files in `action/` directory
- Convention: append `.msg`/`.srv`/`.action` to CMakeLists.txt `rosidl_generate_interfaces()`

## Package Documentation Pattern

Each ROS 2 package CLAUDE.md should document:

### 1. Nodes and Executables
```markdown
### {node_name}
- **Source**: `src/{node_name}.cpp` or `src/{node_name}.py`
- **Entry point**: `<package_name>:<executable_name>` (in setup.py / CMakeLists)
- **Lifecycle**: Managed / Static / Components
- **Purpose**: One-sentence description
```

### 2. Published / Subscribed Topics
```markdown
- **Published**:
  - `/topic/name` (Interfaces/Type) -- QoS: RELIABLE, DEPTH 10 -- {purpose}
- **Subscribed**:
  - `/topic/name` (Interfaces/Type) -- QoS: BEST_EFFORT, DEPTH 1 -- {purpose}
```

QoS selection guidance:
- **Sensor data** (camera, LiDAR, IMU): `BEST_EFFORT` + `KEEP_LAST 1` (drop stale frames)
- **Commands** (velocity, joint targets): `RELIABLE` + `KEEP_LAST 1`
- **Maps / point clouds**: `RELIABLE` + `VOLATILE` durability for large payloads

### 3. Services and Actions
- Service: `{service_name}` (`{pkg}/srv/{File}.srv`) -- {request/response summary}
- Action: `{action_name}` (`{pkg}/action/{File}.action`) -- {goal/feedback/result summary}

### 4. Parameters with Defaults
Document all `declare_parameter()` calls:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | double | 1.0 | Brief description |
| `param_name` | string | `"default"` | Brief description |

### 5. Launch Files
- **`{robot}.launch.py`**: launches full robot stack (drivers, controllers, nav stack)
- **`{robot}.launch.py` args**: `use_sim_time:=true`, `namespace:=robot1`
- **Composition**: use `ComposableNodeContainer` for intra-process comms

## Hardware Abstraction

### Sensor Drivers
- Camera: `camera_info_manager` for calibration, `image_transport` for compression
- LiDAR: point cloud output on `sensor_msgs/PointCloud2`, tf for extrinsics
- IMU: `sensor_msgs/Imu`, bias estimation in calibration node
- Encoder: wheel encoder -> odometry via `robot_localization` or custom EKF

### Actuator Interfaces
| Transport | Common use | ROS 2 integration |
|-----------|-----------|-------------------|
| CAN | Motor controllers, servo drives | `ros2_canopen`, `socketcan` |
| UART | Serial servos, microcontrollers | `serial_driver`, custom nodes |
| EtherCAT | High-speed motion control | `ethercat_manager`, SOEM |

### Real-Time Control Loops
- Use `rclcpp::Executor` with priority scheduling
- Set scheduler policy: `chrt -f 80` for the control process
- Avoid dynamic allocation in control loop: preallocate messages, use real-time-safe allocators
- Monitor loop timing: `rclcpp::WallTimer` for diagnostics

### Motor Enable / Disable Guards
- Require explicit enable sequence before motor power
- E-stop clears enable state via hardware pin
- Software disable on: node crash, topic timeout, limit switch trigger
- Document the enable sequence in the control package CLAUDE.md

## Simulation

### Gazebo Integration (Gazebo Classic / Ignition / Gazebo)
- **World files**: `.sdf` / `.world` in `worlds/` directory
- **Robot models**: URDF with Gazebo plugins (`<gazebo>` tags in URDF)
- **Plugins**: `libgazebo_ros_diff_drive.so`, `libgazebo_ros_camera.so`, etc.
- **Bridge**: `ros_gz_bridge` for topic remapping between ROS 2 and Gazebo

### Isaac Sim Integration
- URDF import via Isaac Sim's URDF Importer
- ROS 2 bridge via `isaac_ros_common` and `isaac_ros_navigation`
- Synthetic data generation for perception training

### URDF / Xacro
- Xacro macros for parameterized robot descriptions
- `robot_state_publisher` for tf tree broadcast
- `joint_state_publisher` (GUI variant for manual testing)
- Convention: one `.xacro` per subsystem (arm, base, head), top-level robot xacro includes them
