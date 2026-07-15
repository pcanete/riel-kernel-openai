---
name: riel-session-close
description: Cerrar una sesión sustantiva dejando continuidad verificable en archivos; no usar para intercambios triviales sin trabajo persistente.
---

1. Confirmá entregables escritos.
2. Actualizá `shared/open-loops.md` y `shared/decisions.md`.
3. Cerrá eventos del bus con un evento `close`; nunca edites líneas históricas.
4. Ejecutá `python scripts/riel.py session-close --summary ... --next-action ... --owner ...`.
5. Informá: realizado, abierto, dueño y próxima acción concreta.
