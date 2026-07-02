#!/usr/bin/env python3
"""Scan a project directory and output a structured JSON tree report.

Applies ignore rules from .gitignore and built-in patterns, classifies files by type,
and reports file counts per directory. Used by claude-md-generator to decide where
CLAUDE.md files are needed.

Usage:
    python scan_dir.py <project-root> [--max-depth 3] [--output /tmp/scan.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Optional

# Directories always ignored
ALWAYS_IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", ".eggs",
    "dist", "build", "target", "out", ".next", ".nuxt", ".cache", ".turbo",
    ".idea", ".vscode", ".history", ".Trashes",
}

# Patterns for files always ignored
ALWAYS_IGNORE_PATTERNS = [
    "*.pyc", "*.pyo", "*.so", "*.o", "*.a", "*.dylib", "*.dll", "*.wasm",
    "*.class", "*.jar", "*.war", "*.dex",
    ".DS_Store", "Thumbs.db", "*.tmp", "*.swp", "*.swo", "*~",
    "*.egg-info", "*.dist-info",
    "__MACOSX",
]

# Directories containing generated/support files
IGNORE_DIR_PATTERNS = [
    "coverage", ".nyc_output", ".pytest_cache", "htmlcov",
    "*.egg-info", "*.dist-info",
]

# Files that should never appear in generated output
SENSITIVE_PATTERNS = [
    ".env", ".env.*", "*.key", "*.pem", "*.p12", "*.pfx",
    "credentials*", "secrets*", "*.secret", "id_rsa*", "*.pem",
]

# Max file size to consider (1 MB) - larger files are skipped
MAX_FILE_SIZE = 1_048_576


def read_gitignore(root: Path) -> list[str]:
    """Parse .gitignore and return list of patterns."""
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return []
    patterns = []
    with open(gitignore) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line.rstrip("/"))
    return patterns


def should_ignore_path(
    path: Path,
    root: Path,
    ignore_patterns: list[str],
    is_dir: bool,
) -> bool:
    """Check if a path should be ignored."""
    name = path.name
    rel = str(path.relative_to(root))

    # Check always-ignore directories
    if is_dir and name in ALWAYS_IGNORE_DIRS:
        return True

    # Check always-ignore patterns for files
    if not is_dir:
        for pattern in ALWAYS_IGNORE_PATTERNS:
            if fnmatch(name, pattern):
                return True

    # Check sensitive files
    if not is_dir:
        for pattern in SENSITIVE_PATTERNS:
            if fnmatch(name, pattern):
                return True

    # Check .gitignore patterns
    for pattern in ignore_patterns:
        if fnmatch(name, pattern) or fnmatch(rel, pattern):
            return True
        # Handle directory patterns like "build/" matching "build"
        if is_dir and pattern.endswith("/") and fnmatch(name, pattern.rstrip("/")):
            return True

    return False


def classify_file(path: Path, root: Path, project_type: str = "generic") -> str:
    """Classify a file by its role in the project."""
    name = path.name.lower()
    parent = path.parent.name.lower()

    # --- Domain-specific classifications first ---

    # Autonomous Driving
    if project_type == "autonomous-driving":
        if name.endswith((".pb.txt", ".proto")):
            return "config"
        if name.endswith((".urdf", ".urdf.xacro", ".sdf")):
            return "assets"
        if "launch" in name and name.endswith((".xml", ".py")):
            return "entry_point"

    # Robotics / ROS2
    if project_type == "robotics":
        if name == "package.xml":
            return "config"
        if name.endswith((".msg", ".srv", ".action")):
            return "source"
        if "launch" in name and name.endswith((".xml", ".py")):
            return "entry_point"
        if name.endswith((".urdf", ".urdf.xacro", ".sdf", ".world")):
            return "assets"

    # Embedded
    if project_type == "embedded":
        if name.endswith((".ld", ".s", ".S")):
            return "config"
        if name.endswith((".dts", ".dtsi", ".ioc", ".prj")):
            return "config"
        if name in ("freertosconfig.h", "rtos_config.h", "sdkconfig", "kconfig"):
            return "config"
        if name.endswith((".sch", ".brd", ".kicad_pcb", ".bdf", ".xdc")):
            return "assets"
        if name.startswith("startup_"):
            return "entry_point"

    # --- Standard classifications (unchanged from v1) ---

    # Entry points
    if name in ("main.py", "main.rs", "index.js", "index.ts", "index.tsx",
                 "app.tsx", "app.ts", "lib.rs", "manage.py", "wsgi.py", "asgi.py"):
        return "entry_point"

    # Config files
    config_names = (
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
        "package.json", "tsconfig.json", "vite.config.ts", "vite.config.js",
        "webpack.config.js", "next.config.js", "tailwind.config.ts",
        "cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
        "go.mod", "cmakelists.txt", "makefile", "dockerfile",
        "docker-compose.yml", "docker-compose.yaml", ".env.example",
        "mkdocs.yml", "eslint.config.js", "eslint.config.ts",
    )
    if name in config_names:
        return "config"

    # Test files
    if "test" in name or "test" in parent or "spec" in name or "spec" in parent:
        return "test"

    # Documentation
    if name.endswith((".md", ".rst", ".txt")) or name in ("readme", "changelog", "contributing", "license"):
        return "docs"

    # Assets
    asset_extensions = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
                        ".ttf", ".eot", ".mp4", ".webm", ".mp3", ".wav", ".pdf")
    if path.suffix.lower() in asset_extensions:
        return "assets"

    # Source code (by extension)
    source_extensions = (".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java",
                         ".kt", ".scala", ".c", ".cpp", ".h", ".hpp", ".cc", ".cs",
                         ".rb", ".php", ".swift", ".vue", ".svelte", ".css", ".scss",
                         ".less", ".html", ".htm", ".sql", ".graphql", ".gql", ".proto",
                         ".yaml", ".yml", ".toml", ".json", ".xml")
    if path.suffix.lower() in source_extensions:
        return "source"

    return "other"


def scan_directory(
    root: Path,
    current: Path,
    max_depth: int,
    current_depth: int,
    ignore_patterns: list,
    project_type: str = "generic",
) -> Optional[dict]:
    """Recursively scan a directory and return its structure."""
    if current_depth > max_depth:
        return None

    result = {
        "name": current.name if current != root else ".",
        "path": str(current.relative_to(root)) if current != root else ".",
        "type": "directory",
        "files": [],
        "subdirs": [],
        "file_count": 0,
        "total_file_count": 0,
    }

    try:
        entries = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return None

    file_count = 0
    for entry in entries:
        if should_ignore_path(entry, root, ignore_patterns, entry.is_dir()):
            continue

        if entry.is_dir():
            subdir = scan_directory(root, entry, max_depth, current_depth + 1, ignore_patterns, project_type)
            if subdir:
                result["subdirs"].append(subdir)
                file_count += subdir["total_file_count"]
        elif entry.is_file():
            # Skip large files
            try:
                if entry.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            classification = classify_file(entry, root, project_type)
            result["files"].append({
                "name": entry.name,
                "path": str(entry.relative_to(root)),
                "type": classification,
            })
            file_count += 1

    result["file_count"] = len(result["files"])
    result["total_file_count"] = file_count
    return result


def detect_project_type(root: Path) -> str:
    """Detect the project type based on characteristic files. Returns one of 10 types."""
    files = {f.name.lower() for f in root.iterdir() if f.is_file()}
    dirs = {d.name.lower() for d in root.iterdir() if d.is_dir()}

    # --- Autonomous Driving: Apollo pattern ---
    if "modules" in dirs:
        modules_dir = root / "modules"
        if modules_dir.is_dir():
            module_subdirs = {d.name.lower() for d in modules_dir.iterdir() if d.is_dir()}
            pipeline_dirs = {"perception", "planning", "control", "prediction", "routing"}
            if len(module_subdirs & pipeline_dirs) >= 3:
                return "autonomous-driving"
            if "cyber" in dirs:
                return "autonomous-driving"

    # --- Autonomous Driving: Autoware pattern ---
    autoware_markers = ("autoware.repos",)
    if any(k in files for k in autoware_markers):
        return "autonomous-driving"
    # .repos file with autoware content
    for f_name in files:
        if f_name.endswith(".repos"):
            try:
                content = (root / f_name).read_text()
                if "autoware" in content.lower():
                    return "autonomous-driving"
            except OSError:
                pass

    # --- Robotics: ROS2 workspace ---
    has_package_xml = False
    for d in dirs:
        pkg_dir = root / d
        if pkg_dir.is_dir() and (pkg_dir / "package.xml").exists():
            has_package_xml = True
            break
    if has_package_xml:
        ros2_dirs = {d for d in dirs if any(
            d.endswith(suffix) for suffix in
            ("_msgs", "_control", "_bringup", "_description", "_simulation", "_navigation")
        )}
        if len(ros2_dirs) >= 2 or any(f.endswith((".urdf", ".urdf.xacro")) for f in files):
            return "robotics"

    # --- Embedded: RTOS config ---
    for f_name in files:
        f_lower = f_name.lower()
        if f_lower in ("freertosconfig.h", "rtos_config.h", "sdkconfig", "kconfig",
                        "platformio.ini"):
            return "embedded"

    # --- Embedded: linker scripts + startup ---
    linker_files = [f for f in files if f.endswith(".ld") or f.startswith("startup_")]
    if linker_files:
        cmake_files = [f for f in files if f.endswith(".cmake") or f == "cmakelists.txt"]
        if cmake_files:
            return "embedded"

    # --- Embedded: MCU config files ---
    if any(f.endswith(".ioc") for f in files):
        return "embedded"

    # --- Embedded: Zephyr device trees ---
    if any(f.endswith((".dts", ".dtsi")) for f in files):
        return "embedded"

    # --- Infrastructure / DevOps ---
    if any(f.endswith((".tf", ".tfvars")) for f in files):
        return "infra"
    if any(d in dirs for d in ("k8s", "kubernetes", "helm", "playbooks")):
        return "infra"
    # Ansible check
    if any(f.endswith(".yml") and "playbook" in f for f in files):
        return "infra"

    # --- Standard software types ---
    if "package.json" in files:
        try:
            with open(root / "package.json") as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if any(k in deps for k in ("react", "vue", "next", "nuxt", "svelte")):
                return "node-web"
            return "node-web"
        except (json.JSONDecodeError, OSError):
            return "node-web"

    if any(k in files for k in ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt")):
        return "python"

    if "cargo.toml" in files:
        return "rust"

    if any(k in files for k in ("pom.xml", "build.gradle", "build.gradle.kts")):
        return "java"

    if "go.mod" in files:
        return "go"

    if "cmakelists.txt" in files:
        return "generic"

    return "generic"


def detect_monorepo(root: Path, project_type: str) -> bool:
    """Check if project is a monorepo."""
    files = {f.name.lower() for f in root.iterdir() if f.is_file()}

    if project_type == "node-web":
        if any(k in files for k in ("pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json")):
            return True
        if "package.json" in files:
            try:
                with open(root / "package.json") as f:
                    pkg = json.load(f)
                if pkg.get("workspaces"):
                    return True
            except (json.JSONDecodeError, OSError):
                pass

    if project_type == "rust":
        if "cargo.toml" in files:
            try:
                content = (root / "cargo.toml").read_text()
                if "[workspace]" in content:
                    return True
            except OSError:
                pass

    if project_type == "python":
        pkg_dirs = [d for d in root.iterdir()
                     if d.is_dir() and (d / "pyproject.toml").exists()
                     and d.name not in (".git", "__pycache__", ".venv", "venv")]
        if len(pkg_dirs) > 1:
            return True

    if project_type == "java":
        if any(k in files for k in ("settings.gradle", "settings.gradle.kts")):
            return True
        if "pom.xml" in files:
            try:
                content = (root / "pom.xml").read_text()
                if "<modules>" in content:
                    return True
            except OSError:
                pass

    if project_type == "go":
        if "go.work" in files:
            return True

    if project_type == "robotics":
        src_dir = root / "src"
        if src_dir.is_dir():
            packages = [d for d in src_dir.iterdir()
                        if d.is_dir() and (d / "package.xml").exists()]
            if len(packages) > 2:
                return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Scan project directory for CLAUDE.md generation")
    parser.add_argument("root", type=str, help="Project root directory")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum scan depth")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    ignore_patterns = read_gitignore(root)
    project_type = detect_project_type(root)
    is_monorepo = detect_monorepo(root, project_type)

    tree = scan_directory(root, root, args.max_depth, 0, ignore_patterns, project_type)

    report = {
        "project_root": str(root),
        "project_type": project_type,
        "is_monorepo": is_monorepo,
        "max_depth": args.max_depth,
        "ignore_patterns": ignore_patterns,
        "tree": tree,
    }

    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Scan report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
