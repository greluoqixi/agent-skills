# Pipeline Stage CLAUDE.md Template (Autonomous Driving)

For autonomous driving pipeline stages (Perception, Planning, Control, etc.).

## Template

```markdown
# {{STAGE_NAME}} 模块

## 职责

{{ONE_SENTENCE_PURPOSE}} — pipeline {{POSITION_IN_PIPELINE}}

## 输入 / 输出

| 方向 | Topic / 接口 | 数据类型 | QoS |
|------|-------------|---------|-----|
{{#each IO_TOPICS}}
| {{DIRECTION}} | `{{TOPIC}}` | `{{TYPE}}` | {{QOS}} |
{{/each}}

## 算法

{{#each ALGORITHMS}}
- **{{NAME}}**: {{DESCRIPTION}} (配置: `{{CONFIG_KEY}}`)
{{/each}}

## 关键文件

| 文件 | 功能 |
|------|------|
{{#each KEY_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}

## 上游依赖

{{#each UPSTREAM}}
- **{{MODULE}}** → {{WHAT_IT_PROVIDES}}
{{/each}}

## 下游消费者

{{#each DOWNSTREAM}}
- **{{MODULE}}** ← {{WHAT_IT_CONSUMES}}
{{/each}}

## 安全约束

{{#each SAFETY_CONSTRAINTS}}
- {{CONSTRAINT}}
{{/each}}
```
