# Agent Skills

Personal collection of AI agent skills for Claude Code and Codex CLI, distributed as a plugin marketplace.

## Marketplace Installation

Add this marketplace to your agent:

**Claude Code:**

```bash
/plugin marketplace add greluoqixi/claude-skills
```

Then install any Claude Code plugin:

```bash
/plugin install claude-md-generator@claude-skills
```

**Codex CLI:**

```bash
/codex plugin marketplace add greluoqixi/claude-skills
```

Then install any Codex plugin:

```bash
/codex plugin install agents-md-generator@claude-skills
```

## Plugins

| Plugin | Version | Agent | Description |
|--------|---------|-------|-------------|
| [claude-md-generator](./plugins/claude-md-generator/) | 2.0.0 | Claude Code | Generate and maintain CLAUDE.md files as intelligent codebase indexes. Supports 10 project types including autonomous driving, robotics, and embedded systems. |
| [agents-md-generator](./plugins/agents-md-generator/) | 1.0.0 | Codex CLI | Generate and maintain AGENTS.md files as intelligent codebase indexes for Codex CLI. Supports 10 project types including autonomous driving, robotics, and embedded systems. |

## Manual Installation

If you prefer not to use the marketplace:

**Claude Code:**

```bash
# Clone the repo
git clone https://github.com/greluoqixi/claude-skills.git

# Symlink individual skills into Claude Code
ln -s $(pwd)/claude-skills/plugins/claude-md-generator/skills/claude-md-generator \
  ~/.claude/skills/claude-md-generator
```

**Codex CLI:**

```bash
# Clone the repo
git clone https://github.com/greluoqixi/claude-skills.git

# Symlink individual skills into Codex CLI
ln -s $(pwd)/claude-skills/plugins/agents-md-generator/skills/agents-md-generator \
  ~/.codex/skills/agents-md-generator
```

## Adding New Plugins

1. Create plugin structure under `plugins/<name>/`
2. Add manifest: `.claude-plugin/plugin.json` for Claude Code, `.codex-plugin/plugin.json` for Codex CLI
3. Add skills under `plugins/<name>/skills/`
4. Register in `.claude-plugin/marketplace.json`
5. Commit and push — users get updates via `/plugin marketplace update` (Claude Code) or `/codex plugin marketplace update` (Codex CLI)

## Repository Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace registry
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/       # Claude Code plugin manifest
│       │   └── plugin.json
│       ├── .codex-plugin/        # Codex CLI plugin manifest
│       │   └── plugin.json
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md
│               ├── scripts/
│               ├── references/
│               └── assets/
└── README.md
```
