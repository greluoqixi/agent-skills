# CLAUDE.md Template Specification (v2)

## Section Selection by Project Type

| Section | Python | Node-Web | Rust | Java | Go | Infra | AutoDriving | Robotics | Embedded | Generic |
|---------|--------|----------|------|------|----|-------|-------------|----------|----------|---------|
| @README.md bridge | always | always | always | always | always | always | always | always | always | always |
| @AGENTS.md bridge | if exists | if exists | if exists | if exists | if exists | if exists | if exists | if exists | if exists | if exists |
| Commands | always | always | always | always | always | always | always | always | always | always |
| Architecture | always | always | always | always | always | always | always | always | always | always |
| Pipeline overview | -- | -- | -- | -- | -- | -- | required | -- | -- | -- |
| Package/Module map | -- | -- | -- | -- | -- | -- | required | required | -- | -- |
| CPS layer map | -- | -- | -- | -- | -- | -- | -- | -- | required | -- |
| Middleware | -- | -- | -- | -- | -- | -- | required | required | required | -- |
| Target hardware | -- | -- | -- | -- | -- | -- | -- | -- | required | -- |
| Toolchain | -- | -- | -- | -- | -- | -- | if non-std | if cross-comp | required | -- |
| Communication graph | -- | -- | -- | -- | -- | -- | required | if >3 ifaces | if >3 peripherals | -- |
| Sensor/Peripheral map | -- | -- | -- | -- | -- | -- | if sensors | required | required | -- |
| Hardware abstraction | -- | -- | -- | -- | -- | -- | -- | required | required | -- |
| Simulation | -- | -- | -- | -- | -- | -- | if sim dirs | if sim pkgs | if HIL tests | -- |
| Safety rules | -- | -- | -- | -- | -- | always | required | required | required | -- |
| Real-time constraints | -- | -- | -- | -- | -- | -- | required | if control | required | -- |
| Memory map | -- | -- | -- | -- | -- | -- | -- | -- | if linker | -- |
| Code separation | -- | -- | -- | -- | -- | -- | -- | required | -- | -- |
| Entry points | if non-obv | if non-obv | if non-obv | always | if non-obv | N/A | if non-obv | if non-obv | always | if non-obv |
| Code conventions | if non-def | if non-def | if non-def | if non-def | if non-def | always | always | always | always | if non-def |
| Environment | if conda | if non-std | if features | if JDK | if needed | always | always | always | always | if needed |
| Data / DB | if data | if DB deps | skip | skip | skip | skip | -- | -- | -- | if data |
| Auth | skip | if auth | skip | if auth | skip | skip | -- | -- | -- | if auth |
| Hook automation | if hooks | if hooks | if hooks | if hooks | if hooks | if hooks | if hooks | if hooks | if hooks | if hooks |
| Caveats | if gotchas | if gotchas | if gotchas | if gotchas | if gotchas | always | always | always | always | if gotchas |

## Conditional Logic

Sections are controlled by four conditions in priority order:

1. **Project type** -- domain-specific sections turn on or off based on which of the 10 types the project matches. The table above encodes these rules.
2. **File existence** -- `if exists`, `if hooks`, `if sim dirs`, `if sim pkgs`, `if HIL tests` all check the filesystem at generation time. Boolean macros: `HAS_README`, `HAS_AGENTS`, `HAS_HOOKS`, `HAS_SIM_DIRS`, `HAS_SIM_PKGS`, `HAS_HIL_TESTS`.
3. **Content detection** -- `if auth`, `if data`, `if DB deps`, `if sensors`, `if gotchas`, `if features`, `if conda`, `if JDK`, `if needed`, `if non-std`, `if cross-comp`, `if control`, `if linker` require scanning config files or source for relevant patterns. Boolean macros: `HAS_CAVEATS`, `HAS_SAFETY_RULES`, `HAS_REALTIME`.
4. **Non-obviousness** -- `if non-obv` and `if non-def` require human judgment or a heuristic. A command is non-obvious if it cannot be inferred from `package.json`, `pyproject.toml`, `Cargo.toml`, or similar build files.

Sections evaluating to empty are omitted entirely from the final CLAUDE.md.

## Content Quality Rules

### The Delete Test
For every line you write, ask: "If I delete this line, would Claude make a mistake?" If the answer is no, delete it.

### Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Copy the README | Reference @README.md |
| List all 50 dependencies | List the 3-5 that shape architecture |
| "Write clean code" | Nothing -- Claude already does this |
| "Use 4-space indent" | Configure a linter hook |
| Alphabetical file lists | Group by importance and relationship |
| Vague descriptions ("utility functions") | Specific descriptions ("date formatting and timezone conversion") |

### Per-Type Example Outputs

**Python**: Standard Python project shows Commands (pytest, ruff, mypy), Architecture (layered services/repositories), Environment (conda env, Python 3.11), Code conventions (if any non-PEP8).

**Node-Web**: Commands (npm test, npm run dev, npx vitest), Architecture (components/pages/hooks/stores), Entry points (index.html -> main.tsx), Environment (Node 20, nvm).

**AutoDriving**: Pipeline overview (perception -> prediction -> planning -> control), Middleware (CyberRT/ROS2 topics), Safety rules (ASIL levels, guardian monitor), Real-time constraints (latency budgets per stage), Communication graph (module topic wiring).

**Embedded**: CPS layer map (Application -> Middleware/RTOS -> HAL -> Hardware), Target hardware (MCU model, clock, Flash/RAM), Toolchain (cross-compiler path), Memory map (linker sections), Safety rules (MISRA-C, banned APIs).
