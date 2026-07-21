from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "Windows PowerShell required")
class WindowsHookRunnerTests(unittest.TestCase):
    def test_runner_uses_python_recorded_by_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            kernel = base / "kernel"
            runtime = base / "state"
            hook_dir = kernel / ".codex" / "hooks"
            hook_dir.mkdir(parents=True)
            runtime.mkdir()
            shutil.copy2(ROOT / ".codex" / "hooks" / "run_hook.ps1", hook_dir / "run_hook.ps1")
            (hook_dir / "session_start.py").write_text("print('hook-runner-ok')\n", encoding="utf-8")
            (runtime / "instance.json").write_text(
                json.dumps({"python_executable": sys.executable}), encoding="utf-8"
            )
            (kernel / ".riel-instance.json").write_text(
                json.dumps({"state_dir": str(runtime)}), encoding="utf-8"
            )
            subprocess.run(["git", "init", "--quiet"], cwd=kernel, check=True)
            result = subprocess.run(
                [
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", str(hook_dir / "run_hook.ps1"), "-Hook", "session_start.py",
                ],
                cwd=kernel,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("hook-runner-ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
