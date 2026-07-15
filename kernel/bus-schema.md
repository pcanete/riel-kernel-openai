# Bus append-only

## Principio

Cada cola es NDJSON: una línea JSON por evento. Las líneas existentes nunca se editan ni eliminan. El cierre se expresa con un nuevo evento `type: close` y el campo `closes`.

## Evento mínimo

```json
{
  "schema_version": "1.0",
  "id": "evt-...",
  "type": "task",
  "status": "open",
  "sender": "riel",
  "recipient": "riel",
  "scope": "engagement:ejemplo",
  "created_at": "2026-07-15T10:00:00-03:00",
  "payload": {}
}
```

## Tipos

`context`, `task`, `decision`, `handoff`, `block`, `approval`, `close`, `audit`.

## Concurrencia

La CLI usa bloqueo de archivo según plataforma. Los subagentes no escriben directamente: devuelven el resultado al coordinador.
