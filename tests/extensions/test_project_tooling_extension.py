from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]
EXTENSION = ROOT / "extensions" / "project-tooling"
SCANNER = EXTENSION / "scripts" / "tooling_audit.py"


def test_extension_manifest_declares_expected_commands() -> None:
    manifest = yaml.safe_load((EXTENSION / "extension.yml").read_text(encoding="utf-8"))
    commands = {item["name"] for item in manifest["provides"]["commands"]}
    assert commands == {
        "speckit.project-tooling.audit",
        "speckit.project-tooling.confirm",
        "speckit.project-tooling.update",
        "speckit.project-tooling.verify-task",
        "speckit.project-tooling.verify-feature",
    }
    for item in manifest["provides"]["commands"]:
        assert (EXTENSION / item["file"]).is_file()


def test_scanner_audits_and_checks_policy(tmp_path: Path) -> None:
    (tmp_path / ".fvmrc").write_text('{"flutter":"3.41.7"}', encoding="utf-8")
    inventory_path = tmp_path / "inventory.json"
    audit = subprocess.run(
        [sys.executable, str(SCANNER), "audit", "--root", str(tmp_path),
         "--output", str(inventory_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert audit.returncode == 0, audit.stderr
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert any(item["declared"].get("flutter") == "3.41.7" for item in inventory["manifests"])

    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"tools": {"definitely-missing-tool": {"required": True}}}), encoding="utf-8")
    check = subprocess.run(
        [sys.executable, str(SCANNER), "check", "--root", str(tmp_path),
         "--policy", str(policy)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert check.returncode == 2
    result = json.loads(check.stdout)
    assert result["ok"] is False
    assert result["results"][0]["status"] == "missing"


def test_scanner_propose_never_executes_updates(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"tools": {"missing": {"required": True}}}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCANNER), "propose", "--root", str(tmp_path),
         "--policy", str(policy)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["requires_confirmation"] is True
    assert payload["actions"][0]["status"] == "missing"
