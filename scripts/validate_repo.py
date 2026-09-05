#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar el kernel y, opcionalmente, su contrato común con Claude")
    parser.add_argument("--peer", type=Path, help="Checkout local de riel-kernel (Claude) para comparar contrato y skills")
    args = parser.parse_args()
    errors: list[str] = []
    for name in ("org", "engagements", "clients", "projects", "casos", "bus", "bandeja", ".riel"):
        if (ROOT / name).exists():
            errors.append(f"El kernel contiene la raíz privada prohibida: {name}/")
    for path in (ROOT / ".codex" / "agents").glob("local-*.toml"):
        errors.append(f"El kernel contiene un agente específico de organización: {path.relative_to(ROOT)}")
    agents = ROOT / "AGENTS.md"
    if agents.stat().st_size > 65536:
        errors.append("AGENTS.md supera 65536 bytes")

    for path in [ROOT / ".codex" / "config.toml", *sorted((ROOT / ".codex" / "agents").glob("riel-*.toml"))]:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"TOML inválido {path.relative_to(ROOT)}: {exc}")

    for path in [ROOT / ".codex" / "hooks.json", *sorted((ROOT / "kernel" / "schemas").glob("*.json"))]:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"JSON inválido {path.relative_to(ROOT)}: {exc}")

    for skill in sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\nname:" not in text or "\ndescription:" not in text:
            errors.append(f"Metadata inválida en {skill.relative_to(ROOT)}")

    if args.peer:
        pairs = [(ROOT / "kernel" / "coordination.md", args.peer / "docs" / "coordination.md")]
        pairs.extend(
            (skill, args.peer / ".claude" / "skills" / skill.parent.name / "SKILL.md")
            for skill in sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
        )
        for source, peer in pairs:
            if not peer.is_file():
                errors.append(f"Falta contraparte del contrato común: {peer}")
            elif source.read_text(encoding="utf-8") != peer.read_text(encoding="utf-8"):
                errors.append(f"Divergencia del contrato común: {source.relative_to(ROOT)} vs {peer}")

    link_re = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if any(part in {"org", "engagements", "bus", ".riel"} for part in path.parts):
            continue
        for link in link_re.findall(path.read_text(encoding="utf-8")):
            target = (path.parent / link.split("#", 1)[0]).resolve()
            if link and not target.exists():
                errors.append(f"Link roto en {path.relative_to(ROOT)}: {link}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Validación del repositorio: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
