from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / ".codex" / "hooks" / "guard.py"


class GuardTests(unittest.TestCase):
    def run_guard(self, root: Path, payload: dict) -> str:
        env = os.environ.copy()
        env["RIEL_ROOT"] = str(root)
        result = subprocess.run(
            [sys.executable, str(GUARD)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            env=env,
            cwd=ROOT,
            check=False,
        )
        return result.stdout.strip()

    def make_instance(self, root: Path):
        (root / ".riel").mkdir(parents=True)
        (root / "bus" / "approvals").mkdir(parents=True)
        (root / ".riel" / "instance.json").write_text("{}", encoding="utf-8")

    def test_destructive_command_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_instance(root)
            out = self.run_guard(root, {"tool_name": "Bash", "tool_input": {"command": "git reset --hard"}})
            self.assertIn('"permissionDecision": "deny"', out)

    def test_runtime_write_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_instance(root)
            out = self.run_guard(root, {"tool_name": "apply_patch", "tool_input": {"command": "*** Update File: org/context.md"}})
            self.assertEqual(out, "")

    def test_kernel_write_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_instance(root)
            out = self.run_guard(root, {"tool_name": "apply_patch", "tool_input": {"command": "*** Update File: kernel/CONSTITUTION.md"}})
            self.assertIn("solo lectura", out)

    def test_external_tool_needs_and_consumes_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_instance(root)
            out = self.run_guard(root, {"tool_name": "mcp__gmail__send_email", "tool_input": {"to": "x@example.com"}})
            self.assertIn("aprobación", out)

            approval_id = "apr-test"
            record = {
                "status": "approved",
                "consumed_at": None,
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).astimezone().isoformat(),
                "tool_pattern": "gmail.*send",
            }
            (root / "bus" / "approvals" / f"{approval_id}.json").write_text(json.dumps(record), encoding="utf-8")
            (root / ".riel" / "active-approval").write_text(approval_id, encoding="utf-8")
            out = self.run_guard(root, {"tool_name": "mcp__gmail__send_email", "tool_input": {"to": "x@example.com"}})
            self.assertEqual(out, "")
            updated = json.loads((root / "bus" / "approvals" / f"{approval_id}.json").read_text())
            self.assertTrue(updated["consumed_at"])
            self.assertFalse((root / ".riel" / "active-approval").exists())

    def test_absolute_kernel_path_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_instance(root)
            target = root / "kernel" / "CONSTITUTION.md"
            out = self.run_guard(root, {"tool_name": "Bash", "tool_input": {"command": f"echo x > {target}"}})
            self.assertIn("archivos protegidos", out)


if __name__ == "__main__":
    unittest.main()
