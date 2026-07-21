# Arquitectura

## Separación física

- **Kernel:** este checkout Git. Contiene doctrina, adapters de runtime, templates, hooks, skills y pruebas. Es público, actualizable y reemplazable.
- **Estado técnico:** directorio externo enlazado por `.riel-instance.json`. Contiene referencias, recibos y hashes; no contiene contexto organizacional durable ni permisos delegados.
- **Fuentes compartidas:** sistemas accesibles para la organización donde viven contexto, usuarios, engagements, decisiones, loops y visibilidad.
- **Ejecución local:** worktrees o directorios separados para software, contenidos u otros artefactos. Nunca viven dentro del kernel.

## Capas lógicas

- **Capa 0 — kernel:** reglas portables y adapter OpenAI/Codex.
- **Capa 1 — organización:** registro compartido de identidad, gobierno, herramientas y fuentes canónicas.
- **Capa 2 — usuarios:** autoridad, preferencias y necesidades de explicación en un registro compartido.
- **Capa 3 — engagements:** trabajo real, decisiones, estado y próximos pasos en proyectos compartidos.

Las capas 1–3 ya no son carpetas dentro del checkout. Son roles de información resueltos por adapters.

Los adapters no convierten el contenido recuperado en autoridad. Conservan procedencia y referencias, limitan el alcance por organización y engagement, y entregan el contenido como datos no confiables para evaluación.

## Anclas

El kernel usa rutas relativas sólo para sus propios archivos. Las fuentes organizacionales se identifican mediante referencias opacas o URLs del adapter. Una ruta local puede apuntar a ejecución, pero nunca define la identidad de una organización.

## Contexto progresivo

Riel recupera una capa por vez desde la fuente compartida correspondiente. No descarga toda la organización ni persiste una copia local por defecto.

## Fuente de verdad

El sistema compartido declarado prevalece sobre conversaciones, cachés y archivos locales. Los artefactos tienen su propia fuente compartida —por ejemplo GitHub para software o Drive para documentos— y el registro de trabajo conserva el enlace, estado, dueño y próxima acción.

## Prueba de reemplazabilidad

La arquitectura es correcta si se puede eliminar el checkout, clonarlo nuevamente, reconectar los adapters y recuperar la continuidad sin pérdida de contexto organizacional.
