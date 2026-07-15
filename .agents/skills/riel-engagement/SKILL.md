---
name: riel-engagement
description: Crear, abrir, retomar o cerrar una unidad de trabajo en engagements/; usar para clientes, proyectos internos, casos o research.
---

- Usá una única raíz: `engagements/<id>/`.
- Para crear: `python scripts/riel.py new-engagement --id <id> --type <client|internal-project|case|research> --name <nombre>`.
- Antes de trabajar, leer `shared/context.md`, `shared/open-loops.md`, `shared/decisions.md` y el `AGENTS.md` local.
- Definí resultado, dueño, criterio de cierre y próxima acción.
- Escribí entregables en `work/` o en el archivo canónico correspondiente.
- No mezclar datos de dos engagements ni promover aprendizajes a `org/` sin revisión humana.
