# Design: Bug Fix Knowledge Accumulation for Agent Skills

## Problem

When AI fixes a non-obvious bug in a project, the solution knowledge (symptom, root cause, fix approach, prevention rules) is lost when the conversation context clears. Future AI sessions have no way to learn from past fixes, leading to repeated mistakes.

## Scope

This is a feature provided **to third-party projects** that use `claude-md-generator` or `agents-md-generator`. When a skill generates CLAUDE.md/AGENTS.md for a project, it also sets up a knowledge accumulation mechanism.

## Approach: Passive Template (Hybrid Trigger)

Skill provides a structured template + soft constraint rules. AI autonomously decides when a fix is worth recording. No new hooks or scripts — consistency with existing skill architecture.

## TROUBLESHOOTING.md Template

Stored as a new skill asset. Copied to project root during initial generation.

### Structure

Two-part records: **Retrospect** (what happened) and **Prevention** (how to avoid next time).

- **Retrospect**: symptom, root cause chain, fix steps with file paths
- **Prevention**: mistake pattern (why AI went wrong), a check rule (executable verification before similar changes), related modules (upstream/downstream files to also review)

### Anti-Staleness

- Records grouped by month, reverse chronological
- Entries older than 6 months tagged `[可能过期]`
- Time-decay rule at top of file: AI should prefer recent records

### Template Content

```markdown
# Troubleshooting & Fix Knowledge

> 时间衰减：优先参考近 6 个月的记录。超过 6 个月的条目标注 `[可能过期]`。

## 记录格式

每条记录包含两部分：

### 回溯
- **症状**：错误现象（日志、报错信息、异常行为）
- **根因**：导致问题的根本原因链
- **方案**：修复的具体步骤，含关键代码片段或文件路径

### 预防
- **犯错模式**：AI 最初为什么走了错误方向（误判、遗漏、假设错误）
- **检查规则**：下次做类似改动时应先验证的条件（一条可执行的检查项）
- **关联模块**：修改这类代码时还需要关注的上下游文件
```

## Integration with CLAUDE.md/AGENTS.md

### Layer 1: Root File Reference

Root template gains a new section:

```markdown
## 经验知识库

@TROUBLESHOOTING.md — 历史问题修复记录及预防规则。修改代码前，检查是否涉及已有记录的关联模块。
```

### Layer 2: Maintenance Rule Extension

Existing maintenance rule in root template appends:

> **当你花费显著精力定位并修复一个非显而易见的 bug 时，必须在 TROUBLESHOOTING.md 中追加一条记录，包含回溯和预防两部分。**

Key qualifier: "非显而易见的" (non-obvious) — syntax errors, typos, and trivial config omissions don't qualify. Only deep root causes, cross-module impacts, or cases where AI initially went wrong.

## Skill Workflow Changes

### claude-md-generator (Claude Code)

| File | Change |
|------|--------|
| `assets/troubleshooting-template.md` | **New** — the template |
| `assets/root-template.md` | Add "经验知识库" section + extend maintenance rule |
| `SKILL.md` Phase 3 | Add step before manifest update: copy template if TROUBLESHOOTING.md missing |
| `SKILL.md` Bundled Resources | Add `troubleshooting-template.md` to assets list |

### agents-md-generator (Codex CLI)

Same changes, mirrored paths.

### Generation Behavior

- **First generation**: TROUBLESHOOTING.md copied to project root with template header + empty record area
- **Subsequent syncs**: TROUBLESHOOTING.md is NOT tracked by manifest — it's user/AI edited, skill only creates it once

### What It Does NOT Do

- No staleness detection for TROUBLESHOOTING.md
- No enforcement of entry count or quality
- No automatic cleanup of old entries
- No new hooks or scripts

## Design Rationale

| Decision | Reason |
|----------|--------|
| MD over HTML | AI-native, version-control friendly, referenceable via `@TROUBLESHOOTING.md` |
| Single file over directory | Simple, low management cost. Matches user preference |
| Passive template over active detection | Consistent with skill philosophy. Git log parsing is unreliable. 80% of value from rule + template |
| Prevention-focused records | Pure fix logs only help when symptoms match exactly. Check rules help before similar changes |
| No manifest tracking | TROUBLESHOOTING.md is a knowledge base, not a config file. Over-automation turns it into noise |
| Soft constraint only | Follows existing watchdog pattern. Hard enforcement would create friction for trivial fixes |

## Files Changed Summary

```
plugins/
├── claude-md-generator/skills/claude-md-generator/
│   ├── SKILL.md                              # Phase 3 + Bundled Resources
│   └── assets/
│       ├── root-template.md                  # New section + rule extension
│       └── troubleshooting-template.md       # NEW
└── agents-md-generator/skills/agents-md-generator/
    ├── SKILL.md                              # Same changes
    └── assets/
        ├── root-template.md                  # Same changes
        └── troubleshooting-template.md       # NEW
```
