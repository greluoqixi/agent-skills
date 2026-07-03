# ROS2 Package CLAUDE.md Template

For individual ROS2 packages in a robotics workspace.

## Template

```markdown
# {{PACKAGE_NAME}} 包

## 用途

{{ONE_SENTENCE_PURPOSE}}

## 节点

| 节点名 | 功能 | 可执行文件 |
|--------|------|-----------|
{{#each NODES}}
| `{{NODE_NAME}}` | {{DESCRIPTION}} | `{{EXECUTABLE}}` |
{{/each}}

## 接口

### 发布 (Publishers)

| Topic | 消息类型 | QoS |
|-------|---------|-----|
{{#each PUBLISHERS}}
| `{{TOPIC}}` | `{{MSG_TYPE}}` | {{QOS}} |
{{/each}}

### 订阅 (Subscribers)

| Topic | 消息类型 | QoS |
|-------|---------|-----|
{{#each SUBSCRIBERS}}
| `{{TOPIC}}` | `{{MSG_TYPE}}` | {{QOS}} |
{{/each}}

## 参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
{{#each PARAMS}}
| `{{NAME}}` | `{{TYPE}}` | `{{DEFAULT}}` | {{DESCRIPTION}} |
{{/each}}

## 依赖

- **ROS2 包**: {{ROS2_DEPS}}
- **系统**: {{SYSTEM_DEPS}}

## 启动文件

| 文件 | 用途 |
|------|------|
{{#each LAUNCH_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}

## 维护规则

当本目录内文件新增、移动、重命名或删除时，检查本文件是否需要更新。**运行 claude-md-generator 技能同步。**
```
