from __future__ import annotations

import importlib.util
import json
import os
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
        self.base = Path(self.tmp.name)
        self.root = self.base / "kernel"
        self.state_dir = self.base / "technical-state"
        self.work_dir = self.base / "client-work"
        self.work_dir.mkdir()
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".riel-instance.json", "org", "engagements",
                "clients", "projects", "casos", "bus", "bandeja", ".riel"
            ),
        )
        self.old = Path.cwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def init_instance(self):
        riel.command_init(
            Namespace(
                organization_ref="clickup://workspace/acme",
                owner_ref="user://ana",
                instance_id="acme",
                state_dir=str(self.state_dir),
                timezone="America/Argentina/Cordoba",
                force=False,
            )
        )

    def configure_required_sources(self):
        for role, locator in (
            ("organization", "wiki://acme"),
            ("work", "clickup://space/acme"),
        ):
            riel.command_configure_source(
                Namespace(role=role, provider="test", locator=locator, mode="read-write")
            )

    def test_init_keeps_business_context_outside_kernel(self):
        self.init_instance()
        link = json.loads((self.root / ".riel-instance.json").read_text(encoding="utf-8"))
        self.assertTrue(Path(link["state_dir"]).samefile(self.state_dir))
        self.assertTrue((self.state_dir / "instance.json").exists())
        instance = json.loads((self.state_dir / "instance.json").read_text(encoding="utf-8"))
        self.assertTrue(Path(instance["python_executable"]).is_file())
        for forbidden in ("org", "engagements", "clients", "projects", "casos", "bus", "bandeja", ".riel"):
            self.assertFalse((self.root / forbidden).exists())

    def test_doctor_requires_and_validates_shared_sources(self):
        self.init_instance()
        errors, _ = riel.doctor(self.root)
        self.assertIn("Falta fuente compartida obligatoria: organization", errors)
        self.assertIn("Falta fuente compartida obligatoria: work", errors)
        self.configure_required_sources()
        errors, _ = riel.doctor(self.root)
        self.assertEqual(errors, [])

    def test_init_reconnects_existing_state_without_erasing_sources(self):
        self.init_instance()
        self.configure_required_sources()
        (self.root / ".riel-instance.json").unlink()
        self.init_instance()
        instance = json.loads((self.state_dir / "instance.json").read_text(encoding="utf-8"))
        self.assertEqual(set(instance["shared_sources"]), {"organization", "work"})
        self.assertTrue((self.root / ".riel-instance.json").exists())

    def test_doctor_rejects_legacy_local_context(self):
        self.init_instance()
        self.configure_required_sources()
        (self.root / "org").mkdir()
        errors, _ = riel.doctor(self.root)
        self.assertTrue(any("datos o agentes locales heredados" in item for item in errors))

    def test_link_work_must_be_outside_kernel(self):
        self.init_instance()
        inside = self.root / "client-work"
        inside.mkdir()
        with self.assertRaises(SystemExit):
            riel.command_link_work(
                Namespace(
                    engagement_ref="clickup://task/1",
                    shared_record="clickup://task/1",
                    work_dir=str(inside),
                    artifact_ref=None,
                )
            )
        riel.command_link_work(
            Namespace(
                engagement_ref="clickup://task/1",
                shared_record="clickup://task/1",
                work_dir=str(self.work_dir),
                artifact_ref="git://client/repo",
            )
        )
        state = json.loads((self.state_dir / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(Path(state["active_workdir"]).samefile(self.work_dir))

    def test_session_close_requires_shared_record_and_writes_external_receipt(self):
        self.init_instance()
        with self.assertRaises(SystemExit):
            riel.command_session_close(
                Namespace(engagement_ref="work://1", shared_record="", confirmed_by="user://ana")
            )
        riel.command_session_close(
            Namespace(
                engagement_ref="work://1",
                shared_record="clickup://task/1#comment-2",
                confirmed_by="user://ana",
            )
        )
        self.assertEqual(len(list((self.state_dir / "receipts").glob("*.json"))), 1)
        self.assertFalse((self.root / "session-log.md").exists())

    def test_cli_cannot_mint_or_activate_technical_approvals(self):
        self.init_instance()
        parser = riel.build_parser()
        subcommands = next(
            action.choices for action in parser._actions if getattr(action, "choices", None)
        )
        for forbidden in ("request-approval", "approve", "deny", "activate-approval"):
            self.assertNotIn(forbidden, subcommands)
        self.assertFalse((self.state_dir / "approvals").exists())
        self.assertFalse((self.state_dir / "active-approval").exists())

    def test_doctor_warns_that_legacy_approval_artifacts_are_inert(self):
        self.init_instance()
        self.configure_required_sources()
        (self.state_dir / "approvals").mkdir()
        (self.state_dir / "active-approval").write_text("apr-old\n", encoding="utf-8")
        errors, warnings = riel.doctor(self.root)
        self.assertEqual(errors, [])
        self.assertTrue(any("No conceden permisos" in warning for warning in warnings))

    def test_slug_preserves_spanish_names(self):
        self.assertEqual(riel.slug("Ana Pérez Núñez"), "ana-perez-nunez")


if __name__ == "__main__":
    unittest.main()
