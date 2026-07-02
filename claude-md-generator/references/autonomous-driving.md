# Autonomous Driving Domain Guide

## Architecture Comparison

### Apollo (Bazel-based)

- **Middleware**: CyberRT -- microsecond latency, deterministic scheduling, custom DDS-like transport
- **Module structure**: `modules/{perception,planning,control,prediction,routing,localization,map}`
- **Build system**: Bazel with `apollo.sh` wrapper script for common operations
- **Safety compliance**: ISO 26262 (ASIL B/C/D), ISO 21448 (SOTIF), UL 4600
- **Key config**: `modules/common/adapters/adapter_config.conf` for topic wiring

### Autoware (ROS2-based)

- **Middleware**: ROS 2 Humble/Iron with DDS (Fast-DDS / Cyclone DDS)
- **Repository split**: `autoware.core` (stable) / `autoware.universe` (experimental)
- **Module packages**: `autoware_core_{sensing,perception,planning,control,localization}`
- **Build system**: colcon with ament_cmake, vcs tool for repo management
- **Key config**: YAML parameter files in each package `config/` directory

### Architectural Decision Table

| Aspect | Apollo | Autoware |
|--------|--------|----------|
| Inter-module comm | CyberRT channels (protobuf) | ROS 2 topics (IDL/msg) |
| Scheduling | CyberRT cooperative scheduling | ROS 2 executor (MultiThreaded) |
| Time management | CyberRT clock, hardware-aware | ROS 2 time, sim clock plugin |
| Recording | CyberRT record file | rosbag 2 |
| Visualization | DreamView web UI | RViz 2 |
| Safety monitor | Guardian module | emergency_handler node |

## Pipeline Stage Documentation Pattern

Each stage in the perception-to-control pipeline should be documented with the following structure:

### Stage Template

```markdown
### {Stage Name}
- **Input topics**: `/topic/name` (MessageType, QoS: RELIABLE/KEEP_LAST 10)
- **Output topics**: `/topic/name` (MessageType, QoS: BEST_EFFORT/KEEP_LAST 1)
- **Algorithm**: {brief description with config file reference}
- **Upstream**: {stage name or module}
- **Downstream**: {stage name or module}
- **Safety constraints**:
  - Hard limit: {value} (violation triggers guardian override)
  - Latency budget: {value} ms
  - Degradation mode: {behavior on timeout}
```

### Perception Stage
- Camera pipeline: YOLO-based detection, DeepSort tracking
- LiDAR pipeline: PointPillars / CenterPoint for detection
- Fusion: Hungarian algorithm + Kalman filter association

### Prediction Stage
- Trajectory prediction: social LSTM / Transformer-based
- Output: probability-weighted trajectory hypotheses
- Time horizon: 5-8 seconds with uncertainty estimates

### Planning Stage
- Path planning: Hybrid A\* / lattice planner
- Speed planning: ST graph optimization
- Behavior planning: finite state machine (LANE_FOLLOW, INTERSECTION, PARKING)

### Control Stage
- Longitudinal: PID + feedforward
- Lateral: MPC (model predictive control) with 10-20 step horizon
- Output: steering angle + acceleration/deceleration commands via CAN

## Simulation Integration

### SIL (Software-in-the-Loop)
- **Carla**: sensor simulation, scenario definition via Python API, traffic manager
- **LGSVL** (deprecated, migration to SVL Simulator): similar capability
- **Scenario configuration**: OpenSCENARIO / OpenDRIVE format
- **Typical launch**: `python scenario_runner.py --scenario {name}`

### Logging Simulator
- Record real drives as rosbag / CyberRT record files
- Replay sensor topics to pipeline modules
- Enable offline tuning without hardware

### HIL (Hardware-in-the-Loop)
- Real ECU with simulated sensor input
- CAN bus simulation (CANoe, vcan)
- Validates real-time performance on target hardware

## Safety Documentation

### Guardian / Safety Monitor
- Independent watchdog process (separate from planning stack)
- Monitors: trajectory validity, steering command rate, braking distance
- Override: if safety envelope breached, Guardian issues direct CAN brake command

### Emergency Stop Sequence
1. Planning timeout (>100ms) -> Guardian brake
2. Steering rate exceeds limit -> Guardian brake
3. Lateral acceleration > 0.4g -> Guardian brake
4. E-Stop button pressed -> immediate brake + disengage

### ISO 26262 ASIL Levels
| System | ASIL | Redundancy |
|--------|------|------------|
| Steering actuation | ASIL B(D) | Dual-wound motor, dual position sensors |
| Braking actuation | ASIL C(D) | Redundant brake lines, independent ECU |
| Perception fusion | ASIL B | Sensor diversity (camera + LiDAR + radar) |
| Planning | ASIL B | Bounded validity checking |

### SOTIF (ISO 21448)
- Known hazardous scenarios documented in HAZOP table
- Functional insufficiency: edge cases not covered by sensor suite
- Validation: scenario coverage metrics, ODD definition
