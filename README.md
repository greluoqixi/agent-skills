# Claude Skills

Personal collection of Claude Code skills.

## Skills

| Skill | Description |
|-------|-------------|
| [claude-md-generator](./claude-md-generator/) | Generate and maintain CLAUDE.md files as intelligent codebase indexes. Supports 10 project types including autonomous driving, robotics, and embedded systems. |

## Installation

Copy or symlink individual skill directories into `~/.claude/skills/`:

```bash
# Option 1: symlink (recommended — auto-updates when you git pull)
ln -s $(pwd)/claude-md-generator ~/.claude/skills/claude-md-generator

# Option 2: copy
cp -r claude-md-generator ~/.claude/skills/
```

## Structure

Each skill follows the standard layout:

```
skill-name/
├── SKILL.md          # Main instructions (required)
├── scripts/          # Executable code
├── references/       # Documentation loaded on demand
└── assets/           # Templates and other output files
```
