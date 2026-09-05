---
name: riel-session-close
description: Cerrar trabajo con continuidad compartida o preparar un handoff verificable; no convertir cada respuesta o consulta en un registro obligatorio.
---

Verificá el resultado y distinguí terminado, pendiente y bloqueado. Determiná si el pedido o workflow autoriza registro; una consulta sin ese requisito termina con la respuesta, sin inventar tareas.

Cuando corresponda registrar, actualizá la fuente del caso con resultado, referencia del artefacto, decisiones relevantes, pendientes, responsable y próxima acción. Reutilizá una autorización vigente para ese alcance.

Volvé a leer el registro con el conector autorizado y contrastá su contenido con lo escrito. Indicá qué acceso comprobaste; no deduzcas permisos de todo el equipo porque vos pudiste leer. Una URL, respuesta HTTP o recibo local no demuestra por sí solo que el resultado quedó visible.

Si el adapter ofrece un recibo técnico, es opcional y no reemplaza la lectura compartida. No debe atribuirle al comando una verificación que no realizó.

Si falla una sincronización necesaria, entregá el artefacto y declaralo `ejecución realizada / visibilidad pendiente`, indicando el dato pendiente y la próxima acción. No dupliques la memoria institucional en el kernel.
