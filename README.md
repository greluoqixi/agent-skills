# Claude Skills

Personal collection of Claude Code skills, distributed as a plugin marketplace.

## Marketplace Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add greluoqixi/claude-skills
```

Then install any plugin:

```bash
/plugin install claude-md-generator@claude-skills
```

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [claude-md-generator](./plugins/claude-md-generator/) | 2.0.0 | Generate and maintain CLAUDE.md files as intelligent codebase indexes. Supports 10 project types including autonomous driving, robotics, and embedded systems. |

## Manual Installation

If you prefer not to use the marketplace:

```bash
# Clone the repo
git clone https://github.com/greluoqixi/claude-skills.git

# Symlink individual skills into Claude Code
ln -s $(pwd)/claude-skills/plugins/claude-md-generator/skills/claude-md-generator \
  ~/.claude/skills/claude-md-generator
```

## Adding New Plugins

1. Create plugin structure under `plugins/<name>/`
2. Add `.claude-plugin/plugin.json` manifest
3. Add skills under `plugins/<name>/skills/`
4. Register in `.claude-plugin/marketplace.json`
5. Commit and push — users get updates via `/plugin marketplace update`

## Repository Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace registry
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md
│               ├── scripts/
│               ├── references/
│               └── assets/
└── README.md
```
