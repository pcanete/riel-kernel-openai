from __future__ import annotations

import hashlib
import json
from pathlib import Path

from common import find_root, instance_dir, load_stdin, now_iso


def append_line(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    payload = load_stdin()
    root = find_root()
    runtime = instance_dir(root)
    if runtime is None:
        return
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "unknown")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    serialized = json.dumps(tool_input, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    event = {
        "schema_version": "1.0",
        "id": f"audit-{digest[:16]}-{now_iso()}",
        "type": "audit",
        "status": "recorded",
        "sender": "codex",
        "recipient": "riel",
        "scope": "workspace",
        "created_at": now_iso(),
        "payload": {
            "tool_name": tool_name,
            "input_sha256": digest,
        },
    }
    day = event["created_at"][:10]
    # Registro técnico mínimo y descartable. No sustituye la visibilidad
    # compartida del trabajo, las decisiones ni los próximos pasos.
    append_line(runtime / "audit" / f"{day}.ndjson", event)


if __name__ == "__main__":
    main()
