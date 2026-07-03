# Root CLAUDE.md Template (v2)

Every section must pass: "If I delete this line, would Claude make a mistake?"
Sections adapt per project type. Empty sections are omitted entirely.

## Template Structure

```markdown
{{#if HAS_README}}@README.md{{/if}}
{{#if HAS_AGENTS}}@AGENTS.md{{/if}}

# CLAUDE.md

{{#if IS_AUTONOMOUS_DRIVING}}
## Pipeline 总览

```
传感器 (LiDAR/Camera/Radar/GPS/IMU)
  → Perception (检测、追踪、分割)
  → Prediction (轨迹预测)
  → Planning (路径 + 行为 + 运动规划)
  → Control (PID/MPC/LQR → 油门/制动/转向)
  → CAN bus → 车辆执行器
```

| 模块 | 用途 | 详细索引 |
|------|------|----------|
{{#each PIPELINE_MODULES}}
| `{{PATH}}/` | {{PURPOSE}} | `{{PATH}}/CLAUDE.md` |
{{/each}}

辅助: Localization, HD-Map, Monitor/Guardian, Simulation
{{/if}}

{{#if IS_ROBOTICS}}
## 包地图

| 包 | 用途 | 详细索引 |
|----|------|----------|
{{#each PACKAGES}}
| `{{NAME}}/` | {{PURPOSE}} | `{{NAME}}/CLAUDE.md` |
{{/each}}
{{/if}}

{{#if IS_EMBEDDED}}
## 目标硬件

- **MCU/MPU**: {{CHIP_MODEL}} ({{ARCHITECTURE}}, {{CLOCK_SPEED}})
- **Flash**: {{FLASH_SIZE}}, **RAM**: {{RAM_SIZE}}
- **工具链**: {{COMPILER}} {{COMPILER_VERSION}}

## CPS 分层

| 层 | 目录 | 详细索引 |
|----|------|----------|
{{#each CPS_LAYERS}}
| {{LAYER}} | `{{PATH}}/` | `{{PATH}}/CLAUDE.md` |
{{/each}}
{{/if}}

{{#unless IS_SPECIALIZED_DOMAIN}}
## 架构

{{ARCHITECTURE_DESCRIPTION}}

{{#if HAS_MODULES}}
| 模块 | 用途 | 详细索引 |
|------|------|----------|
{{#each MODULES}}
| `{{PATH}}/` | {{PURPOSE}} | `{{PATH}}/CLAUDE.md` |
{{/each}}
{{/if}}
{{/unless}}

## 命令

{{#each COMMANDS}}
- {{DESCRIPTION}}: `{{EXACT_COMMAND}}`
{{/each}}

{{#if HAS_ARCHITECTURE_CONSTRAINTS}}
## 架构约束

{{#each CONSTRAINTS}}
- {{#if IS_PROHIBITION}}**禁止**{{else}}**必须**{{/if}} {{RULE}}
{{/each}}
{{/if}}

{{#if HAS_ENTRY_POINTS}}
## 入口文件

{{#each ENTRY_POINTS}}
- **`{{FILE}}`** — {{DESCRIPTION}}
{{/each}}
{{/if}}

{{#if HAS_CODING_CONVENTIONS}}
## 代码约定

{{#each CONVENTIONS}}
- {{CONVENTION}}
{{/each}}
{{/if}}

{{#if HAS_ENVIRONMENT}}
## 环境

{{#each ENV_ITEMS}}
- {{ITEM}}
{{/each}}
{{/if}}

{{#if HAS_SAFETY_RULES}}
## 安全规则

{{#each SAFETY_RULES}}
- {{RULE}}
{{/each}}
{{/if}}

{{#if HAS_REALTIME}}
## 实时约束

{{#each REALTIME_CONSTRAINTS}}
- {{CONSTRAINT}}
{{/each}}
{{/if}}

## 自动化（由 hooks 处理）

- 目录结构变更检测 → `SessionStart` hook（`.claude/check-stale.py`）

{{#each HOOK_ITEMS}}
- {{DESCRIPTION}} → `{{HOOK_EVENT}}` hook
{{/each}}

{{#if HAS_TOOLCHAIN}}
## 工具链

{{#each TOOLCHAIN_ITEMS}}
- {{ITEM}}
{{/each}}
{{/if}}

{{#if HAS_MEMORY_MAP}}
## 内存布局

- Flash: {{FLASH_LAYOUT}}
- RAM: {{RAM_LAYOUT}}
- 栈: {{STACK_SIZE}}, 堆: {{HEAP_SIZE}}
{{/if}}

{{#if HAS_CAVEATS}}
## 注意事项

{{#each CAVEATS}}
- {{CAVEAT}}
{{/each}}
{{/if}}

## 维护规则

当你在这个项目中新增、移动、重命名或删除文件/目录时，必须检查本文件是否需要更新以反映最新的项目结构。**请在变更完成后运行 claude-md-generator 技能同步本文件。**
```

## Conditional Logic

Sections are controlled by the 10-type selection table. Generator evaluates:
1. Project type → domain-specific sections
2. File existence → HAS_README, HAS_AGENTS, HAS_HOOKS
3. Content detection → HAS_CAVEATS, HAS_SAFETY_RULES, HAS_REALTIME
4. Non-obviousness → CANNOT_BE_INFERRED

Sections that evaluate to empty are omitted entirely.
