# Root AGENTS.md Template (v1)

Every section must pass: "If I delete this line, would Codex make a mistake?"
Sections adapt per project type. Empty sections are omitted entirely.

## Template Structure

```markdown
{{#if HAS_README}}@README.md{{/if}}
{{#if HAS_EXISTING_AGENTS}}@AGENTS.md{{/if}}

# AGENTS.md

{{#if IS_AUTONOMOUS_DRIVING}}
## Pipeline Overview

```
Sensor (LiDAR/Camera/Radar/GPS/IMU)
  -> Perception (detection, tracking, segmentation)
  -> Prediction (trajectory prediction)
  -> Planning (path + behavior + motion planning)
  -> Control (PID/MPC/LQR -> throttle/brake/steering)
  -> CAN bus -> Vehicle actuators
```

| Module | Purpose | Detail Index |
|--------|---------|-------------|
{{#each PIPELINE_MODULES}}
| `{{PATH}}/` | {{PURPOSE}} | `{{PATH}}/AGENTS.md` |
{{/each}}

Support: Localization, HD-Map, Monitor/Guardian, Simulation
{{/if}}

{{#if IS_ROBOTICS}}
## Package Map

| Package | Purpose | Detail Index |
|---------|---------|-------------|
{{#each PACKAGES}}
| `{{NAME}}/` | {{PURPOSE}} | `{{NAME}}/AGENTS.md` |
{{/each}}
{{/if}}

{{#if IS_EMBEDDED}}
## Target Hardware

- **MCU/MPU**: {{CHIP_MODEL}} ({{ARCHITECTURE}}, {{CLOCK_SPEED}})
- **Flash**: {{FLASH_SIZE}}, **RAM**: {{RAM_SIZE}}
- **Toolchain**: {{COMPILER}} {{COMPILER_VERSION}}

## CPS Layers

| Layer | Directory | Detail Index |
|-------|-----------|-------------|
{{#each CPS_LAYERS}}
| {{LAYER}} | `{{PATH}}/` | `{{PATH}}/AGENTS.md` |
{{/each}}
{{/if}}

{{#unless IS_SPECIALIZED_DOMAIN}}
## Architecture

{{ARCHITECTURE_DESCRIPTION}}

{{#if HAS_MODULES}}
| Module | Purpose | Detail Index |
|--------|---------|-------------|
{{#each MODULES}}
| `{{PATH}}/` | {{PURPOSE}} | `{{PATH}}/AGENTS.md` |
{{/each}}
{{/if}}
{{/unless}}

## Commands

{{#each COMMANDS}}
- {{DESCRIPTION}}: `{{EXACT_COMMAND}}`
{{/each}}

{{#if HAS_ARCHITECTURE_CONSTRAINTS}}
## Architecture Constraints

{{#each CONSTRAINTS}}
- {{#if IS_PROHIBITION}}**Forbidden**{{else}}**Required**{{/if}} {{RULE}}
{{/each}}
{{/if}}

{{#if HAS_ENTRY_POINTS}}
## Entry Points

{{#each ENTRY_POINTS}}
- **`{{FILE}}`** -- {{DESCRIPTION}}
{{/each}}
{{/if}}

{{#if HAS_CODING_CONVENTIONS}}
## Code Conventions

{{#each CONVENTIONS}}
- {{CONVENTION}}
{{/each}}
{{/if}}

{{#if HAS_ENVIRONMENT}}
## Environment

{{#each ENV_ITEMS}}
- {{ITEM}}
{{/each}}
{{/if}}

{{#if HAS_SAFETY_RULES}}
## Safety Rules

{{#each SAFETY_RULES}}
- {{RULE}}
{{/each}}
{{/if}}

{{#if HAS_REALTIME}}
## Real-Time Constraints

{{#each REALTIME_CONSTRAINTS}}
- {{CONSTRAINT}}
{{/each}}
{{/if}}

{{#if HAS_HOOKS}}
## Automation (handled by hooks)

{{#each HOOK_ITEMS}}
- {{DESCRIPTION}} -> `{{HOOK_EVENT}}` hook
{{/each}}
{{/if}}

{{#if HAS_TOOLCHAIN}}
## Toolchain

{{#each TOOLCHAIN_ITEMS}}
- {{ITEM}}
{{/each}}
{{/if}}

{{#if HAS_MEMORY_MAP}}
## Memory Layout

- Flash: {{FLASH_LAYOUT}}
- RAM: {{RAM_LAYOUT}}
- Stack: {{STACK_SIZE}}, Heap: {{HEAP_SIZE}}
{{/if}}

{{#if HAS_CODE_SANDBOX}}
## Codex Sandbox Configuration

- Sandbox mode: {{SANDBOX_MODE}}
- Approval policy: {{APPROVAL_POLICY}}
{{#if CUSTOM_MODEL}}- Model: {{MODEL}}{{/if}}
{{/if}}

{{#if HAS_CAVEATS}}
## Caveats

{{#each CAVEATS}}
- {{CAVEAT}}
{{/each}}
{{/if}}

{{#if HAS_TROUBLESHOOTING}}
## Knowledge Base

@TROUBLESHOOTING.md — Historical fix records and prevention rules. Before modifying code, check whether it involves related modules from existing records.
{{/if}}

## Maintenance Rules

When you create, move, rename, or delete files/directories in this project, you MUST check whether this file AND all nested AGENTS.md files in subdirectories need updating to reflect the latest project structure. **Run the agents-md-generator skill to sync all affected files after structural changes.**

At the start of each session, run `python .codex/check-stale.py` to detect directory structure drift from external changes.

When you spend significant effort diagnosing and fixing a non-obvious bug, you MUST append a record to TROUBLESHOOTING.md with both Retrospect (symptoms, root cause, solution) and Prevention (mistake pattern, check rule, related modules) sections.
```

## Conditional Logic

Sections are controlled by the 10-type selection table. Generator evaluates:
1. Project type -> domain-specific sections
2. File existence -> HAS_README, HAS_EXISTING_AGENTS, HAS_TROUBLESHOOTING, HAS_HOOKS
3. Content detection -> HAS_CAVEATS, HAS_SAFETY_RULES, HAS_REALTIME
4. Non-obviousness -> CANNOT_BE_INFERRED
5. .codex/config.toml presence -> HAS_CODE_SANDBOX

Sections that evaluate to empty are omitted entirely.
