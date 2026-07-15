from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepoTests(unittest.TestCase):
    def test_toml(self):
        tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        for path in (ROOT / ".codex" / "agents").glob("*.toml"):
            tomllib.loads(path.read_text(encoding="utf-8"))

    def test_json(self):
        json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        for path in (ROOT / "kernel" / "schemas").glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_agents_size(self):
        self.assertLessEqual((ROOT / "AGENTS.md").stat().st_size, 65536)

    def test_skill_metadata(self):
        for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            self.assertIn("\nname:", text)
            self.assertIn("\ndescription:", text)


if __name__ == "__main__":
    unittest.main()
