# ROS2 Package AGENTS.md Template

For individual ROS2 packages in a robotics workspace.

## Template

```markdown
# {{PACKAGE_NAME}} Package

## Purpose

{{ONE_SENTENCE_PURPOSE}}

## Nodes

| Node Name | Purpose | Executable |
|-----------|---------|------------|
{{#each NODES}}
| `{{NODE_NAME}}` | {{DESCRIPTION}} | `{{EXECUTABLE}}` |
{{/each}}

## Interfaces

### Publishers

| Topic | Message Type | QoS |
|-------|-------------|-----|
{{#each PUBLISHERS}}
| `{{TOPIC}}` | `{{MSG_TYPE}}` | {{QOS}} |
{{/each}}

### Subscribers

| Topic | Message Type | QoS |
|-------|-------------|-----|
{{#each SUBSCRIBERS}}
| `{{TOPIC}}` | `{{MSG_TYPE}}` | {{QOS}} |
{{/each}}

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
{{#each PARAMS}}
| `{{NAME}}` | `{{TYPE}}` | `{{DEFAULT}}` | {{DESCRIPTION}} |
{{/each}}

## Dependencies

- **ROS2 packages**: {{ROS2_DEPS}}
- **System**: {{SYSTEM_DEPS}}

## Launch Files

| File | Purpose |
|------|---------|
{{#each LAUNCH_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}
```
