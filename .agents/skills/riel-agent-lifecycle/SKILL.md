---
name: riel-agent-lifecycle
description: Proponer, crear, evaluar o retirar agentes locales cuando una función repetitiva tiene frontera estable; no usar por entusiasmo o para una tarea única.
---

Criterios de nacimiento:
- la función apareció al menos tres veces o existe evidencia equivalente;
- tiene entrada, salida y frontera claras;
- no duplica un agente o skill existente;
- el beneficio supera costo, contexto y riesgo;
- existe aprobación nivel 2 con patrón `agent:create`.

Crear con `python scripts/riel.py new-agent ... --approval <id>`. El archivo será `.codex/agents/local-<id>.toml` y quedará fuera de Git.

Evaluar después de uso real: precisión, costo, escalaciones, solapamiento y trazabilidad. Retirar con aprobación `agent:retire`. Registrar el agente y su estado en `org/context.md`.
