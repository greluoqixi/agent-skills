# CPS Layer AGENTS.md Template (Embedded Systems)

For Cyber-Physical System layers in embedded projects.

## Template

```markdown
# {{LAYER_NAME}} Layer

## Responsibility

{{ONE_SENTENCE_PURPOSE}} -- CPS level: {{POSITION_IN_CPS}}

## Key Files

| File | Purpose |
|------|---------|
{{#each KEY_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}

## Hardware Interface

{{#if HAS_HARDWARE_INTERFACE}}
| Peripheral | Pins/Bus | IRQ | DMA |
|------------|----------|-----|-----|
{{#each PERIPHERALS}}
| `{{NAME}}` | {{PINS}} | {{IRQ}} | {{DMA}} |
{{/each}}
{{else}}
This layer does not access hardware directly -- abstracted through {{LOWER_LAYER}}
{{/if}}

## Memory Budget

{{#if HAS_MEMORY_BUDGET}}
- **Flash**: {{FLASH_USAGE}}
- **RAM**: {{RAM_USAGE}} (stack {{STACK_SIZE}}, heap {{HEAP_SIZE}})
{{else}}
Managed by {{ALLOCATED_BY}} layer
{{/if}}

## Timing Constraints

{{#if HAS_TIMING}}
- **Cycle**: {{CYCLE_TIME}}
- **WCET**: {{WCET}}
- **Priority**: {{PRIORITY}}
{{/if}}

## Interrupt Safety

{{#if HAS_ISR}}
- Banned in ISR: {{BANNED_IN_ISR}}
- Critical section max duration: {{CRITICAL_SECTION_MAX}}
{{/if}}

## Maintenance Rules

When files in this directory are added, moved, renamed, or deleted, check whether this AGENTS.md needs updating. **Run the agents-md-generator skill to sync.**
```
