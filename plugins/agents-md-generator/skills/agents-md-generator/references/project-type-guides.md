# Project Type Detection and Generation Guides

## Python

**Detection checklist**: `setup.py`, `pyproject.toml`, `requirements.txt`, `Pipfile`, `conda.yml`, `.py` files in root or `src/`.

**Typical directory structure**:
```
src/{package}/           -- application or library code
tests/                    -- pytest suite
docs/                     -- Sphinx or MkDocs
scripts/                  -- utility scripts
notebooks/                -- Jupyter notebooks (research projects)
```

**Common conventions**: `src/` layout for packages, pytest for testing, `__init__.py` re-exports, `if __name__ == "__main__"` guard.

**Example AGENTS.md snippet**:
```markdown
## Commands
# Run all tests
pytest

# Run single test file
pytest tests/test_{module}.py -v

# Lint
ruff check src/

## Environment
- Python 3.11+, managed via conda env `myproject`
- CUDA 12.1 required for GPU training
```

**Anti-patterns**: Listing every pip dependency; documenting PEP 8 (not project-specific); writing the README into AGENTS.md instead of using `@README.md`.

---

## Node-Web

**Detection checklist**: `package.json` with `react`, `vue`, `next`, `nuxt`, `express`, `fastify`; `tsconfig.json`; `vite.config.ts` or `webpack.config.js`.

**Typical directory structure**:
```
src/
  components/        -- shared UI components
  pages/             -- route-level components
  hooks/             -- custom React hooks
  api/               -- API client functions
  stores/            -- state management
  types/             -- TypeScript type definitions
public/               -- static assets
```

**Common conventions**: Barrel exports from `index.ts`, absolute imports with `@/` alias, colocated CSS modules or Tailwind, Prettier + ESLint.

**Example AGENTS.md snippet**:
```markdown
## Architecture
1. `src/components/` -- shared UI (shadcn/ui primitives)
2. `src/pages/` -- route components (TanStack Router)
3. `src/api/` -- TanStack Query hooks + fetch layer
4. `src/stores/` -- Zustand stores for client state

## Entry Points
`index.html` -> `src/main.tsx` -> `<App/>`
```

**Anti-patterns**: Documenting `useState` or basic React patterns; listing axios/lodash (they don't shape architecture); including `node_modules` or build output in the directory map.

---

## Rust

**Detection checklist**: `Cargo.toml`, `rust-toolchain.toml`, `build.rs`, `.rs` files in `src/`.

**Typical directory structure**:
```
src/
  main.rs            -- binary entry point
  lib.rs             -- library root
  {module}/          -- feature modules
tests/                -- integration tests
benches/              -- criterion benchmarks
examples/             -- usage examples
```

**Common conventions**: Clippy for linting, `rustfmt` for formatting, feature flags in `Cargo.toml`, `Result` return types, `thiserror`/`anyhow` for error handling.

**Example AGENTS.md snippet**:
```markdown
## Environment
- Rust edition 2021, toolchain stable
- Features: `serde`, `tokio`, `clap` (CLI)
- Default features exclude `tracing` (use `--features tracing` for debug)

## Commands
cargo build
cargo test
cargo clippy -- -D warnings
cargo fmt
```

**Anti-patterns**: Listing every crate in Cargo.toml; documenting `impl` syntax; including `target/` references.

---

## Java

**Detection checklist**: `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `src/main/java/` or `src/main/kotlin/`.

**Typical directory structure**:
```
src/
  main/
    java/{group}/{project}/
      controller/    -- REST endpoints
      service/       -- business logic
      repository/    -- data access
      model/         -- JPA entities / DTOs
      config/        -- Spring/Boot configuration
    resources/
      application.yml / application.properties
  test/
    java/
```

**Common conventions**: Spring Boot or Quarkus for web services, Lombok for boilerplate reduction, SLF4J + Logback, Maven wrapper or Gradle wrapper.

**Example AGENTS.md snippet**:
```markdown
## Architecture
HTTP -> controller/ (validation) -> service/ (business logic) -> repository/ (JPA) -> PostgreSQL

## Commands
./mvnw spring-boot:run
./mvnw test -Dtest={TestClassName}
./mvnw verify

## Entry Points
`src/main/java/{group}/{project}/Application.java` -- @SpringBootApplication
```

**Anti-patterns**: Documenting standard Java naming conventions; listing all `@Bean` definitions; including IDE config files.

---

## Go

**Detection checklist**: `go.mod`, `go.sum`, `main.go` or `cmd/` directory.

**Typical directory structure**:
```
cmd/{app}/main.go     -- binary entry point
internal/
  handler/             -- HTTP handlers
  service/             -- business logic
  repository/          -- data access
pkg/                   -- shared library code
migrations/            -- database migrations
```

**Common conventions**: `cmd/` pattern for binaries, `internal/` for private packages, `errgroup` for goroutine orchestration, `slog` or `logrus` for logging.

**Example AGENTS.md snippet**:
```markdown
## Architecture
HTTP (chi router) -> handler/ -> service/ -> repository/ -> PostgreSQL

## Commands
go run ./cmd/server
go test ./...
go test ./internal/handler/ -run TestCreateUser
go vet ./...
```

**Anti-patterns**: Documenting `defer`, `goroutine`, or `interface{}` basics; including `vendor/` in directory map; listing every indirect dependency.

---

## Infra

**Detection checklist**: `Dockerfile`, `docker-compose.yml`, `terraform/`, `ansible/`, `helm/`, `kustomize/`, `*.yaml` with Kubernetes resources.

**Typical directory structure**:
```
terraform/
  modules/             -- reusable modules
  environments/
    staging/
    production/
ansible/
  playbooks/
  roles/
helm/
  charts/
docker/
  Dockerfile
  docker-compose.yml
```

**Common conventions**: Infrastructure as code, environment separation (staging/production), secrets management via vault or external provider, immutable infrastructure patterns.

**Example AGENTS.md snippet**:
```markdown
## Safety Rules
- Terraform state stored in S3 with DynamoDB locking
- Production apply requires signed-off PR and CI approval
- Never commit .tfvars with secrets -- use Vault references

## Environment
- Terraform 1.5+, AWS provider 5.x
- kubectl context: staging (dev), production (restricted)

## Commands
terraform plan -var-file=environments/staging.tfvars
terraform apply -var-file=environments/production.tfvars
kubectl get pods -n {namespace}
```

**Anti-patterns**: Documenting basic Terraform syntax; committing `terraform.tfstate`; missing safety constraints (this is the highest-leverage section for infra).

---

## AutoDriving

**Detection checklist**: Perception/planning/control module directories, `modules/` or `autoware_*` packages, `CyberRT` or `ROS 2` middleware config files.

**Typical directory structure**:
```
modules/
  perception/          -- camera, LiDAR, radar pipelines
  prediction/          -- trajectory prediction
  planning/            -- path/motion planning
  control/             -- steering/throttle/brake
  localization/        -- GNSS+IMU fusion
  mapping/             -- HD map management
```

**Common conventions**: Pipeline-based architecture, deterministic replay for debugging, simulation-first testing, ISO 26262 documentation artifacts.

**Example AGENTS.md snippet**:
```markdown
## Pipeline Overview
1. perception/ (Camera YOLO -> LiDAR PointPillars) -> fusion
2. prediction/ (social LSTM) -> trajectory hypotheses
3. planning/ (Hybrid A*) -> trajectory
4. control/ (PID + MPC) -> CAN commands

## Middleware
CyberRT topics: `/perception/obstacles`, `/planning/trajectory`, `/control/commands`

## Safety Rules
- Planning outputs validated against hard braking/jerk limits
- Guardian module overrides control if safety envelope exceeded
- ASIL B(D) for steering, ASIL C(D) for braking
```

**Anti-patterns**: Not documenting topic/message types; skipping safety documentation; listing every config parameter.

---

## Robotics

**Detection checklist**: `ROS` or `ROS 2` workspace, `colcon` or `catkin`, `.urdf` or `.xacro` files, `rosdep`, `.repos` files.

**Typical directory structure**:
```
src/
  {robot}_description/    -- URDF/Xacro models
  {robot}_bringup/        -- launch files
  {robot}_control/        -- controllers
  {robot}_navigation/     -- nav2 configuration
  {robot}_perception/     -- sensor processing
  {robot}_msgs/           -- custom message definitions
```

**Common conventions**: Namespace-based topic organization, lifecycle nodes for deterministic startup, QoS profiles for sensor data, hardware drivers as standalone nodes.

**Example AGENTS.md snippet**:
```markdown
## Architecture
sensor drivers (camera/LiDAR/IMU) -> perception stack -> nav2 -> control node -> motor driver

## Middleware
ROS 2 Humble, DDS (Fast-DDS)
Key topics: /camera/image_raw (sensor_data), /scan (sensor_data), /cmd_vel (geometry_msgs)

## Code Separation
- `_control` packages: real-time critical, C++ only
- `_perception` packages: Python prototyping OK, C++ for deployment
- `_simulation` packages: Gazebo plugins, not deployed on robot
```

**Anti-patterns**: Including ROS tutorial-level content; documenting every topic in the system; skipping hardware abstraction layer docs.

---

## Embedded

**Detection checklist**: `Makefile` or `CMakeLists.txt` with cross-compilation, linker scripts (`.ld` or `.lds`), `FreeRTOSConfig.h`, `prj.conf` (Zephyr), `platformio.ini`, MCU vendor SDK files.

**Typical directory structure**:
```
src/
  app/                 -- application logic
  drivers/             -- peripheral drivers
  hal/                 -- hardware abstraction layer
  os/                  -- RTOS configuration
  startup/             -- vector table, reset handler
ldscripts/             -- linker scripts
tests/
  unit/                -- host-compiled tests
  hw/                  -- hardware-in-the-loop tests
```

**Common conventions**: MISRA-C compliance, interrupt-driven I/O, DMA for high-throughput, static memory allocation (no malloc in control path), watchdog timers.

**Example AGENTS.md snippet**:
```markdown
## CPS Layer Map
Application (control loop) -> FreeRTOS (task scheduler) -> HAL (GPIO/SPI/I2C) -> STM32G474

## Target Hardware
- MCU: STM32G474RET6, ARM Cortex-M4, 170 MHz
- Flash: 512 KB, RAM: 128 KB
- Peripherals: 3x SPI, 2x I2C, 2x CAN-FD, 4x ADC

## Safety Rules
- MISRA-C:2012 mandatory (deviation process required)
- No malloc/free in control tasks
- Stack depth analysis verified per task
- Watchdog timeout: 100 ms (ISR feeds only)
```

**Anti-patterns**: Omitting linker script details; not documenting ISR latency requirements; missing cross-compilation toolchain path; skipping boot sequence documentation.

---

## Generic

**Detection checklist**: No strong match for any of the above 9 types. Falls into catch-all for polyglot repos, documentation projects, or unusual stacks.

**Typical directory structure**: Varies wildly. Rely on the README bridge and directory structure scanning.

**Common conventions**: None universal. Default to language-agnostic sections: Commands, Architecture, Environment, Data/DB, Auth, Caveats.

**Example AGENTS.md snippet**:
```markdown
## Commands
make build          # compile everything
make test           # run all tests
make clean          # remove build artifacts

## Architecture
(Describe at a high level -- use @README.md as starting point)

## Data / DB
- SQLite at `data/project.db`
- Schema migrations in `migrations/`
```

**Anti-patterns**: Over-documenting trivial Makefile commands; skipping Architecture section ("it's a small project"); including every section from the template.
