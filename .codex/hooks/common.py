from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def find_root() -> Path:
    override = os.environ.get("RIEL_ROOT")
    if override:
        return Path(override).resolve()
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value:
            return Path(value).resolve()
    except Exception:
        pass
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "kernel").exists():
            return candidate
    return current


def load_stdin() -> dict[str, Any]:
    try:
        raw = os.sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def is_instance(root: Path) -> bool:
    return (root / ".riel" / "instance.json").exists()


def maintenance_enabled() -> bool:
    return os.environ.get("RIEL_MAINTENANCE") == "1"


def redact(text: str) -> str:
    patterns = [
        (r"(?i)(api[_-]?key|token|secret|password|authorization)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]"),
        (r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]"),
        (r"ghp_[A-Za-z0-9]+", "ghp_[REDACTED]"),
        (r"sk-[A-Za-z0-9_-]+", "sk-[REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text
