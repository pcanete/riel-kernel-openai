#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KERNEL_VERSION = "3.0.0.dev0"
SOURCE_ROLES = {"organization", "work", "knowledge", "artifacts"}
SOURCE_MODES = {"read", "read-write"}
REQUIRED_SOURCE_ROLES = {"organization", "work"}
LEGACY_LOCAL_ROOTS = (
    "org", "engagements", "clients", "projects", "casos", "bus", "bandeja", ".riel"
)
LINK_FILENAME = ".riel-instance.json"


def now() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def iso(value: datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="seconds")


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip().lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    return value.strip("-") or "instance"


def root_from(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "kernel").exists():
            return candidate
    raise SystemExit("No se encontró la raíz de Riel (AGENTS.md + kernel/).")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def default_state_home() -> Path:
    override = os.environ.get("RIEL_STATE_HOME")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        return (Path(base) if base else Path.home() / "AppData" / "Local") / "Riel" / "instances"
    xdg = os.environ.get("XDG_STATE_HOME")
    return (Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state") / "riel" / "instances"


def link_path(root: Path) -> Path:
    return root / LINK_FILENAME


def instance_dir(root: Path, required: bool = True) -> Path | None:
    link = read_json(link_path(root), None)
    if not isinstance(link, dict) or not link.get("state_dir"):
        if required:
            raise SystemExit(
                "La instancia no está conectada. Ejecutá `python scripts/riel.py init` "
                "desde una terminal humana."
            )
        return None
    state_dir = Path(str(link["state_dir"])).expanduser().resolve()
    if is_within(state_dir, root):
        raise SystemExit("El estado de Riel no puede vivir dentro del checkout del kernel.")
    if required and not (state_dir / "instance.json").exists():
        raise SystemExit(f"No existe la instancia externa declarada en {LINK_FILENAME}: {state_dir}")
    return state_dir


def instance_record(root: Path) -> dict[str, Any]:
    directory = instance_dir(root)
    assert directory is not None
    return read_json(directory / "instance.json", {})


def active_state(root: Path) -> dict[str, Any]:
    directory = instance_dir(root)
    assert directory is not None
    return read_json(
        directory / "state.json",
        {
            "active_user_ref": None,
            "active_engagement_ref": None,
            "active_workdir": None,
            "shared_record_ref": None,
        },
    )


def tracked_private_files(root: Path) -> list[str]:
    try:
        output = subprocess.check_output(["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    private = tuple(prefix + "/" for prefix in LEGACY_LOCAL_ROOTS)
    return [
        line
        for line in output.splitlines()
        if line.startswith(private) or re.match(r"\.codex/agents/local-.*\.toml$", line)
    ]


def legacy_local_data(root: Path) -> list[str]:
    found: list[str] = []
    for name in LEGACY_LOCAL_ROOTS:
        target = root / name
        if target.exists():
            found.append(name + "/")
    for target in (root / ".codex" / "agents").glob("local-*.toml"):
        found.append(str(target.relative_to(root)).replace("\\", "/"))
    return found


def event_id(prefix: str) -> str:
    stamp = now().strftime("%Y%m%dT%H%M%S")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def validate_source(role: str, source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if role not in SOURCE_ROLES:
        errors.append(f"rol inválido: {role}")
    for field in ("provider", "locator", "mode"):
        if not str(source.get(field) or "").strip():
            errors.append(f"falta `{field}`")
    if source.get("mode") not in SOURCE_MODES:
        errors.append("mode debe ser read o read-write")
    return errors


def command_init(args: argparse.Namespace) -> None:
    root = root_from()
    instance_id = slug(args.instance_id or args.organization_ref)
    state_dir = (
        Path(args.state_dir).expanduser().resolve()
        if args.state_dir
        else (default_state_home() / instance_id).resolve()
    )
    if is_within(state_dir, root):
        raise SystemExit("--state-dir debe estar fuera del checkout del kernel.")
    existing_path = state_dir / "instance.json"
    existing = read_json(existing_path, {}) if existing_path.exists() else {}
    if existing and not args.force:
        if existing.get("organization_ref") != args.organization_ref:
            raise SystemExit("La instancia externa pertenece a otra organization_ref.")
        if existing.get("owner_ref") != args.owner_ref:
            raise SystemExit("La instancia externa declara otro owner_ref.")
        write_json(
            link_path(root),
            {
                "schema_version": "1.0",
                "instance_id": existing.get("instance_id") or instance_id,
                "state_dir": str(state_dir),
            },
        )
        print(f"Instancia técnica existente reconectada sin modificar sus fuentes: {state_dir}")
        return

    state_dir.mkdir(parents=True, exist_ok=True)
    for directory in ("audit", "receipts"):
        (state_dir / directory).mkdir(exist_ok=True)

    shared_sources = existing.get("shared_sources", {}) if existing else {}
    initialized_at = existing.get("initialized_at") or iso()
    write_json(
        existing_path,
        {
            "schema_version": "2.0",
            "kernel_version": KERNEL_VERSION,
            "mode": "shared-first",
            "instance_id": instance_id,
            "organization_ref": args.organization_ref,
            "owner_ref": args.owner_ref,
            "initialized_at": initialized_at,
            "timezone": args.timezone or os.environ.get("TZ") or "local",
            "python_executable": str(Path(sys.executable).resolve()),
            "shared_sources": shared_sources,
        },
    )
    state_path = state_dir / "state.json"
    if not state_path.exists():
        write_json(
            state_path,
            {
                "active_user_ref": args.owner_ref,
                "active_engagement_ref": None,
                "active_workdir": None,
                "shared_record_ref": None,
                "updated_at": iso(),
            },
        )
    write_json(
        link_path(root),
        {
            "schema_version": "1.0",
            "instance_id": instance_id,
            "state_dir": str(state_dir),
        },
    )
    print(f"Instancia técnica conectada fuera del kernel: {state_dir}")
    print(
        "Ahora configurá las fuentes compartidas `organization` y `work` con "
        "`python scripts/riel.py configure-source`."
    )
    print("Riel no creará contexto organizacional ni engagements dentro de este checkout.")


def command_configure_source(args: argparse.Namespace) -> None:
    root = root_from()
    directory = instance_dir(root)
    assert directory is not None
    if args.role not in SOURCE_ROLES:
        raise SystemExit(f"Rol inválido. Valores: {', '.join(sorted(SOURCE_ROLES))}")
    if args.mode not in SOURCE_MODES:
        raise SystemExit("Modo inválido. Valores: read, read-write")
    record = instance_record(root)
    sources = record.setdefault("shared_sources", {})
    sources[args.role] = {
        "provider": args.provider,
        "locator": args.locator,
        "mode": args.mode,
        "configured_at": iso(),
    }
    write_json(directory / "instance.json", record)
    print(f"Fuente compartida configurada: {args.role} -> {args.provider}")


def doctor(root: Path, template_mode: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "AGENTS.md",
        "README.md",
        "kernel/CONSTITUTION.md",
        "kernel/shared-source-model.md",
        ".codex/config.toml",
        ".codex/hooks.json",
        "scripts/riel.py",
        "kernel/schemas/instance.schema.json",
        "kernel/schemas/connection.schema.json",
    ]
    for item in required:
        if not (root / item).exists():
            errors.append(f"Falta {item}")

    try:
        import tomllib

        tomllib.loads((root / ".codex" / "config.toml").read_text(encoding="utf-8"))
        for path in (root / ".codex" / "agents").glob("riel-*.toml"):
            tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"TOML inválido: {exc}")
    try:
        json.loads((root / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        for path in (root / "kernel" / "schemas").glob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON inválido: {exc}")

    if (root / "AGENTS.md").stat().st_size > 65536:
        errors.append("AGENTS.md supera 65536 bytes")
    leaked = tracked_private_files(root)
    if leaked:
        errors.append("Git rastrea archivos privados: " + ", ".join(leaked))
    legacy = legacy_local_data(root)
    if legacy:
        errors.append(
            "El checkout contiene datos o agentes locales heredados: "
            + ", ".join(legacy)
            + ". Migrarlos a fuentes compartidas antes de usar esta versión."
        )

    if template_mode:
        return errors, warnings

    directory = instance_dir(root, required=False)
    if directory is None:
        warnings.append("Instancia no conectada; el kernel permanece en modo desarrollo")
        return errors, warnings
    if is_within(directory, root):
        errors.append("El estado técnico está dentro del checkout")
        return errors, warnings
    record_path = directory / "instance.json"
    if not record_path.exists():
        errors.append(f"No existe {record_path}")
        return errors, warnings
    try:
        record = read_json(record_path, {})
    except Exception as exc:
        errors.append(f"Instancia externa inválida: {exc}")
        return errors, warnings
    if record.get("mode") != "shared-first":
        errors.append("La instancia externa no usa mode=shared-first")
    python_executable = Path(str(record.get("python_executable") or ""))
    if not python_executable.is_file():
        errors.append("El intérprete Python registrado para los hooks no existe")
    sources = record.get("shared_sources") or {}
    for role in sorted(REQUIRED_SOURCE_ROLES - set(sources)):
        errors.append(f"Falta fuente compartida obligatoria: {role}")
    for role, source in sources.items():
        for error in validate_source(role, source):
            errors.append(f"shared_sources.{role}: {error}")
    legacy_approval_artifacts = [
        path.name for path in (directory / "approvals", directory / "active-approval") if path.exists()
    ]
    if legacy_approval_artifacts:
        warnings.append(
            "Artefactos técnicos de aprobación heredados ignorados: "
            + ", ".join(legacy_approval_artifacts)
            + ". No conceden permisos; revisalos y retiralos manualmente."
        )
    return errors, warnings


def command_doctor(args: argparse.Namespace) -> None:
    root = root_from()
    errors, warnings = doctor(root, template_mode=args.template)
    for warning in warnings:
        print(f"ADVERTENCIA: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("Riel doctor: OK")


def command_set_context(args: argparse.Namespace) -> None:
    root = root_from()
    directory = instance_dir(root)
    assert directory is not None
    state = active_state(root)
    if args.user_ref:
        state["active_user_ref"] = args.user_ref
    if args.engagement_ref:
        state["active_engagement_ref"] = args.engagement_ref
        state["shared_record_ref"] = args.shared_record or args.engagement_ref
    if args.clear_engagement:
        state["active_engagement_ref"] = None
        state["shared_record_ref"] = None
        state["active_workdir"] = None
    state["updated_at"] = iso()
    write_json(directory / "state.json", state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def command_link_work(args: argparse.Namespace) -> None:
    root = root_from()
    directory = instance_dir(root)
    assert directory is not None
    workdir = Path(args.work_dir).expanduser().resolve()
    if is_within(workdir, root):
        raise SystemExit("El directorio de ejecución debe estar fuera del checkout del kernel.")
    if not workdir.exists() or not workdir.is_dir():
        raise SystemExit(f"No existe el directorio de ejecución: {workdir}")
    state = active_state(root)
    state.update(
        {
            "active_engagement_ref": args.engagement_ref,
            "shared_record_ref": args.shared_record,
            "active_workdir": str(workdir),
            "artifact_ref": args.artifact_ref,
            "updated_at": iso(),
        }
    )
    write_json(directory / "state.json", state)
    print("Ejecución local enlazada. El contexto y la visibilidad siguen en la fuente compartida.")


def command_session_close(args: argparse.Namespace) -> None:
    root = root_from()
    directory = instance_dir(root)
    assert directory is not None
    state = active_state(root)
    engagement_ref = args.engagement_ref or state.get("active_engagement_ref")
    if not engagement_ref:
        raise SystemExit("No hay engagement activo. Usá --engagement-ref.")
    if not args.shared_record:
        raise SystemExit("No se puede cerrar sin una referencia al registro compartido actualizado.")
    receipt = {
        "schema_version": "1.0",
        "id": event_id("receipt"),
        "engagement_ref": engagement_ref,
        "shared_record_ref": args.shared_record,
        "confirmed_by": args.confirmed_by,
        "recorded_at": iso(),
    }
    write_json(directory / "receipts" / f"{receipt['id']}.json", receipt)
    state["shared_record_ref"] = args.shared_record
    state["updated_at"] = iso()
    write_json(directory / "state.json", state)
    print("Sesión cerrada con visibilidad compartida confirmada.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI técnica de Riel Kernel shared-first")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Conectar el checkout con estado técnico externo")
    p.add_argument("--organization-ref", required=True)
    p.add_argument("--owner-ref", required=True)
    p.add_argument("--instance-id")
    p.add_argument("--state-dir")
    p.add_argument("--timezone")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=command_init)

    p = sub.add_parser("configure-source", help="Declarar una fuente compartida")
    p.add_argument("--role", required=True, choices=sorted(SOURCE_ROLES))
    p.add_argument("--provider", required=True)
    p.add_argument("--locator", required=True)
    p.add_argument("--mode", required=True, choices=sorted(SOURCE_MODES))
    p.set_defaults(func=command_configure_source)

    p = sub.add_parser("doctor", help="Validar kernel limpio, instancia externa y fuentes compartidas")
    p.add_argument("--template", action="store_true")
    p.set_defaults(func=command_doctor)

    p = sub.add_parser("set-context", help="Seleccionar referencias compartidas activas")
    p.add_argument("--user-ref")
    p.add_argument("--engagement-ref")
    p.add_argument("--shared-record")
    p.add_argument("--clear-engagement", action="store_true")
    p.set_defaults(func=command_set_context)

    p = sub.add_parser("link-work", help="Enlazar ejecución local fuera del kernel")
    p.add_argument("--engagement-ref", required=True)
    p.add_argument("--shared-record", required=True)
    p.add_argument("--work-dir", required=True)
    p.add_argument("--artifact-ref")
    p.set_defaults(func=command_link_work)

    p = sub.add_parser("session-close")
    p.add_argument("--engagement-ref")
    p.add_argument("--shared-record", required=True)
    p.add_argument("--confirmed-by", required=True)
    p.set_defaults(func=command_session_close)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
