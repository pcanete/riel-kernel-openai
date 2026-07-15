from __future__ import annotations

import hashlib
import json
from pathlib import Path

from common import find_root, is_instance, load_stdin, now_iso, redact


def append_line(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    payload = load_stdin()
    root = find_root()
    if not is_instance(root):
        return
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "unknown")
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    serialized = json.dumps(tool_input, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    summary = ""
    if tool_name == "Bash" and isinstance(tool_input, dict):
        summary = redact(str(tool_input.get("command") or ""))[:500]
    elif tool_name == "apply_patch" and isinstance(tool_input, dict):
        command = str(tool_input.get("command") or tool_input.get("patch") or "")
        paths = []
        for line in command.splitlines():
            if line.startswith("*** ") and " File:" in line:
                paths.append(line.split("File:", 1)[1].strip())
        summary = "paths=" + ",".join(paths[:20])
    elif tool_name.startswith("mcp__"):
        summary = "external-tool-call"
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
            "summary": summary,
        },
    }
    day = event["created_at"][:10]
    append_line(root / "bus" / "events" / f"{day}.ndjson", event)


if __name__ == "__main__":
    main()
