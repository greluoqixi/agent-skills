# Agent Skills

[中文版本](./README_CN.md)

Personal collection of AI agent skills for Claude Code and Codex CLI, distributed as a plugin marketplace.

## Features

### Intelligent Codebase Indexing

Generate structured `CLAUDE.md` / `AGENTS.md` files that serve as navigable indexes for AI agents. Each generated file answers: which files matter, where are the entry points, and how do modules relate.

- **10 project types**: Python, Node/Web, Rust, Java, Go, Infrastructure, Autonomous Driving, Robotics (ROS2), Embedded Systems, and Generic fallback
- **4-phase workflow**: Probe (detect type) → Scan (map structure) → Generate (produce docs) → Verify (validate output)
- **Progressive disclosure**: Root file is a navigation hub (≤250 lines). Detail lives in subdirectory files loaded on-demand.

### Manifest-Based Sync

Generated files are tracked via SHA-256 section hashes. On subsequent runs, sections with matching hashes are safe to regenerate; sections with changed hashes were user-edited and are preserved. No more overwriting manual tweaks.

### Multi-Layer Maintenance

Three lines of defense against stale documentation:

| Layer | Mechanism | How it works |
|-------|-----------|--------------|
| **Hard** | SessionStart hook | `check-stale.py` fingerprints directory structure; harness injects a system-reminder when drift is detected between sessions |
| **Soft** | Self-referential watchdog | Every generated file (root + subdirectories) contains a maintenance rule instructing the AI to sync after structural changes |
| **Contextual** | Path-scoped rules | `.claude/rules/` (Claude Code) and nested `AGENTS.md` (Codex CLI) load only when the AI works in matching directories |

### Domain-Specific Templates

- **Autonomous Driving**: Pipeline-centric (Perception → Planning → Control), I/O topics, safety invariants
- **Robotics (ROS2)**: Package-level docs with nodes, interfaces, parameters, launch files
- **Embedded Systems**: CPS layered architecture, memory budgets, timing constraints, ISR safety
- **Standard software**: Auth, DB, API conventions only when non-obvious

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
codex plugin add greluoqixi/claude-skills
```

Then install any Codex plugin:

```bash
codex plugin add agents-md-generator@claude-skills
```

## Plugins

| Plugin | Version | Agent | Description |
|--------|---------|-------|-------------|
| [claude-md-generator](./plugins/claude-md-generator/) | 2.0.0 | Claude Code | Generate and maintain CLAUDE.md files as intelligent codebase indexes. Supports 10 project types. Includes SessionStart hook for automatic drift detection. |
| [agents-md-generator](./plugins/agents-md-generator/) | 1.0.0 | Codex CLI | Generate and maintain AGENTS.md files as intelligent codebase indexes for Codex CLI. Supports 10 project types. Includes drift detection script with nested AGENTS.md support. |

## Manual Installation

If you prefer not to use the marketplace:

**Claude Code:**

```bash
# Clone the repo
git clone https://github.com/greluoqixi/agent-skills.git

# Symlink individual skills into Claude Code
ln -s $(pwd)/agent-skills/plugins/claude-md-generator/skills/claude-md-generator \
  ~/.claude/skills/claude-md-generator
```

**Codex CLI:**

```bash
# Clone the repo
git clone https://github.com/greluoqixi/agent-skills.git

# Symlink individual skills into Codex CLI
ln -s $(pwd)/agent-skills/plugins/agents-md-generator/skills/agents-md-generator \
  ~/.codex/skills/agents-md-generator
```

## Updating

Refresh the marketplace catalog and upgrade installed plugins to the latest version:

**Claude Code:**

```bash
# Refresh marketplace catalog
/plugin marketplace update

# Upgrade plugin to latest version
/plugin update claude-md-generator@claude-skills
```

If the `update` subcommand is not available, uninstall and reinstall:

```bash
/plugin uninstall claude-md-generator
/plugin install claude-md-generator@claude-skills
```

**Codex CLI:**

```bash
# Refresh marketplace catalog
codex plugin marketplace upgrade

# Re-add plugin to get latest version
codex plugin add agents-md-generator@claude-skills
```

**Manual (symlink):**

```bash
cd ~/agent-skills && git pull
```

## Adding New Plugins

1. Create plugin structure under `plugins/<name>/`
2. Add manifest: `.claude-plugin/plugin.json` for Claude Code, `.codex-plugin/plugin.json` for Codex CLI
3. Add skills under `plugins/<name>/skills/`
4. Register in `.claude-plugin/marketplace.json`
5. Commit and push — users get updates via `/plugin marketplace update` (Claude Code) or `codex plugin marketplace upgrade` (Codex CLI)

## Repository Structure

```
agent-skills/
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
