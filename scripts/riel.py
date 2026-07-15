#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

KERNEL_VERSION = "2.0.0"
EVENT_TYPES = {"context", "task", "decision", "handoff", "block", "approval", "close", "audit"}
ENGAGEMENT_TYPES = {"client", "internal-project", "case", "research"}
RISK_LEVELS = {"low", "medium", "high", "critical"}


def now() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def iso(value: datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="seconds")


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip().lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    return value.strip("-") or "usuario"


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


def render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def append_ndjson(path: Path, data: dict[str, Any]) -> None:
    lock = path.with_suffix(path.suffix + ".lock")
    with file_lock(lock):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


def event_id(prefix: str = "evt") -> str:
    stamp = now().strftime("%Y%m%dT%H%M%S")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def ensure_instance(root: Path) -> None:
    if not (root / ".riel" / "instance.json").exists():
        raise SystemExit("La instancia no está inicializada. Ejecutá `python scripts/riel.py init`.")


def active_state(root: Path) -> dict[str, Any]:
    return read_json(root / ".riel" / "state.json", {"active_user": None, "active_engagement": None})


def command_init(args: argparse.Namespace) -> None:
    root = root_from()
    instance_path = root / ".riel" / "instance.json"
    if instance_path.exists() and not args.force:
        raise SystemExit("La instancia ya existe. Usá --force únicamente para reparar metadatos.")
    org_name = args.org_name or "Organización sin completar"
    owner = args.owner or "Responsable sin completar"
    owner_id = slug(owner)
    timezone_name = args.timezone or os.environ.get("TZ") or "local"

    for directory in [
        root / "org" / "users",
        root / "engagements",
        root / "bus" / "queues",
        root / "bus" / "events",
        root / "bus" / "approvals",
        root / ".riel",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    org_template = (root / "templates" / "org-context.md").read_text(encoding="utf-8")
    user_template = (root / "templates" / "user.md").read_text(encoding="utf-8")
    org_path = root / "org" / "context.md"
    user_path = root / "org" / "users" / f"{owner_id}.md"
    if not org_path.exists():
        org_path.write_text(render(org_template, {"ORG_NAME": org_name, "OWNER": owner}), encoding="utf-8")
    if not user_path.exists():
        user_path.write_text(render(user_template, {"USER_NAME": owner, "USER_ID": owner_id}), encoding="utf-8")

    write_json(instance_path, {
        "schema_version": "1.0",
        "kernel_version": KERNEL_VERSION,
        "mode": "instance",
        "initialized_at": iso(),
        "timezone": timezone_name,
    })
    write_json(root / ".riel" / "state.json", {
        "active_user": owner_id,
        "active_engagement": None,
        "updated_at": iso(),
    })
    (root / "bus" / "queues" / "riel.ndjson").touch(exist_ok=True)
    print(f"Instancia inicializada. Usuario activo: {owner_id}.")
    print("Revisá y aprobá org/context.md y el perfil del usuario antes de canonizarlos.")


def validate_event(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["schema_version", "id", "type", "status", "sender", "recipient", "scope", "created_at", "payload"]
    for key in required:
        if key not in event:
            errors.append(f"falta `{key}`")
    if event.get("schema_version") != "1.0":
        errors.append("schema_version debe ser 1.0")
    if event.get("type") not in EVENT_TYPES:
        errors.append(f"tipo inválido: {event.get('type')}")
    if event.get("type") == "close" and not event.get("closes"):
        errors.append("un evento close requiere `closes`")
    if not isinstance(event.get("payload"), dict):
        errors.append("payload debe ser objeto")
    try:
        datetime.fromisoformat(str(event.get("created_at")))
    except ValueError:
        errors.append("created_at no es ISO válido")
    return errors


def validate_approval(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["schema_version", "id", "requested_by", "action", "tool_pattern", "scope", "risk", "reversible", "created_at", "expires_at", "status"]
    for key in required:
        if key not in record:
            errors.append(f"falta `{key}`")
    if record.get("risk") not in RISK_LEVELS:
        errors.append("risk inválido")
    if record.get("status") not in {"pending", "approved", "denied", "expired", "consumed"}:
        errors.append("status inválido")
    try:
        re.compile(str(record.get("tool_pattern") or ""))
    except re.error as exc:
        errors.append(f"tool_pattern inválido: {exc}")
    for field in ("created_at", "expires_at"):
        try:
            datetime.fromisoformat(str(record.get(field)))
        except ValueError:
            errors.append(f"{field} no es ISO válido")
    return errors


def tracked_private_files(root: Path) -> list[str]:
    try:
        output = subprocess.check_output(["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    private = ("org/", "engagements/", "bus/", ".riel/")
    return [line for line in output.splitlines() if line.startswith(private) or re.match(r"\.codex/agents/local-.*\.toml$", line)]


def doctor(root: Path, template_mode: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "AGENTS.md", "README.md", "kernel/CONSTITUTION.md", ".codex/config.toml",
        ".codex/hooks.json", "scripts/riel.py", "kernel/schemas/event.schema.json",
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

    if not template_mode:
        if not (root / ".riel" / "instance.json").exists():
            warnings.append("Instancia no inicializada")
        for path in (root / "bus").glob("**/*.ndjson") if (root / "bus").exists() else []:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"{path.relative_to(root)}:{number}: JSON inválido: {exc}")
                    continue
                for err in validate_event(event):
                    errors.append(f"{path.relative_to(root)}:{number}: {err}")
        approvals = root / "bus" / "approvals"
        if approvals.exists():
            for path in approvals.glob("*.json"):
                try:
                    record = read_json(path, {})
                except Exception as exc:
                    errors.append(f"{path.relative_to(root)}: JSON inválido: {exc}")
                    continue
                for err in validate_approval(record):
                    errors.append(f"{path.relative_to(root)}: {err}")
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


def command_new_engagement(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    engagement_id = slug(args.id)
    if args.type not in ENGAGEMENT_TYPES:
        raise SystemExit(f"Tipo inválido. Valores: {', '.join(sorted(ENGAGEMENT_TYPES))}")
    target = root / "engagements" / engagement_id
    if target.exists():
        raise SystemExit(f"El engagement `{engagement_id}` ya existe.")
    (target / "shared").mkdir(parents=True)
    (target / "work").mkdir()
    values = {
        "ENGAGEMENT_ID": engagement_id,
        "ENGAGEMENT_NAME": args.name,
        "ENGAGEMENT_TYPE": args.type,
        "OWNER": args.owner or active_state(root).get("active_user") or "pendiente",
    }
    mapping = {
        "templates/engagement-agents.md": target / "AGENTS.md",
        "templates/engagement-context.md": target / "shared" / "context.md",
        "templates/open-loops.md": target / "shared" / "open-loops.md",
        "templates/decisions.md": target / "shared" / "decisions.md",
        "templates/session-log.md": target / "shared" / "session-log.md",
    }
    for source, destination in mapping.items():
        text = (root / source).read_text(encoding="utf-8")
        destination.write_text(render(text, values), encoding="utf-8")
    print(f"Engagement creado: engagements/{engagement_id}")


def command_set_context(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    state = active_state(root)
    if args.user:
        user = slug(args.user)
        if not (root / "org" / "users" / f"{user}.md").exists():
            raise SystemExit(f"No existe org/users/{user}.md")
        state["active_user"] = user
    if args.engagement:
        engagement = slug(args.engagement)
        if not (root / "engagements" / engagement).exists():
            raise SystemExit(f"No existe engagements/{engagement}")
        state["active_engagement"] = engagement
    if args.clear_engagement:
        state["active_engagement"] = None
    state["updated_at"] = iso()
    write_json(root / ".riel" / "state.json", state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def command_bus_send(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    if args.type not in EVENT_TYPES - {"close", "audit"}:
        raise SystemExit("Tipo no permitido para bus-send.")
    try:
        payload = json.loads(args.payload) if args.payload else {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Payload JSON inválido: {exc}")
    event = {
        "schema_version": "1.0",
        "id": event_id(),
        "type": args.type,
        "status": "open",
        "sender": args.sender,
        "recipient": slug(args.recipient),
        "scope": args.scope,
        "created_at": iso(),
        "payload": payload,
    }
    append_ndjson(root / "bus" / "queues" / f"{event['recipient']}.ndjson", event)
    print(event["id"])


def command_bus_close(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    event = {
        "schema_version": "1.0",
        "id": event_id("close"),
        "type": "close",
        "status": "closed",
        "sender": args.sender,
        "recipient": slug(args.recipient),
        "scope": args.scope,
        "created_at": iso(),
        "payload": {"reason": args.reason},
        "closes": args.event_id,
    }
    append_ndjson(root / "bus" / "queues" / f"{event['recipient']}.ndjson", event)
    print(event["id"])


def command_request_approval(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    if args.risk not in RISK_LEVELS:
        raise SystemExit("Riesgo inválido.")
    pattern = args.tool_pattern.strip()
    if pattern in {".*", ".+", "^.*$", "^.+$"} or len(pattern) < 3:
        raise SystemExit("tool-pattern demasiado amplio. Describí la herramienta o comando exacto.")
    if len(pattern) > 300:
        raise SystemExit("tool-pattern demasiado largo (máximo 300 caracteres).")
    if not 1 <= args.expires_minutes <= 1440:
        raise SystemExit("expires-minutes debe estar entre 1 y 1440.")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise SystemExit(f"tool-pattern inválido: {exc}")
    approval_id = event_id("apr")
    record = {
        "schema_version": "1.0",
        "id": approval_id,
        "requested_by": args.requested_by,
        "approved_by": None,
        "action": args.action,
        "tool_pattern": pattern,
        "scope": args.scope,
        "risk": args.risk,
        "reversible": bool(args.reversible),
        "reason": args.reason or "",
        "created_at": iso(),
        "approved_at": None,
        "expires_at": iso(now() + timedelta(minutes=args.expires_minutes)),
        "status": "pending",
        "consumed_at": None,
    }
    write_json(root / "bus" / "approvals" / f"{approval_id}.json", record)
    print(approval_id)


def load_approval(root: Path, approval_id: str) -> tuple[Path, dict[str, Any]]:
    path = root / "bus" / "approvals" / f"{approval_id}.json"
    if not path.exists():
        raise SystemExit(f"No existe la aprobación {approval_id}")
    return path, read_json(path, {})


def command_approve(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    path, record = load_approval(root, args.id)
    if record.get("status") != "pending":
        raise SystemExit(f"Estado actual no aprobable: {record.get('status')}")
    if datetime.fromisoformat(record["expires_at"]) < now():
        record["status"] = "expired"
        write_json(path, record)
        raise SystemExit("La aprobación expiró.")
    record["status"] = "approved"
    record["approved_by"] = args.by
    record["approved_at"] = iso()
    write_json(path, record)
    print(f"Aprobada: {args.id}")


def command_deny(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    path, record = load_approval(root, args.id)
    if record.get("status") not in {"pending", "approved"}:
        raise SystemExit(f"Estado actual no denegable: {record.get('status')}")
    record["status"] = "denied"
    record["approved_by"] = args.by
    record["reason"] = args.reason or record.get("reason", "")
    write_json(path, record)
    print(f"Denegada: {args.id}")


def approval_is_valid(record: dict[str, Any], subject: str) -> bool:
    if record.get("status") != "approved" or record.get("consumed_at"):
        return False
    try:
        if datetime.fromisoformat(record["expires_at"]) < now():
            return False
        return bool(re.search(record["tool_pattern"], subject, re.IGNORECASE))
    except (ValueError, re.error, KeyError):
        return False


def command_activate_approval(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    _, record = load_approval(root, args.id)
    if record.get("status") != "approved" or record.get("consumed_at"):
        raise SystemExit("La aprobación no está aprobada o ya fue consumida.")
    try:
        if datetime.fromisoformat(record["expires_at"]) < now():
            raise SystemExit("La aprobación expiró.")
    except (ValueError, KeyError):
        raise SystemExit("La aprobación tiene un vencimiento inválido.")
    if args.subject and not approval_is_valid(record, args.subject):
        raise SystemExit("La aprobación no coincide con el subject indicado.")
    (root / ".riel" / "active-approval").write_text(args.id + "\n", encoding="utf-8")
    print(f"Aprobación activa para el próximo uso coincidente: {args.id}")


def command_new_agent(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    _, approval = load_approval(root, args.approval)
    if not approval_is_valid(approval, "agent:create"):
        raise SystemExit("Se requiere aprobación vigente cuyo patrón coincida con `agent:create`.")
    agent_id = slug(args.id).replace("-", "_")
    target = root / ".codex" / "agents" / f"local-{agent_id}.toml"
    if target.exists():
        raise SystemExit(f"El agente {agent_id} ya existe.")
    instructions = args.instructions.replace(chr(34) * 3, chr(39) * 3)
    content = (
        f'name = "{agent_id}"\n'
        f'description = {json.dumps(args.description, ensure_ascii=False)}\n'
        f'model_reasoning_effort = "{args.reasoning_effort}"\n'
        f'sandbox_mode = "{args.sandbox_mode}"\n'
        'developer_instructions = """\n'
        f'{instructions}\n'
        'No escribas directamente en el bus; devolvé resultados a Riel.\n'
        '"""\n'
    )
    target.write_text(content, encoding="utf-8")
    approval["status"] = "consumed"
    approval["consumed_at"] = iso()
    approval["consumed_subject"] = "agent:create"
    write_json(root / "bus" / "approvals" / f"{args.approval}.json", approval)
    print(f"Agente local creado: {target.relative_to(root)}")


def command_retire_agent(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    _, approval = load_approval(root, args.approval)
    if not approval_is_valid(approval, "agent:retire"):
        raise SystemExit("Se requiere aprobación vigente cuyo patrón coincida con `agent:retire`.")
    agent_id = slug(args.id).replace("-", "_")
    target = root / ".codex" / "agents" / f"local-{agent_id}.toml"
    if not target.exists():
        raise SystemExit(f"No existe {target.relative_to(root)}")
    archive = root / ".riel" / "retired-agents"
    archive.mkdir(parents=True, exist_ok=True)
    shutil.move(str(target), str(archive / f"{target.stem}-{now().strftime('%Y%m%d%H%M%S')}.toml"))
    approval["status"] = "consumed"
    approval["consumed_at"] = iso()
    approval["consumed_subject"] = "agent:retire"
    write_json(root / "bus" / "approvals" / f"{args.approval}.json", approval)
    print(f"Agente retirado: {agent_id}")


def command_session_close(args: argparse.Namespace) -> None:
    root = root_from()
    ensure_instance(root)
    state = active_state(root)
    engagement = args.engagement or state.get("active_engagement")
    if not engagement:
        raise SystemExit("No hay engagement activo. Usá --engagement.")
    log_path = root / "engagements" / slug(engagement) / "shared" / "session-log.md"
    if not log_path.exists():
        raise SystemExit(f"No existe {log_path.relative_to(root)}")
    block = (
        f"\n## {iso()}\n\n"
        f"- Qué se hizo: {args.summary}\n"
        f"- Qué quedó abierto: {args.open or 'ver open-loops.md'}\n"
        f"- Dueño: {args.owner}\n"
        f"- Próxima acción: {args.next_action}\n"
    )
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(block)
    print(f"Sesión registrada en {log_path.relative_to(root)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI de Riel Kernel")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Inicializar capas privadas")
    p.add_argument("--org-name")
    p.add_argument("--owner")
    p.add_argument("--timezone")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=command_init)

    p = sub.add_parser("doctor", help="Validar estructura, bus y privacidad")
    p.add_argument("--template", action="store_true", help="Validar el repositorio sin exigir una instancia")
    p.set_defaults(func=command_doctor)

    p = sub.add_parser("new-engagement")
    p.add_argument("--id", required=True)
    p.add_argument("--type", required=True, choices=sorted(ENGAGEMENT_TYPES))
    p.add_argument("--name", required=True)
    p.add_argument("--owner")
    p.set_defaults(func=command_new_engagement)

    p = sub.add_parser("set-context")
    p.add_argument("--user")
    p.add_argument("--engagement")
    p.add_argument("--clear-engagement", action="store_true")
    p.set_defaults(func=command_set_context)

    p = sub.add_parser("bus-send")
    p.add_argument("--recipient", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--sender", default="riel")
    p.add_argument("--scope", default="workspace")
    p.add_argument("--payload", default="{}")
    p.set_defaults(func=command_bus_send)

    p = sub.add_parser("bus-close")
    p.add_argument("event_id")
    p.add_argument("--recipient", default="riel")
    p.add_argument("--sender", default="riel")
    p.add_argument("--scope", default="workspace")
    p.add_argument("--reason", default="completed")
    p.set_defaults(func=command_bus_close)

    p = sub.add_parser("request-approval")
    p.add_argument("--action", required=True)
    p.add_argument("--tool-pattern", required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--risk", required=True, choices=sorted(RISK_LEVELS))
    p.add_argument("--reversible", action="store_true")
    p.add_argument("--reason")
    p.add_argument("--requested-by", default="riel")
    p.add_argument("--expires-minutes", type=int, default=120)
    p.set_defaults(func=command_request_approval)

    p = sub.add_parser("approve")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.set_defaults(func=command_approve)

    p = sub.add_parser("deny")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.add_argument("--reason")
    p.set_defaults(func=command_deny)

    p = sub.add_parser("activate-approval")
    p.add_argument("id")
    p.add_argument("--subject")
    p.set_defaults(func=command_activate_approval)

    p = sub.add_parser("new-agent")
    p.add_argument("--id", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--instructions", required=True)
    p.add_argument("--approval", required=True)
    p.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default="medium")
    p.add_argument("--sandbox-mode", choices=["read-only", "workspace-write"], default="read-only")
    p.set_defaults(func=command_new_agent)

    p = sub.add_parser("retire-agent")
    p.add_argument("--id", required=True)
    p.add_argument("--approval", required=True)
    p.set_defaults(func=command_retire_agent)

    p = sub.add_parser("session-close")
    p.add_argument("--summary", required=True)
    p.add_argument("--next-action", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--open")
    p.add_argument("--engagement")
    p.set_defaults(func=command_session_close)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
