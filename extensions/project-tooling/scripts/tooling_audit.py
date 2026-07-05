#!/usr/bin/env python3
"""Read-only, secret-safe project tooling inventory and policy comparison."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKIP = {".git", ".dart_tool", "build", "dist", "node_modules", "Pods", "vendor"}
COMMANDS = {
    "git": ["git", "--version"], "docker": ["docker", "--version"],
    "dotnet": ["dotnet", "--version"], "fvm": ["fvm", "--version"],
    "flutter": ["flutter", "--version"], "dart": ["dart", "--version"],
    "node": ["node", "--version"], "npm": ["npm", "--version"],
    "python3": ["python3", "--version"], "uv": ["uv", "--version"],
    "xcrun": ["xcrun", "--version"], "adb": ["adb", "version"],
}
NAMES = {
    ".fvmrc", ".tool-versions", "global.json", "package.json", "pubspec.yaml",
    "pyproject.toml", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml", "Podfile", "Gemfile", "go.mod", "Cargo.toml",
    "gradle-wrapper.properties", "settings.gradle", "settings.gradle.kts",
}


def run(command: list[str]) -> dict[str, Any]:
    path = shutil.which(command[0])
    if not path:
        return {"installed": False, "path": None, "version": None}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
        lines = (result.stdout or result.stderr).strip().splitlines()
        return {"installed": True, "path": path, "version": lines[0][:300] if lines else None,
                "exit_code": result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"installed": True, "path": path, "version": None, "error": type(exc).__name__}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def files(root: Path) -> list[Path]:
    result: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in names:
            if name in NAMES or name.endswith((".csproj", ".sln")):
                result.append(Path(current) / name)
    return sorted(result)


def manifests(root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in files(root):
        item: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "kind": path.name,
                                "declared": {}}
        if path.name in {".fvmrc", "global.json", "package.json"}:
            data = load_json(path)
            if isinstance(data, dict) and path.name == ".fvmrc":
                item["declared"]["flutter"] = data.get("flutter")
            elif isinstance(data, dict) and path.name == "global.json":
                item["declared"]["dotnet"] = data.get("sdk", {}).get("version")
            elif isinstance(data, dict):
                item["declared"]["engines"] = data.get("engines", {})
                item["declared"]["scripts"] = sorted((data.get("scripts") or {}).keys())
                item["declared"]["dependencies"] = sorted(set(data.get("dependencies") or {}) |
                                                                set(data.get("devDependencies") or {}))
        elif path.suffix == ".csproj":
            try:
                tree = ET.parse(path)
                item["declared"]["target_frameworks"] = [e.text for e in tree.findall(".//TargetFramework") + tree.findall(".//TargetFrameworks") if e.text]
                item["declared"]["packages"] = [e.attrib["Include"] for e in tree.findall(".//PackageReference") if "Include" in e.attrib]
            except (OSError, ET.ParseError):
                item["parse_error"] = True
        result.append(item)
    return result


def ci(root: Path) -> list[dict[str, Any]]:
    pattern = re.compile(r"\b(dotnet|docker|fvm|flutter|dart|npm|pnpm|yarn|pytest|uv|gradle|xcodebuild|adb)\b")
    result: list[dict[str, Any]] = []
    base = root / ".github" / "workflows"
    for path in sorted(base.glob("*.y*ml")) if base.exists() else []:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern.search(line) and not re.search(r"(?i)(token|password|secret)\s*[:=]", line):
                result.append({"path": path.relative_to(root).as_posix(), "line": number,
                               "command_hint": line.strip()[:300]})
    return result


def skills(root: Path) -> list[dict[str, Any]]:
    locations = [root / ".agents" / "skills", root / ".codex" / "skills",
                 Path.home() / ".codex" / "skills", Path.home() / "flutter-proj" / "my-skills" / "skills"]
    seen: set[Path] = set()
    result: list[dict[str, Any]] = []
    for base in locations:
        if not base.exists():
            continue
        for path in base.glob("*/SKILL.md"):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = path.read_text(encoding="utf-8", errors="replace")[:2000]
            match = re.search(r"(?m)^name:\s*[\"']?([^\n\"']+)", text)
            result.append({"name": match.group(1).strip() if match else path.parent.name,
                           "installed": True, "path": str(path)})
    return sorted(result, key=lambda item: (item["name"], item["path"]))


def inventory(root: Path) -> dict[str, Any]:
    return {"schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root), "environment": {"system": platform.system(),
            "release": platform.release(), "machine": platform.machine()},
            "tools": {name: run(command) for name, command in COMMANDS.items()},
            "manifests": manifests(root), "executed_hints": ci(root), "skills": skills(root),
            "notes": ["Declared, imported, executed, installed, and required are distinct states.",
                      "No secret values are read from environment or repository configuration."]}


def number(text: str | None) -> tuple[int, ...] | None:
    match = re.search(r"(\d+(?:\.\d+)+)", text or "")
    return tuple(map(int, match.group(1).split("."))) if match else None


def compare(data: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    result: list[dict[str, Any]] = []
    for name, expected in (policy.get("tools") or {}).items():
        actual = data["tools"].get(name, {"installed": False})
        status = "ok"
        if expected.get("required", True) and not actual.get("installed"):
            status = "missing"
        actual_number = number(actual.get("version"))
        if status == "ok" and expected.get("exact") and actual_number != number(str(expected["exact"])):
            status = "conflict"
        minimum = number(str(expected.get("minimum", "")))
        if status == "ok" and minimum and (actual_number is None or actual_number < minimum):
            status = "conflict"
        result.append({"kind": "tool", "name": name, "status": status,
                       "required": expected, "actual": actual})
    installed_skills = {item["name"] for item in data["skills"]}
    for name in policy.get("skills") or []:
        result.append({"kind": "skill", "name": name,
                       "status": "ok" if name in installed_skills else "missing"})
    return {"schema_version": "1.0", "results": result,
            "ok": all(item["status"] == "ok" for item in result)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["audit", "check", "propose"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy")
    parser.add_argument("--output")
    args = parser.parse_args()
    data = inventory(Path(args.root).resolve())
    payload: dict[str, Any] = data
    if args.mode != "audit":
        if not args.policy:
            parser.error("--policy is required for check/propose")
        policy = load_json(Path(args.policy))
        if not isinstance(policy, dict):
            parser.error("policy must be valid JSON")
        checked = compare(data, policy)
        payload = checked if args.mode == "check" else {
            "schema_version": "1.0", "requires_confirmation": True,
            "actions": [item for item in checked["results"] if item["status"] != "ok"],
            "note": "Approve exact manager-specific commands before mutation; this script never installs tools."
        }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 2 if args.mode == "check" and not payload.get("ok", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
