#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

EXCLUDE_PARTS = {".git", "org", "engagements", "bus", ".riel", "__pycache__"}


def files_under(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        if rel.match(".codex/agents/local-*.toml"):
            continue
        yield path, rel


def main() -> int:
    parser = argparse.ArgumentParser(description="Instalador seguro de Riel en una carpeta existente")
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force", action="store_true", help="Reemplazar colisiones después de revisarlas")
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)

    collisions = []
    planned = []
    for src, rel in files_under(source):
        dst = target / rel
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            collisions.append(rel)
        else:
            planned.append((src, dst))

    if collisions and not args.force:
        print("Se detectaron colisiones; no se modificó nada:")
        for item in collisions:
            print(" -", item)
        print("Revisá las diferencias. Usá --force solo después de decidir reemplazarlas.")
        return 2

    for src, rel in files_under(source):
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"Kernel instalado en {target}")
    print("Siguiente paso: python scripts/riel.py init")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
