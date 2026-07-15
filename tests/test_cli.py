from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("riel_cli", ROOT / "scripts" / "riel.py")
riel = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(riel)


class RielCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", "org", "engagements", "bus", ".riel"))
        self.old = Path.cwd()
        import os
        os.chdir(self.root)

    def tearDown(self):
        import os
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_init_and_engagement(self):
        riel.command_init(Namespace(org_name="Acme", owner="Ana Pérez", timezone="America/Argentina/Cordoba", force=False))
        self.assertTrue((self.root / ".riel" / "instance.json").exists())
        self.assertTrue((self.root / "org" / "users" / "ana-perez.md").exists())
        riel.command_new_engagement(Namespace(id="cliente-1", type="client", name="Cliente Uno", owner=None))
        self.assertTrue((self.root / "engagements" / "cliente-1" / "AGENTS.md").exists())

    def test_bus_append_and_close(self):
        riel.command_init(Namespace(org_name="Acme", owner="Ana", timezone="local", force=False))
        args = Namespace(recipient="riel", type="task", sender="riel", scope="workspace", payload='{"x":1}')
        riel.command_bus_send(args)
        path = self.root / "bus" / "queues" / "riel.ndjson"
        event = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["type"], "task")
        riel.command_bus_close(Namespace(event_id=event["id"], recipient="riel", sender="riel", scope="workspace", reason="done"))
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["closes"], event["id"])

    def test_approval_lifecycle(self):
        riel.command_init(Namespace(org_name="Acme", owner="Ana", timezone="local", force=False))
        args = Namespace(action="Publicar", tool_pattern="git push", scope="repo", risk="medium", reversible=True, reason="", requested_by="riel", expires_minutes=60)
        riel.command_request_approval(args)
        approval_file = next((self.root / "bus" / "approvals").glob("*.json"))
        approval_id = approval_file.stem
        riel.command_approve(Namespace(id=approval_id, by="ana"))
        riel.command_activate_approval(Namespace(id=approval_id, subject="git push origin main"))
        self.assertEqual((self.root / ".riel" / "active-approval").read_text().strip(), approval_id)

    def test_rejects_overbroad_approval(self):
        riel.command_init(Namespace(org_name="Acme", owner="Ana", timezone="local", force=False))
        args = Namespace(action="Todo", tool_pattern=".*", scope="repo", risk="high", reversible=False, reason="", requested_by="riel", expires_minutes=60)
        with self.assertRaises(SystemExit):
            riel.command_request_approval(args)

    def test_slug_preserves_spanish_names(self):
        self.assertEqual(riel.slug("Ana Pérez Núñez"), "ana-perez-nunez")


if __name__ == "__main__":
    unittest.main()
