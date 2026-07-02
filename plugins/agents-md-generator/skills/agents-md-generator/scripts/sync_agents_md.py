#!/usr/bin/env python3
"""Sync existing AGENTS.md files with current directory state.

Uses manifest-based section hash comparison to detect user edits.
Preserves manually-edited content, regenerates auto-generated sections
where hashes still match.

Usage:
    python sync_agents_md.py <project-root> [--dry-run]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_agents_md_files(root: Path) -> list:
    """Find all AGENTS.md files in project, skipping ignored dirs."""
    ignored = {".git", "node_modules", "__pycache__", ".venv", "venv",
               "dist", "build", "target", ".next", ".turbo", ".codex"}
    results = []
    for path in root.rglob("AGENTS.md"):
        if any(p in ignored for p in path.relative_to(root).parts[:-1]):
            continue
        results.append(path)
    # Also find AGENTS.override.md files
    for path in root.rglob("AGENTS.override.md"):
        if any(p in ignored for p in path.relative_to(root).parts[:-1]):
            continue
        results.append(path)
    return sorted(results)


def run_manifest(root: Path, *args: str) -> dict:
    """Run manifest.py as subprocess and return JSON result."""
    script_dir = Path(__file__).parent
    manifest_script = script_dir / "manifest.py"
    if not args:
        args = ("check",)
    cmd = [sys.executable, str(manifest_script)] + list(args) + [str(root)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running manifest.py: {result.stderr}", file=sys.stderr)
        return {"status": "error", "error": result.stderr}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "ok", "output": result.stdout}


def build_sync_report(root: Path) -> dict:
    """Build sync report: what needs updating, what's preserved, what's new."""
    manifest = run_manifest(root)
    if not isinstance(manifest, dict) or manifest.get("status") == "no_manifest":
        return {
            "status": "no_manifest",
            "message": "No manifest found. Run full generation first.",
            "actions": [],
        }

    check_result = run_manifest(root, "check")
    changes = check_result.get("changes", [])

    actions = {
        "regenerate": [],
        "preserve": [],
        "missing": [],
        "new_sections": [],
    }

    for c in changes:
        status = c.get("status", "")
        if status == "unchanged":
            actions["regenerate"].append(c)
        elif status == "modified":
            actions["preserve"].append(c)
        elif status == "missing":
            actions["missing"].append(c)
        elif status == "new":
            actions["new_sections"].append(c)

    return {"status": "ok", "actions": actions}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync AGENTS.md files with manifest")
    parser.add_argument("root", type=str, help="Project root")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    existing_files = find_agents_md_files(root)
    report = build_sync_report(root)

    print("=== AGENTS.md Sync Report ===")
    print(f"Project: {root}")
    print(f"Existing AGENTS.md files: {len(existing_files)}")
    print()

    if report["status"] == "no_manifest":
        print(report["message"])
        return

    actions = report["actions"]

    if actions["regenerate"]:
        print(f"Sections safe to regenerate ({len(actions['regenerate'])}):")
        for item in actions["regenerate"]:
            print(f"  ✓ {item.get('file', '?')}/{item.get('section', '?')}")
        print()

    if actions["preserve"]:
        print(f"Sections to preserve - user edited ({len(actions['preserve'])}):")
        for item in actions["preserve"]:
            print(f"  🔒 {item.get('file', '?')}/{item.get('section', '?')}")
        print()

    if actions["missing"]:
        print(f"Sections removed from file ({len(actions['missing'])}):")
        for item in actions["missing"]:
            print(f"  ✗ {item.get('file', '?')}/{item.get('section', '?')}")
        print()

    if actions["new_sections"]:
        print(f"New sections added by user ({len(actions['new_sections'])}):")
        for item in actions["new_sections"]:
            print(f"  + {item.get('file', '?')}/{item.get('section', '?')}")
        print()

    if args.dry_run:
        print("[Dry run -- no changes applied]")
    else:
        print("Run the full generation workflow to apply changes.")
        print("Use the SKILL.md workflow to regenerate with preserved sections.")


if __name__ == "__main__":
    main()
