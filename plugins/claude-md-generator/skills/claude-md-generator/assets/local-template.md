# CLAUDE.local.md Template

Personal project-specific overrides. Gitignored, appends to project CLAUDE.md.

## Template

```markdown
# CLAUDE.local.md — 本地覆盖

## 本地环境

- {{LOCAL_ENV_DETAILS}}

## 本地命令

{{#each LOCAL_COMMANDS}}
- {{COMMAND}}
{{/each}}

## 个人偏好

{{#each PERSONAL_PREFERENCES}}
- {{PREFERENCE}}
{{/each}}
```
