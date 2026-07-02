---
name: claude-md-generator
description: Generate and maintain CLAUDE.md files as intelligent codebase indexes. Use this skill whenever starting work in a new repository, when project structure changes, when asked to generate/update/create CLAUDE.md, or when needing to understand project architecture before making changes. Supports 10 project types including autonomous driving, robotics, and embedded systems. Automatically detects project type, generates root CLAUDE.md, subdirectory indexes, .claude/rules/ path-scoped rules, and CLAUDE.local.md personal overrides.
---

# CLAUDE.md Generator

Generate and maintain CLAUDE.md files as intelligent, navigable indexes for AI working in unfamiliar codebases. The core problem: AI lands in a new repo and doesn't know which files matter, where the entry points are, or how modules relate. A well-structured CLAUDE.md answers those questions immediately.

## When to Use

Triggers automatically when:
- Starting work in a new repository or unfamiliar codebase
- Project structure has changed (files added, removed, renamed, reorganized)
- User asks to generate, update, or create CLAUDE.md or "project docs for AI"
- After major refactors that change module layout

Do NOT use for: single-file README updates, human-facing documentation (use doc-coauthoring), or writing code comments/docstrings.

## Core Principles

Explain these to the user only if they ask why certain decisions were made.

### The 200-Line Limit

Claude Code's system prompt has limited instruction capacity. Every line in CLAUDE.md consumes a slot. **Soft limit 200, hard stop 250** — if a file exceeds 250 lines, push detail to subdirectory CLAUDE.md files or `.claude/rules/`.

### The Delete Test

For every line: **"If I deleted this line, would Claude make a mistake?"** If no, delete it. This eliminates generic advice ("write clean code"), language-default conventions ("use 4-space indent"), and information Claude can infer from config files ("this project uses React 18").

### Progressive Disclosure

The root CLAUDE.md is a navigation hub, not a manual. Point to deeper docs:
- `@README.md` bridges the human-facing README
- `@AGENTS.md` bridges existing cross-tool agent docs
- Subdirectory CLAUDE.md files load on-demand when Claude reads that directory
- `.claude/rules/` rules load when Claude reads matching files

### Manifest-Based Sync

Generated CLAUDE.md files are tracked via `.claude/.claude-md-state.json`, which stores SHA-256 hashes of each section. During sync, sections whose hash matches the manifest are safe to regenerate. Sections whose hash differs were user-edited and are preserved. See `scripts/manifest.py` for the implementation.

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
3. **Check for AGENTS.md** — if present, generated CLAUDE.md bridges it with `@AGENTS.md`.
4. **Read .gitignore** and other ignore files for directory filtering.
5. **Read .claude/settings.json** — detect hooks to reference as "automated" in output.
6. **Read README.md** first paragraph for project description.

### Phase 2: Scan

Run `scripts/scan_dir.py <root> --max-depth 3` (or manual find/glob as fallback).

The scanner output provides:
- Full directory tree with file counts and classifications
- Project type and monorepo status
- Ignore patterns applied

From this, determine:
- Which directories need CLAUDE.md (>15 files or >3 subdirs; lowered thresholds for specialized domains)
- Which cross-directory patterns trigger `.claude/rules/` generation
- Which config files to read for metadata extraction

### Phase 3: Generate

Produce up to 4 product types:

**Root CLAUDE.md** (`./CLAUDE.md` or `./.claude/CLAUDE.md`):
Read `assets/root-template.md` for structure. Section selection adapts to project type per the table in `references/templates.md`. Key decisions:
- Domain-specific sections (pipeline, CPS layers, safety) only for specialized types
- Standard software sections (auth, DB, data) only when relevant
- Every section passes the delete test
- Commands section: only what can't be inferred from config files

**Subdirectory CLAUDE.md** (`./<module>/CLAUDE.md`):
Read `assets/subdir-template.md` for structure. Template adapts:
- Standard projects → basic module template
- Autonomous driving pipeline stages → `assets/pipeline-module-template.md`
- ROS2 packages → `assets/ros2-package-template.md`
- Embedded CPS layers → `assets/cps-layer-template.md`

**Path-scoped rules** (`./.claude/rules/<name>.md`):
Read `assets/rules-template.md`. Generate only when cross-directory patterns are detected per type (see Rules Generation section below).

**Local overrides** (`./CLAUDE.local.md`):
Read `assets/local-template.md`. Generate only when local toolchain differences are detected (personal conda env name, local port preferences).

**Update manifest**: After all files are written, run `python scripts/manifest.py update <root>` to compute and store section hashes.

**Ask user** if ambiguous information encountered (unclear module purpose, ambiguous entry points, unclear architecture flow). Questions are single-choice or short-answer.

### Phase 4: Verify

Before presenting results:
1. **Line count**: Each file ≤250 lines. Push to subdir/rules if over.
2. **Sensitive data scan**: No `.env`, passwords, secrets, keys in output.
3. **Commands copy-paste check**: Every command is runnable from project root.
4. **Delete test**: Re-skim each line.
5. **Report summary**: What was generated, key findings, any preserved sections.

## Sync Mode

When CLAUDE.md files already exist and user asks to update:

1. Run `python scripts/manifest.py check <root>` to compare hashes.
2. Sections with matching hashes → safe to regenerate.
3. Sections with changed hashes → user edited, preserve.
4. Run Phase 1-2 of generation, then regenerate only safe sections in Phase 3.
5. Update manifest after regeneration.
6. Report preserved vs regenerated sections to user.

If no manifest exists, offer to do a full regeneration.

## Rules Generation Triggers

Only generate `.claude/rules/` when patterns are detected. See `references/project-type-guides.md` for full per-type triggers.

**Web Backend / API**: api-conventions, database-access, error-handling
**Frontend**: component-patterns, routing-conventions, state-management
**ML / Data Science**: data-pipeline, experiment-tracking, model-conventions
**CLI Tools**: cli-conventions, output-format
**Infrastructure**: safety-rules (always), naming-conventions, secrets-management
**Autonomous Driving**: safety-invariants, sensor-pipeline, middleware-patterns
**Robotics**: ros-communication, real-time-control, launch-conventions, hardware-safety
**Embedded**: memory-safety, real-time-guarantees, hardware-access, coding-standard

If no patterns detected for the project type, skip rules generation entirely.

## Domain-Specific Guidance

Brief pointers. Full details live in reference docs, loaded on-demand when domain is detected.

### Autonomous Driving

Pipeline-centric architecture. Key concern: safety constraints that must never be violated. Each pipeline stage (Perception, Planning, Control) gets its own CLAUDE.md with I/O topics, algorithm choices, and safety invariants. See `references/autonomous-driving.md`.

### Robotics (ROS2)

Multi-package workspace structure. Key concern: ROS communication layer vs core logic separation. Each package gets its own CLAUDE.md with nodes, interfaces, parameters, and launch files. See `references/robotics-ros2.md`.

### Embedded & Engineering

CPS layered architecture. Key concern: mixing hardware-near and algorithm-near code. Use dual-layer CLAUDE.md strategy — root describes hardware context, algorithm subdirs describe math/software without hardware noise. See `references/embedded-systems.md`.

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
- `scripts/sync_claude_md.py` — manifest-based sync tool
- `scripts/manifest.py` — sidecar state manager (hash, check, update)

### References
- `references/templates.md` — section selection table and quality rules for all 10 types
- `references/project-type-guides.md` — per-type detection checklist, conventions, anti-patterns
- `references/autonomous-driving.md` — Apollo/Autoware domain guide
- `references/robotics-ros2.md` — ROS2 workspace and package conventions
- `references/embedded-systems.md` — CPS architecture, RTOS, MISRA, dual-layer strategy

### Assets (Templates)
- `assets/root-template.md` — adaptive root CLAUDE.md template (10-type conditional sections)
- `assets/subdir-template.md` — standard subdirectory template with domain cross-references
- `assets/rules-template.md` — `.claude/rules/` path-scoped rule template
- `assets/local-template.md` — `CLAUDE.local.md` personal override template
- `assets/pipeline-module-template.md` — autonomous driving pipeline stage template
- `assets/ros2-package-template.md` — ROS2 package documentation template
- `assets/cps-layer-template.md` — embedded CPS layer template
