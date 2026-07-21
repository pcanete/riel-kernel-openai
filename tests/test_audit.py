from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / ".codex" / "hooks" / "audit.py"


class AuditTests(unittest.TestCase):
    def test_local_audit_does_not_persist_business_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "kernel"
            runtime = base / "technical-state"
            root.mkdir()
            runtime.mkdir()
            (runtime / "instance.json").write_text("{}", encoding="utf-8")
            (root / ".riel-instance.json").write_text(
                json.dumps({"schema_version": "1.0", "instance_id": "test", "state_dir": str(runtime)}),
                encoding="utf-8",
            )
            payload = {
                "tool_name": "Bash",
                "tool_input": {"command": "build --client SecretClient --token secret-value"},
            }
            env = os.environ.copy()
            env["RIEL_ROOT"] = str(root)
            subprocess.run(
                [sys.executable, str(AUDIT)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                env=env,
                cwd=ROOT,
                check=True,
            )
            audit_file = next((runtime / "audit").glob("*.ndjson"))
            stored = audit_file.read_text(encoding="utf-8")
            self.assertNotIn("SecretClient", stored)
            self.assertNotIn("secret-value", stored)
            event = json.loads(stored)
            self.assertEqual(set(event["payload"]), {"tool_name", "input_sha256"})


if __name__ == "__main__":
    unittest.main()
