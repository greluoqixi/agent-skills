# CPS Layer CLAUDE.md Template (Embedded Systems)

For Cyber-Physical System layers in embedded projects.

## Template

```markdown
# {{LAYER_NAME}} 层

## 职责

{{ONE_SENTENCE_PURPOSE}} — CPS 层次: {{POSITION_IN_CPS}}

## 关键文件

| 文件 | 功能 |
|------|------|
{{#each KEY_FILES}}
| `{{FILE}}` | {{DESCRIPTION}} |
{{/each}}

## 硬件接口

{{#if HAS_HARDWARE_INTERFACE}}
| 外设 | 引脚/总线 | 中断 | DMA |
|------|----------|------|-----|
{{#each PERIPHERALS}}
| `{{NAME}}` | {{PINS}} | {{IRQ}} | {{DMA}} |
{{/each}}
{{else}}
本层不直接访问硬件 — 通过 {{LOWER_LAYER}} 抽象
{{/if}}

## 内存预算

{{#if HAS_MEMORY_BUDGET}}
- **Flash**: {{FLASH_USAGE}}
- **RAM**: {{RAM_USAGE}} (栈 {{STACK_SIZE}}, 堆 {{HEAP_SIZE}})
{{else}}
由 {{ALLOCATED_BY}} 层管理
{{/if}}

## 时间约束

{{#if HAS_TIMING}}
- **周期**: {{CYCLE_TIME}}
- **WCET**: {{WCET}}
- **优先级**: {{PRIORITY}}
{{/if}}

## 中断安全

{{#if HAS_ISR}}
- ISR 中禁止: {{BANNED_IN_ISR}}
- 临界区最大时长: {{CRITICAL_SECTION_MAX}}
{{/if}}

## 维护规则

当本目录内文件新增、移动、重命名或删除时，检查本文件是否需要更新。**运行 claude-md-generator 技能同步。**
```
