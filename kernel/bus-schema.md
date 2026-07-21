# Contrato de eventos compartidos

Riel conserva el concepto lógico de evento para trazabilidad, pero no mantiene un bus de negocio dentro del checkout.

## Persistencia

- Los eventos durables viven en la fuente compartida de trabajo o conocimiento.
- El adaptador traduce la estructura del proveedor a los campos mínimos de Riel.
- El log técnico externo de hooks sirve para diagnóstico; no sustituye el historial visible de la organización.
- No se crean `bus/inbox`, `bus/outbox` ni archivos NDJSON locales con contexto organizacional.

## Campos mínimos

- `id`: identificador estable.
- `type`: tarea, decisión, handoff, bloqueo, aprobación o contexto.
- `organization_ref`: referencia a la organización.
- `engagement_ref`: referencia opcional al engagement.
- `actor_ref`: responsable o emisor verificable.
- `created_at`: fecha y zona horaria.
- `summary`: descripción breve.
- `record_ref`: URL o identificador del registro compartido.
- `evidence_refs`: referencias a artefactos o evidencia.

`kernel/schemas/event.schema.json` documenta la forma interoperable. No prescribe una base local.
