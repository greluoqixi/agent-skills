#!/usr/bin/env python3
""".claude/.claude-md-state.json manifest manager.

Replaces the old HTML-comment approach (<!-- AUTO-GENERATED -->) which gets
stripped by Claude Code. Instead, section state is tracked via a JSON manifest
at .claude/.claude-md-state.json using SHA-256 hashes.

Used by both generation and sync workflows.

Usage:
    python manifest.py init <root> [project-type]
    python manifest.py hash-section [text]
    python manifest.py check <root>
    python manifest.py update <root> [logical_path real_path ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

MANIFEST_DIR = ".claude"
MANIFEST_FILE = ".claude-md-state.json"

# Matches ## or ### markdown headings
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$")


# ---------------------------------------------------------------------------
# Core hash function
# ---------------------------------------------------------------------------


def hash_section(text: str) -> str:
    """SHA-256 of normalized text (whitespace collapsed), return first 16 hex chars.

    Normalization strips leading/trailing whitespace and collapses all runs of
    whitespace into single spaces so that formatting-only changes don't break
    the sync comparison.
    """
    normalized = re.sub(r"\s+", " ", text.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------


def _manifest_path(root: Path) -> Path:
    """Return the full path to the manifest file under *root*."""
    return root / MANIFEST_DIR / MANIFEST_FILE


def load_manifest(root: Path) -> Optional[dict]:
    """Load an existing manifest, or return ``None`` if none exists."""
    path = _manifest_path(root)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_manifest(root: Path, data: dict):
    """Write *data* to the manifest file, creating ``.claude/`` if needed."""
    dir_path = root / MANIFEST_DIR
    dir_path.mkdir(parents=True, exist_ok=True)
    path = _manifest_path(root)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def init_manifest(root: Path, project_type: str) -> dict:
    """Create a new empty manifest for *project_type* and save it.

    Returns the newly created manifest dict.
    """
    data: dict = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_type": project_type,
        "files": {},
    }
    save_manifest(root, data)
    return data


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------


def extract_sections(filepath: Path) -> dict:
    """Parse a markdown file into ``{section_name: {body, start_line, end_line}}``.

    Sections are defined by ``##`` or ``###`` markdown headings.  The section
    name is the heading text lowercased with whitespace replaced by hyphens.
    The section body spans from the heading line (inclusive) to the line before
    the next heading (exclusive), or to end-of-file for the last section.
    """
    if not filepath.exists():
        return {}

    lines = filepath.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    sections: dict = {}

    current_name: Optional[str] = None
    current_start: Optional[int] = None  # 1-based line number

    for i, line in enumerate(lines, 1):
        match = HEADING_RE.match(line)
        if not match:
            continue

        # Close the previous section when a new heading is found.
        if current_name is not None and current_start is not None:
            body_lines = lines[current_start - 1 : i - 1]
            sections[current_name] = {
                "body": "\n".join(body_lines),
                "start_line": current_start,
                "end_line": i - 1,
            }

        heading_text = match.group(2).strip()
        current_name = re.sub(r"\s+", "-", heading_text.lower())
        current_start = i

    # Close the last section.
    if current_name is not None and current_start is not None:
        body_lines = lines[current_start - 1 :]
        sections[current_name] = {
            "body": "\n".join(body_lines),
            "start_line": current_start,
            "end_line": total_lines,
        }

    return sections


def compute_manifest_sections(filepath: Path) -> dict:
    """Compute ``{section_name: {hash, line_range}}`` for a markdown file.

    This is the data that gets stored in the manifest for each CLAUDE.md file.
    """
    sections = extract_sections(filepath)
    result: dict = {}
    for name, info in sections.items():
        result[name] = {
            "hash": hash_section(info["body"]),
            "line_range": [info["start_line"], info["end_line"]],
        }
    return result


# ---------------------------------------------------------------------------
# Diff / check
# ---------------------------------------------------------------------------


def check_manifest(root: Path) -> dict:
    """Compare manifest against actual files on disk and return a diff.

    The returned dict has one key per file (as listed in the manifest).
    Each value is another dict with keys ``unchanged``, ``modified``,
    ``missing``, and ``new``, each holding a list of section names in
    that category.
    """
    manifest = load_manifest(root)
    if manifest is None:
        return {
            "error": "no_manifest",
            "message": f"No manifest found at {_manifest_path(root)}",
        }

    result: dict = {}

    for logical_path, file_info in manifest.get("files", {}).items():
        real_path = (root / logical_path).resolve()

        if not real_path.exists():
            result[logical_path] = {
                "error": "file_not_found",
                "message": f"File not found: {real_path}",
            }
            continue

        stored_sections = file_info.get("sections", {})
        current_sections = compute_manifest_sections(real_path)

        file_result: Dict[str, list] = {
            "unchanged": [],
            "modified": [],
            "missing": [],
            "new": [],
        }

        all_names = set(stored_sections.keys()) | set(current_sections.keys())

        for name in sorted(all_names):
            in_stored = name in stored_sections
            in_current = name in current_sections

            if in_stored and in_current:
                if stored_sections[name]["hash"] == current_sections[name]["hash"]:
                    file_result["unchanged"].append(name)
                else:
                    file_result["modified"].append(name)
            elif in_stored:
                file_result["missing"].append(name)
            else:
                file_result["new"].append(name)

        result[logical_path] = file_result

    return result


def update_manifest_after_generation(
    root: Path, files_generated: Dict[str, Path]
) -> dict:
    """Update manifest after generating (or regenerating) CLAUDE.md files.

    Parameters
    ----------
    root:
        Project root directory.
    files_generated:
        Mapping of logical manifest paths (e.g. ``"./CLAUDE.md"``) to the
        actual file on disk whose sections should be recorded.

    Returns
    -------
    The updated (and saved) manifest dict.
    """
    manifest = load_manifest(root)
    if manifest is None:
        # Auto-create with a sensible default when no manifest exists yet.
        manifest = {
            "version": 1,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "project_type": "unknown",
            "files": {},
        }

    manifest["generated_at"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    for logical_path, real_path in files_generated.items():
        if not real_path.exists():
            continue

        sections = compute_manifest_sections(real_path)

        if logical_path not in manifest["files"]:
            manifest["files"][logical_path] = {
                "sections": {},
                "manual_sections": [],
            }

        manifest["files"][logical_path]["sections"] = sections
        # Ensure the key exists for files that were pre-populated.
        manifest["files"][logical_path].setdefault("manual_sections", [])

    save_manifest(root, manifest)
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage .claude/.claude-md-state.json manifest files"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ----- init -----
    init_parser = subparsers.add_parser("init", help="Create a new manifest")
    init_parser.add_argument("root", type=str, help="Project root directory")
    init_parser.add_argument(
        "project_type",
        type=str,
        nargs="?",
        default="unknown",
        help="Project type (python, nodejs, rust, etc.)",
    )

    # ----- hash-section -----
    hash_parser = subparsers.add_parser(
        "hash-section", help="Compute SHA-256 hash (first 16 hex chars) of text"
    )
    hash_parser.add_argument(
        "text",
        type=str,
        nargs="?",
        default=None,
        help="Text to hash (reads from stdin if omitted)",
    )

    # ----- check -----
    check_parser = subparsers.add_parser(
        "check", help="Compare manifest against actual files on disk"
    )
    check_parser.add_argument("root", type=str, help="Project root directory")

    # ----- update -----
    update_parser = subparsers.add_parser(
        "update", help="Update manifest after generating CLAUDE.md files"
    )
    update_parser.add_argument("root", type=str, help="Project root directory")
    update_parser.add_argument(
        "pairs",
        type=str,
        nargs="*",
        metavar="logical_path real_path",
        help="Pairs of logical manifest path and real file path",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        root = Path(args.root).resolve()
        if not root.is_dir():
            print(f"Error: {root} is not a directory", file=sys.stderr)
            sys.exit(1)
        manifest = init_manifest(root, args.project_type)
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    elif args.command == "hash-section":
        if args.text is not None:
            text = args.text
        else:
            text = sys.stdin.read()
        print(hash_section(text))

    elif args.command == "check":
        root = Path(args.root).resolve()
        if not root.is_dir():
            print(f"Error: {root} is not a directory", file=sys.stderr)
            sys.exit(1)
        result = check_manifest(root)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "update":
        root = Path(args.root).resolve()
        if not root.is_dir():
            print(f"Error: {root} is not a directory", file=sys.stderr)
            sys.exit(1)

        if len(args.pairs) % 2 != 0:
            print(
                "Error: update requires an even number of arguments "
                "(logical_path real_path pairs)",
                file=sys.stderr,
            )
            sys.exit(1)

        files_generated: Dict[str, Path] = {}
        for i in range(0, len(args.pairs), 2):
            logical = args.pairs[i]
            real = Path(args.pairs[i + 1]).resolve()
            files_generated[logical] = real

        manifest = update_manifest_after_generation(root, files_generated)
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
