# Nested Subdirectory AGENTS.md Template (v1)

Codex loads nested AGENTS.md files automatically when working in that directory.
This provides path-scoped context. Keep it concise (20-40 lines). Template adapts to project type.

## Standard (Python, Node, Rust, Java, Go, Infra)

```markdown
# {{MODULE_NAME}} Module

## Responsibility
{{ONE_SENTENCE}}

## Key Files
| File | Purpose |
|------|---------|
{{#each KEY_FILES}}
| `{{NAME}}` | {{DESCRIPTION}} |
{{/each}}

## Dependencies
- **Depends on**: {{DEPENDS_ON}}
- **Used by**: {{USED_BY}}

{{#if HAS_SUBMODULES}}
## Submodules
{{#each SUBMODULES}}
- **`{{PATH}}/`** -- {{PURPOSE}}{{#if HAS_AGENTSMD}} -> `{{PATH}}/AGENTS.md`{{/if}}
{{/each}}
{{/if}}

## Maintenance Rules

When files in this directory are added, moved, renamed, or deleted, check whether this AGENTS.md needs updating. **Run the agents-md-generator skill to sync.**
```

## Pipeline Stage (AutoDriving)

See `pipeline-module-template.md` -- includes I/O topics, algorithms, safety constraints.

## ROS2 Package (Robotics)

See `ros2-package-template.md` -- includes nodes, interfaces, parameters, launch files.

## CPS Layer (Embedded)

See `cps-layer-template.md` -- includes peripheral map, memory budget, timing, ISR safety.
