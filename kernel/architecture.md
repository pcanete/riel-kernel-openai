# Arquitectura

## Capas

- **Capa 0 — kernel:** reglas, CLI, schemas, hooks, skills y agentes base. Versionada y portable.
- **Capa 1 — organización:** `org/context.md`, herramientas autorizadas, políticas locales y registro de agentes.
- **Capa 2 — usuarios:** `org/users/<id>.md`, autoridad, preferencias y nivel de uso.
- **Capa 3 — engagements:** contexto y trabajo de una unidad concreta.

## Ancla

Todas las rutas son relativas a la raíz Git. No se guardan rutas absolutas en contratos portables.

## Contexto progresivo

Codex descubre `AGENTS.md` desde la raíz hasta el directorio de trabajo. Riel usa esta jerarquía para mantener reglas globales en la raíz y reglas privadas específicas dentro de cada engagement.

## Fuente de verdad

El hilo principal conserva requisitos y decisiones. Los subagentes absorben exploración ruidosa y devuelven resúmenes. Riel persiste únicamente resultados validados.

## Escritura

Riel es el único escritor del bus. Las herramientas de escritura externa requieren aprobación consumible. Los hooks protegen el kernel en modo instancia.
