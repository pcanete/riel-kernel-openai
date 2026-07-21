---
name: riel-session-close
description: Cerrar una sesión dejando el estado durable y visible en la fuente compartida; el recibo local es solo evidencia técnica.
---

1. Verificá el resultado y distinguí terminado, pendiente y bloqueado.
2. Actualizá el registro compartido del engagement con resultado, evidencia o artefactos, decisiones, pendientes, responsables y próxima acción.
3. Confirmá que la actualización sea legible por las personas que necesitan visibilidad.
4. Ejecutá `session-close --engagement-ref <ref> --shared-record <ref> --confirmed-by <owner-ref>` para emitir un recibo técnico fuera del checkout.
5. Si no fue posible sincronizar la fuente compartida, no declares cierre completo: reportá `ejecución realizada / visibilidad pendiente` y dejá explícito qué debe publicarse.
6. No crees logs de sesión, buses ni memoria organizacional dentro del kernel.
