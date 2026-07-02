# Pipeline Stage AGENTS.md Template (Autonomous Driving)

For autonomous driving pipeline stages (Perception, Planning, Control, etc.).

## Template

```markdown
# {{STAGE_NAME}} Module

## Responsibility

{{ONE_SENTENCE_PURPOSE}} -- pipeline {{POSITION_IN_PIPELINE}}

## Input / Output

| Direction | Topic / Interface | Data Type | QoS |
|-----------|-------------------|-----------|-----|
{{#each IO_TOPICS}}
| {{DIRECTION}} | `{{TOPIC}}` | `{{TYPE}}` | {{QOS}} |
{{/each}}

## Algorithms

{{#each ALGORITHMS}}
- **{{NAME}}**: {{DESCRIPTION}} (config: `{{CONFIG_KEY}}`)
{{/each}}

## Key Files

| File | Purpose |
|------|---------|
{{#each KEY_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}

## Upstream Dependencies

{{#each UPSTREAM}}
- **{{MODULE}}** -> {{WHAT_IT_PROVIDES}}
{{/each}}

## Downstream Consumers

{{#each DOWNSTREAM}}
- **{{MODULE}}** <- {{WHAT_IT_CONSUMES}}
{{/each}}

## Safety Constraints

{{#each SAFETY_CONSTRAINTS}}
- {{CONSTRAINT}}
{{/each}}
```
