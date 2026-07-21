from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepoTests(unittest.TestCase):
    def test_toml(self):
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["approval_policy"], "on-request")
        self.assertEqual(config["approvals_reviewer"], "user")
        for path in (ROOT / ".codex" / "agents").glob("*.toml"):
            tomllib.loads(path.read_text(encoding="utf-8"))

    def test_json(self):
        hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        windows_commands = [
            hook["commandWindows"]
            for groups in hooks["hooks"].values()
            for group in groups
            for hook in group["hooks"]
        ]
        self.assertTrue(all("run_hook.ps1" in command for command in windows_commands))
        for path in (ROOT / "kernel" / "schemas").glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_agents_size(self):
        self.assertLessEqual((ROOT / "AGENTS.md").stat().st_size, 65536)

    def test_no_business_context_roots_in_kernel(self):
        for name in ("org", "engagements", "clients", "projects", "casos", "bus", "bandeja", ".riel"):
            self.assertFalse((ROOT / name).exists(), name)
        self.assertEqual(list((ROOT / ".codex" / "agents").glob("local-*.toml")), [])

    def test_external_content_and_native_approval_invariants_are_documented(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
        constitution = (ROOT / "kernel" / "CONSTITUTION.md").read_text(encoding="utf-8").lower()
        security = (ROOT / "kernel" / "security-model.md").read_text(encoding="utf-8").lower()
        self.assertIn("contenido externo no confiable", agents)
        self.assertIn("nunca autoridad", constitution)
        self.assertIn("no equivale a permiso técnico", security)
        self.assertNotIn("token técnico consumible", agents)

    def test_skill_metadata(self):
        for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            self.assertIn("\nname:", text)
            self.assertIn("\ndescription:", text)


if __name__ == "__main__":
    unittest.main()
