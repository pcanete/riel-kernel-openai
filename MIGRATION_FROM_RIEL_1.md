# Migración desde Riel Kernel 1.x

Esta edición es una reconstrucción, no un reemplazo in-place. Migrá primero a una carpeta o repositorio nuevo y conservá el repositorio anterior como respaldo de solo lectura.

## Correspondencias

| Riel 1.x | Riel 2.x |
|---|---|
| `CLAUDE.md` | `AGENTS.md` + `kernel/` + skills |
| `.claude/agents/riel.md` | identidad principal en `AGENTS.md` |
| `.claude/agents/<especialista>.md` | revisar y recrear como `.codex/agents/local-*.toml` |
| `clients/`, `projects/`, `casos/` | `engagements/<id>/` con tipo en contexto |
| documentación privada en `docs/` | `org/` o `engagements/<id>/shared/` |
| bus NDJSON anterior | archivar; importar solo eventos validados |

## Procedimiento seguro

1. Crear el repositorio nuevo y ejecutar `python scripts/riel.py init`.
2. Completar y revisar `org/context.md` y el perfil del responsable.
3. Crear cada unidad con `new-engagement`; no copiar raíces antiguas directamente.
4. Pasar contexto vigente a `shared/context.md`; dejar material histórico en `work/legacy/`.
5. Convertir decisiones abiertas y pendientes, no todo el historial conversacional.
6. Auditar cada agente anterior. Recrearlo únicamente si cumple el criterio de repetición, frontera estable y aprobación formal.
7. No importar secretos, `.env`, credenciales, logs completos ni archivos ignorados sin clasificación.
8. Ejecutar `python scripts/riel.py doctor` antes del primer uso.

## Qué no migrar automáticamente

- aprobaciones antiguas;
- permisos implícitos;
- agentes no evaluados;
- datos duplicados o sin dueño;
- documentación específica de una organización dentro del kernel público.

La migración termina cuando cada engagement tiene contexto, decisiones, open loops, dueño y próxima acción verificables.
