#!/usr/bin/env python3
"""SessionStart hook: detect directory structure drift and remind AI to sync CLAUDE.md.

Compares the current directory tree fingerprint against a saved snapshot in
.claude/.dir-state.json. If the structure changed (directories added, removed,
or renamed), emits a system-reminder that the harness injects into the session.

Only directories are tracked — file-level changes are ignored. The fingerprint
is updated after each check so the same delta won't re-alert.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_ignore_patterns(root: Path) -> set[str]:
    patterns = {
        ".git", "node_modules", "__pycache__", ".venv", "venv", ".tox",
        "dist", "build", "target", ".next", ".nuxt", ".cache",
        ".claude", ".codex", "coverage", ".pytest_cache", ".mypy_cache",
    }
    gitignore = root / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                patterns.add(stripped.rstrip("/"))
    return patterns


def get_dir_fingerprint(root: Path, ignore: set[str]) -> str:
    dirs = []
    for entry in sorted(root.rglob("*")):
        if not entry.is_dir():
            continue
        parts = entry.relative_to(root).parts
        if any(p in ignore or (p.startswith(".") and p != ".") for p in parts):
            continue
        dirs.append(str(entry.relative_to(root)))
    return hashlib.sha256("\n".join(dirs).encode()).hexdigest()


def main() -> None:
    root = Path.cwd()

    claude_md = root / "CLAUDE.md"
    claude_md_alt = root / ".claude" / "CLAUDE.md"
    if not claude_md.exists() and not claude_md_alt.exists():
        sys.exit(0)

    state_file = root / ".claude" / ".dir-state.json"
    ignore = get_ignore_patterns(root)
    current_fp = get_dir_fingerprint(root, ignore)

    previous_fp = None
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            previous_fp = state.get("fingerprint")
        except (json.JSONDecodeError, KeyError):
            pass

    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({
        "fingerprint": current_fp,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2))

    if previous_fp and previous_fp != current_fp:
        print(
            "Directory structure has changed since last session. "
            "Review root CLAUDE.md AND all subdirectory CLAUDE.md files. "
            "Run /claude-md-generator to sync any that no longer match "
            "the module layout.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
