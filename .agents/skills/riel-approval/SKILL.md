---
name: riel-approval
description: Solicitar, revisar, aprobar y activar permisos de nivel 2 para acciones externas o irreversibles; no usar para lectura o borradores locales.
---

1. Explicá acción, motivo, impacto, riesgo, alcance, reversibilidad y vencimiento.
2. Creá la solicitud con `python scripts/riel.py request-approval` y un `tool-pattern` específico.
3. La persona responsable aprueba con `python scripts/riel.py approve <id> --by <usuario>` o deniega con `deny`.
4. Activá justo antes de ejecutar: `python scripts/riel.py activate-approval <id>`.
5. La aprobación se consume en el primer comando o herramienta externa coincidente.
6. No reutilices una aprobación, no amplíes su alcance y no la trates como autorización permanente.
