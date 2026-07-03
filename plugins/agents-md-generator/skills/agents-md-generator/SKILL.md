---
name: agents-md-generator
description: Generate and maintain AGENTS.md files as intelligent codebase indexes for Codex CLI. Use this skill whenever starting work in a new repository, when project structure changes, when asked to generate/update/create AGENTS.md, or when needing to understand project architecture before making changes. Supports 10 project types including autonomous driving, robotics, and embedded systems. Automatically detects project type, generates root AGENTS.md, nested subdirectory AGENTS.md files, AGENTS.override.md for path-scoped overrides.
allowed-tools: "Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"
argument-hint: "<project-root>"
---

# AGENTS.md Generator

Generate and maintain AGENTS.md files as intelligent, navigable indexes for Codex CLI working in unfamiliar codebases. The core problem: Codex lands in a new repo and doesn't know which files matter, where the entry points are, or how modules relate. A well-structured AGENTS.md answers those questions immediately.

## When to Use

Triggers automatically when:
- Starting work in a new repository or unfamiliar codebase
- Project structure has changed (files added, removed, renamed, reorganized)
- User asks to generate, update, or create AGENTS.md or "project docs for AI"
- After major refactors that change module layout

Do NOT use for: single-file README updates, human-facing documentation (use doc-coauthoring), or writing code comments/docstrings.

## Core Principles

Explain these to the user only if they ask why certain decisions were made.

### The 200-Line Limit

Codex CLI loads AGENTS.md into its context window. Every line consumes tokens. **Soft limit 200, hard stop 250** — if a file exceeds 250 lines, push detail to nested subdirectory AGENTS.md files.

### The Delete Test

For every line: **"If I deleted this line, would Codex make a mistake?"** If no, delete it. This eliminates generic advice ("write clean code"), language-default conventions ("use 4-space indent"), and information Codex can infer from config files ("this project uses React 18").

### Progressive Disclosure

The root AGENTS.md is a navigation hub, not a manual. Point to deeper docs:
- `@README.md` bridges the human-facing README
- `@AGENTS.md` bridges existing cross-tool agent docs
- Nested `AGENTS.md` in subdirectories provide path-scoped context (Codex auto-loads them when working in those directories)
- `AGENTS.override.md` files extend or override parent AGENTS.md without modifying the shared base

### Manifest-Based Sync

Generated AGENTS.md files are tracked via `.codex/.agents-md-state.json`, which stores SHA-256 hashes of each section. During sync, sections whose hash matches the manifest are safe to regenerate. Sections whose hash differs were user-edited and are preserved. See `scripts/manifest.py` for the implementation.

## Codex-Specific Conventions

### AGENTS.md Loading

Codex loads AGENTS.md files using this hierarchy:
1. **Global**: `~/.codex/AGENTS.override.md` > `~/.codex/AGENTS.md`
2. **Project walk**: Starting from Git root, walking down to the working directory
3. In each directory, checks: `AGENTS.override.md` > `AGENTS.md` > fallback filenames
4. All files are **concatenated** (root -> deepest directory)
5. Files closer to cwd override earlier guidance (appear later in prompt)

### AGENTS.override.md

Placed in subdirectories to extend or override the parent AGENTS.md. Useful for:
- Team-specific overrides without modifying shared AGENTS.md
- Path-scoped conventions (e.g., frontend team rules in `src/frontend/AGENTS.override.md`)
- Personal local preferences (place in gitignored locations)

### Nested AGENTS.md for Path-Scoped Rules

Unlike Claude Code's `.claude/rules/` directory, Codex achieves path-scoped rules through **nested AGENTS.md files** in subdirectories. Each subdirectory can have its own AGENTS.md that Codex loads when working in that directory. This is the primary mechanism for scoped instructions.

## The 4-Phase Workflow

Follow these phases in order. Each phase produces information the next phase needs.

### Phase 1: Probe

Run these checks in parallel at the project root:

1. **Detect project type** — one of 10 types:
   - `python` — pyproject.toml, setup.py, requirements.txt
   - `node-web` — package.json (with or without frontend framework)
   - `rust` — Cargo.toml
   - `java` — pom.xml, build.gradle
   - `go` — go.mod
   - `infra` — .tf files, K8s manifests, Ansible playbooks
   - `autonomous-driving` — Apollo (modules/{perception,planning,control}) or Autoware (.repos + ROS2 pipeline)
   - `robotics` — ROS2 workspace (package.xml + _msgs/_control suffixed packages)
   - `embedded` — FreeRTOSConfig.h, .ioc, linker scripts, Zephyr device trees
   - `generic` — none of the above

   Use `scripts/scan_dir.py` for deterministic detection, or check characteristic files manually.

2. **Check for monorepo** — `detect_monorepo()` in scan_dir.py checks ecosystem-specific markers.
3. **Check for existing AGENTS.md** — if present, generated AGENTS.md bridges it with `@AGENTS.md`.
4. **Read .gitignore** and other ignore files for directory filtering.
5. **Read .codex/config.toml** — detect configured model, sandbox mode, and approval policy to reference in output.
6. **Read README.md** first paragraph for project description.

### Phase 2: Scan

Run `scripts/scan_dir.py <root> --max-depth 3` (or manual find/glob as fallback).

The scanner output provides:
- Full directory tree with file counts and classifications
- Project type and monorepo status
- Ignore patterns applied

From this, determine:
- Which directories need AGENTS.md (>15 files or >3 subdirs; lowered thresholds for specialized domains)
- Which subdirectories need AGENTS.override.md for path-scoped overrides
- Which config files to read for metadata extraction

### Phase 3: Generate

Produce up to 3 product types:

**Root AGENTS.md** (`./AGENTS.md`):
Read `assets/root-template.md` for structure. Section selection adapts to project type per the table in `references/templates.md`. Key decisions:
- Domain-specific sections (pipeline, CPS layers, safety) only for specialized types
- Standard software sections (auth, DB, data) only when relevant
- Every section passes the delete test
- Commands section: only what can't be inferred from config files

**Nested Subdirectory AGENTS.md / AGENTS.override.md**:
Read `assets/subdir-template.md` for standard subdirectory AGENTS.md structure.
Read `assets/override-template.md` for AGENTS.override.md structure (path-scoped overrides).
Template adapts:
- Standard projects -> basic module template
- Autonomous driving pipeline stages -> `assets/pipeline-module-template.md`
- ROS2 packages -> `assets/ros2-package-template.md`
- Embedded CPS layers -> `assets/cps-layer-template.md`

**Update manifest**: After all files are written, run `python scripts/manifest.py update <root>` to compute and store section hashes in `.codex/.agents-md-state.json`.

**Install drift detector**: Copy `assets/check-stale.py` to `<root>/.codex/check-stale.py`. Unlike Claude Code, Codex CLI has no native hooks system, so the script is invoked by the AGENTS.md maintenance rule (see root template) — Codex runs `python .codex/check-stale.py` when starting substantive work or after structural changes.

**Ask user** if ambiguous information encountered (unclear module purpose, ambiguous entry points, unclear architecture flow). Questions are single-choice or short-answer.

### Phase 4: Verify

Before presenting results:
1. **Line count**: Each file <=250 lines. Push to nested AGENTS.md if over.
2. **Sensitive data scan**: No `.env`, passwords, secrets, keys in output.
3. **Commands copy-paste check**: Every command is runnable from project root.
4. **Delete test**: Re-skim each line.
5. **Report summary**: What was generated, key findings, any preserved sections.

## Sync Mode

When AGENTS.md files already exist and user asks to update:

1. Run `python scripts/manifest.py check <root>` to compare hashes.
2. Sections with matching hashes -> safe to regenerate.
3. Sections with changed hashes -> user edited, preserve.
4. Run Phase 1-2 of generation, then regenerate only safe sections in Phase 3.
5. Update manifest after regeneration.
6. Report preserved vs regenerated sections to user.

If no manifest exists, offer to do a full regeneration.

## Nested AGENTS.md Generation Triggers

Codex uses nested AGENTS.md files for path-scoped rules instead of a dedicated rules directory. Generate nested AGENTS.md when patterns are detected. See `references/project-type-guides.md` for full per-type triggers.

**Web Backend / API**: api-conventions, database-access, error-handling
**Frontend**: component-patterns, routing-conventions, state-management
**ML / Data Science**: data-pipeline, experiment-tracking, model-conventions
**CLI Tools**: cli-conventions, output-format
**Infrastructure**: safety-rules (always), naming-conventions, secrets-management
**Autonomous Driving**: safety-invariants, sensor-pipeline, middleware-patterns
**Robotics**: ros-communication, real-time-control, launch-conventions, hardware-safety
**Embedded**: memory-safety, real-time-guarantees, hardware-access, coding-standard

When multiple cross-cutting patterns exist, generate:
1. **AGENTS.md** in affected subdirectory with the pattern rules
2. **AGENTS.override.md** only when the pattern rules need to override parent AGENTS.md

If no patterns detected for the project type, skip nested AGENTS.md generation entirely.

## Domain-Specific Guidance

Brief pointers. Full details live in reference docs, loaded on-demand when domain is detected.

### Autonomous Driving

Pipeline-centric architecture. Key concern: safety constraints that must never be violated. Each pipeline stage (Perception, Planning, Control) gets its own AGENTS.md with I/O topics, algorithm choices, and safety invariants. See `references/autonomous-driving.md`.

### Robotics (ROS2)

Multi-package workspace structure. Key concern: ROS communication layer vs core logic separation. Each package gets its own AGENTS.md with nodes, interfaces, parameters, and launch files. See `references/robotics-ros2.md`.

### Embedded & Engineering

CPS layered architecture. Key concern: mixing hardware-near and algorithm-near code. Use dual-layer AGENTS.md strategy — root describes hardware context, algorithm subdirs describe math/software without hardware noise. See `references/embedded-systems.md`.

## Commands Reference

Default commands by project type. Config file commands override these.

| Type | Build | Test | Lint | Run |
|------|-------|------|------|-----|
| Python | `pip install -e ".[dev]"` | `pytest` | `ruff check .` | `python -m <pkg>` |
| Node-Web | `<pm> install` | `<pm> test` | `<pm> run lint` | `<pm> run dev` |
| Rust | `cargo build` | `cargo test` | `cargo clippy` | `cargo run` |
| Java | `mvn compile` | `mvn test` | `mvn checkstyle:check` | `mvn exec:java` |
| Go | `go build ./...` | `go test ./...` | `golangci-lint run` | `go run .` |
| Infra | `terraform plan` | `terratest` | `tflint` | `terraform apply` |
| AutoDriving | `./apollo.sh build` | `./apollo.sh test` | `cpplint` | `./apollo.sh start` |
| Robotics | `colcon build` | `colcon test` | `ament_lint` | `ros2 launch <pkg> <file>` |
| Embedded | `cmake -B build && make -C build` | `ctest` | `cppcheck` | `openocd -f board.cfg` |

`<pm>` resolves to detected package manager (npm, yarn, pnpm, bun). For autonomous driving, detect Apollo (Bazel) vs Autoware (Colcon).

## Bundled Resources

### Scripts
- `scripts/scan_dir.py` — directory scanner with 10-type detection and monorepo recognition
- `scripts/sync_agents_md.py` — manifest-based sync tool
- `scripts/manifest.py` — sidecar state manager (hash, check, update)

### References
- `references/templates.md` — section selection table and quality rules for all 10 types
- `references/project-type-guides.md` — per-type detection checklist, conventions, anti-patterns
- `references/autonomous-driving.md` — Apollo/Autoware domain guide
- `references/robotics-ros2.md` — ROS2 workspace and package conventions
- `references/embedded-systems.md` — CPS architecture, RTOS, MISRA, dual-layer strategy

### Assets (Templates)
- `assets/root-template.md` — adaptive root AGENTS.md template (10-type conditional sections)
- `assets/subdir-template.md` — standard nested subdirectory AGENTS.md template with domain cross-references
- `assets/override-template.md` — AGENTS.override.md template for path-scoped overrides
- `assets/pipeline-module-template.md` — autonomous driving pipeline stage template
- `assets/ros2-package-template.md` — ROS2 package documentation template
- `assets/cps-layer-template.md` — embedded CPS layer template
- `assets/check-stale.py` — directory structure drift detector, run on-demand to check if AGENTS.md needs syncing
