# .claude/rules/ Template

Path-scoped rules that load on demand when Claude reads matching files.

## Template

```markdown
---
paths:
  {{GLOB_PATTERNS}}
---

# {{RULE_NAME}}

## 规则

{{#each RULES}}
- {{RULE}}
{{/each}}

## 原因

{{WHY_THIS_RULE_EXISTS}}
```

## Example

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---

# API Design Rules

## 规则

- 所有 handler 返回 `{ data, error }` 格式
- 请求体验证使用 Zod schema
- 每个 public endpoint 需要 OpenAPI JSDoc 注释

## 原因

统一的返回格式让错误处理中间件和客户端可以一次性处理所有响应。
```
