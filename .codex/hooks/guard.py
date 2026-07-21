from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from common import deny, find_root, is_instance, load_stdin, maintenance_enabled, now_iso

PROTECTED_PREFIXES = (
    "kernel/", "templates/", "scripts/", "tests/", "chatgpt/", ".github/",
    ".codex/config.toml", ".codex/hooks.json", ".codex/hooks/", ".codex/rules/",
    ".codex/agents/riel-", ".agents/skills/",
)
PROTECTED_FILES = {
    "AGENTS.md", "README.md", "LEEME.md", "CHANGELOG.md", "LICENSE",
    "NOTICE", "SECURITY.md", "CONTRIBUTING.md", ".gitignore", ".gitattributes",
}

DESTRUCTIVE_PATTERNS = [
    (r"(?i)\brm\s+-[^\n]*r[^\n]*f[^\n]*(?:\s/|\s\.\s*$|\s\.\*)", "Borrado recursivo destructivo bloqueado."),
    (r"(?i)\bgit\s+reset\s+--hard\b", "`git reset --hard` está bloqueado."),
    (r"(?i)\bgit\s+clean\s+-[^\n]*[fdx]", "`git clean` destructivo está bloqueado."),
    (r"(?i)\bgit\s+push\b[^\n]*(--force|--force-with-lease|-f\b)", "Los force-push están bloqueados."),
    (r"(?i)\bgh\s+repo\s+delete\b", "Eliminar repositorios está bloqueado."),
    (r"(?i)\bchmod\s+-R\s+777\b", "Permisos 777 recursivos están bloqueados."),
    (r"(?i)(curl|wget)[^\n|]*\|\s*(sh|bash|zsh|powershell)\b", "Descargar y ejecutar scripts en una tubería está bloqueado."),
]

EXTERNAL_COMMAND_PATTERNS = [
    r"(?i)\bgit\s+push\b",
    r"(?i)\bgh\s+(pr|issue|release|repo)\s+(create|edit|delete|merge|close|reopen|publish)\b",
    r"(?i)\b(npm|pnpm|yarn)\s+publish\b",
    r"(?i)\b(vercel|netlify)\b.*\b(deploy|--prod)\b",
    r"(?i)\bdocker\s+push\b",
    r"(?i)\bkubectl\s+(apply|delete|patch|create|replace|scale|rollout)\b",
    r"(?i)\bterraform\s+(apply|destroy)\b",
]

WRITE_TOOL_RE = re.compile(
    r"(?i)(^|__|_)(send|create|update|delete|publish|post|forward|archive|trash|"
    r"apply|modify|move|share|invite|deploy|purchase|charge|refund|approve|respond)(_|$)"
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def is_protected_path(path: str) -> bool:
    path = normalize_path(path)
    if path in PROTECTED_FILES:
        return True
    return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def patch_paths(command: str) -> list[str]:
    found = re.findall(r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+)$", command, flags=re.MULTILINE)
    if found:
        return [value.strip() for value in found]
    # Fallback for edit tools that may submit a single path field in a textual command.
    return re.findall(r"(?im)(?:path|file|filename)\s*[:=]\s*[\"']?([^\"'\n]+)", command)


def command_touches_protected(command: str, root: Path) -> bool:
    normalized_command = command.replace("\\", "/")

    # Detect absolute paths before tokenizing. Windows user and workspace paths
    # commonly contain spaces or non-ASCII characters, which are intentionally
    # not covered by the conservative token matcher below. Keep the lexical
    # RIEL_ROOT alias too: Path.resolve() expands Windows 8.3 paths, while the
    # command may still contain the short spelling.
    root_texts = {root.as_posix().rstrip("/") + "/"}
    root_override = os.environ.get("RIEL_ROOT")
    if root_override:
        root_texts.add(Path(root_override).as_posix().rstrip("/") + "/")
    command_key = normalized_command.casefold()
    for root_text in root_texts:
        root_key = root_text.casefold()
        search_from = 0
        while True:
            root_at = command_key.find(root_key, search_from)
            if root_at < 0:
                break
            relative = normalized_command[root_at + len(root_text):]
            if is_protected_path(relative):
                return True
            search_from = root_at + len(root_text)

    root_text = root.as_posix().rstrip("/") + "/"
    for token in re.findall(r"(?:^|\s)([A-Za-z0-9_.:\\/-]+)", command):
        normalized = token.replace("\\", "/").strip("\"'")
        if normalized.startswith(root_text):
            normalized = normalized[len(root_text):]
        if is_protected_path(normalized):
            return True
    return False


def load_active_approval(root: Path, subject: str) -> tuple[bool, str]:
    active_path = root / ".riel" / "active-approval"
    if not active_path.exists():
        return False, "La acción externa requiere una aprobación formal activa."
    approval_id = active_path.read_text(encoding="utf-8").strip()
    record_path = root / "bus" / "approvals" / f"{approval_id}.json"
    if not record_path.exists():
        return False, f"La aprobación activa `{approval_id}` no existe."
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except Exception:
        return False, f"La aprobación `{approval_id}` no es JSON válido."
    if record.get("status") != "approved":
        return False, f"La aprobación `{approval_id}` no está aprobada."
    if record.get("consumed_at"):
        return False, f"La aprobación `{approval_id}` ya fue consumida."
    expires_at = record.get("expires_at")
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at) < datetime.now().astimezone():
                return False, f"La aprobación `{approval_id}` expiró."
        except ValueError:
            return False, f"La aprobación `{approval_id}` tiene vencimiento inválido."
    pattern = record.get("tool_pattern") or ""
    try:
        if not pattern or not re.search(pattern, subject, flags=re.IGNORECASE):
            return False, f"La aprobación `{approval_id}` no coincide con esta acción."
    except re.error:
        return False, f"La aprobación `{approval_id}` tiene un patrón inválido."

    record["consumed_at"] = now_iso()
    record["consumed_subject"] = subject[:500]
    tmp = record_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, record_path)
    active_path.unlink(missing_ok=True)
    return True, approval_id


def main() -> None:
    payload = load_stdin()
    root = find_root()
    if not is_instance(root):
        return

    tool_name = str(payload.get("tool_name") or payload.get("toolName") or "")
    tool_input: Any = payload.get("tool_input") or payload.get("toolInput") or {}
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command") or tool_input.get("patch") or "")
    else:
        command = str(tool_input)

    for pattern, reason in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command):
            deny(reason)
            return

    if not maintenance_enabled():
        if tool_name in {"apply_patch", "Edit", "Write"}:
            paths = patch_paths(command)
            if any(is_protected_path(path) for path in paths):
                deny("El kernel es de solo lectura en una instancia. Usá modo mantenimiento explícito para editarlo.")
                return
        if tool_name == "Bash" and command_touches_protected(command, root):
            write_markers = r"(?i)(>|>>|\btee\b|\bsed\s+-i\b|\brm\b|\bmv\b|\bcp\b|\btruncate\b)"
            if re.search(write_markers, command):
                deny("El comando intenta modificar archivos protegidos del kernel.")
                return

    if tool_name.startswith("mcp__") and WRITE_TOOL_RE.search(tool_name):
        ok, reason = load_active_approval(root, tool_name)
        if not ok:
            deny(reason)
        return

    if tool_name == "Bash" and any(re.search(pattern, command) for pattern in EXTERNAL_COMMAND_PATTERNS):
        ok, reason = load_active_approval(root, command)
        if not ok:
            deny(reason)
        return


if __name__ == "__main__":
    main()
