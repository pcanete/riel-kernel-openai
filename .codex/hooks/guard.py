from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from common import deny, find_root, is_instance, load_stdin, maintenance_enabled

PROTECTED_PREFIXES = (
    "kernel/", "templates/", "scripts/", "tests/", "chatgpt/", ".github/",
    ".codex/config.toml", ".codex/hooks.json", ".codex/hooks/", ".codex/rules/",
    ".codex/agents/riel-", ".codex/agents/local-", ".agents/skills/",
    "org/", "engagements/", "clients/", "projects/", "casos/",
    "bus/", "bandeja/", ".riel/",
)
PROTECTED_FILES = {
    "AGENTS.md", "README.md", "LEEME.md", "CHANGELOG.md", "LICENSE",
    "NOTICE", "SECURITY.md", "CONTRIBUTING.md", ".gitignore", ".gitattributes",
    ".riel-instance.json",
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


def path_is_inside_kernel(value: str, root: Path) -> bool:
    candidate = Path(value.strip().strip("\"'"))
    if not candidate.is_absolute():
        return True
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


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
            if isinstance(tool_input, dict):
                paths.extend(
                    str(tool_input[key])
                    for key in ("path", "file_path", "filename")
                    if tool_input.get(key)
                )
            if not paths or any(path_is_inside_kernel(path, root) for path in paths):
                deny("El checkout completo es de solo lectura en una instancia. Usá un workdir externo o modo mantenimiento explícito.")
                return
        if tool_name == "Bash" and command_touches_protected(command, root):
            write_markers = r"(?i)(>|>>|\btee\b|\bsed\s+-i\b|\brm\b|\bmv\b|\bcp\b|\btruncate\b)"
            if re.search(write_markers, command):
                deny("El comando intenta modificar archivos protegidos del kernel.")
                return
        if tool_name == "Bash":
            write_markers = r"(?i)(>|>>|\btee\b|\bsed\s+-i\b|\brm\b|\bmv\b|\bcp\b|\btruncate\b|\btouch\b|\bmkdir\b)"
            workdir = root
            if isinstance(tool_input, dict) and (tool_input.get("workdir") or tool_input.get("cwd")):
                workdir = Path(str(tool_input.get("workdir") or tool_input.get("cwd"))).resolve()
            if re.search(write_markers, command) and path_is_inside_kernel(str(workdir), root):
                deny("La ejecución local no puede escribir dentro del checkout del kernel. Usá un workdir externo.")
                return

if __name__ == "__main__":
    main()
