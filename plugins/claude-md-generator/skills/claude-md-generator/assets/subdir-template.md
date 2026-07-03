# Subdirectory CLAUDE.md Template (v2)

Loaded on-demand when Claude reads files in the directory.
20-40 lines. Template adapts to project type.

## Standard (Python, Node, Rust, Java, Go, Infra)

```markdown
# {{MODULE_NAME}} 模块

## 职责
{{ONE_SENTENCE}}

## 关键文件
| 文件 | 功能 |
|------|------|
{{#each KEY_FILES}}
| `{{NAME}}` | {{DESCRIPTION}} |
{{/each}}

## 依赖
- **依赖**: {{DEPENDS_ON}}
- **被依赖**: {{USED_BY}}

{{#if HAS_SUBMODULES}}
## 子模块
{{#each SUBMODULES}}
- **`{{PATH}}/`** — {{PURPOSE}}{{#if HAS_CLAUDEMD}} → `{{PATH}}/CLAUDE.md`{{/if}}
{{/each}}
{{/if}}

## 维护规则

当本目录内文件新增、移动、重命名或删除时，检查本文件是否需要更新。**运行 claude-md-generator 技能同步。**
```

## Pipeline Stage (AutoDriving)

See `pipeline-module-template.md` — includes I/O topics, algorithms, safety constraints.

## ROS2 Package (Robotics)

See `ros2-package-template.md` — includes nodes, interfaces, parameters, launch files.

## CPS Layer (Embedded)

See `cps-layer-template.md` — includes peripheral map, memory budget, timing, ISR safety.
