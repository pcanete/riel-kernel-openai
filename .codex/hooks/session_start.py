from __future__ import annotations

import json
from pathlib import Path

from common import find_root, is_instance


def safe_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def count_open_queue(path: Path) -> int:
    if not path.exists():
        return 0
    open_ids: set[str] = set()
    closed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except Exception:
            continue
        if event.get("type") == "close" and event.get("closes"):
            closed.add(str(event["closes"]))
        elif event.get("id"):
            open_ids.add(str(event["id"]))
    return len(open_ids - closed)


def main() -> None:
    root = find_root()
    if not is_instance(root):
        print(
            "Riel está en modo desarrollo/no inicializado. No inventes contexto de organización. "
            "Para crear una instancia, pedí aprobación y ejecutá `python scripts/riel.py init`. "
            "Antes de modificar el kernel, ejecutá las pruebas."
        )
        return

    state = safe_json(root / ".riel" / "state.json")
    user = state.get("active_user") or "sin usuario activo"
    engagement = state.get("active_engagement") or "sin engagement activo"
    open_count = count_open_queue(root / "bus" / "queues" / "riel.ndjson")
    approvals_dir = root / "bus" / "approvals"
    pending = 0
    if approvals_dir.exists():
        for item in approvals_dir.glob("*.json"):
            data = safe_json(item)
            if data.get("status") in {"pending", "approved"} and not data.get("consumed_at"):
                pending += 1
    print(
        f"Instancia Riel activa. Usuario: {user}. Engagement: {engagement}. "
        f"Mensajes abiertos para Riel: {open_count}. Aprobaciones pendientes/activas: {pending}. "
        "Leé las capas indicadas en AGENTS.md y mantené el kernel en solo lectura."
    )


if __name__ == "__main__":
    main()
