# Clasificación y ubicación de datos

## Regla principal

La clasificación define controles; la ubicación define además quién conserva visibilidad. Ningún dato organizacional durable se almacena dentro del checkout del kernel, cualquiera sea su clasificación.

## Clases

- `PUBLIC`: material publicable, como el propio kernel.
- `INTERNAL`: operación interna sin datos especialmente sensibles.
- `CONFIDENTIAL`: clientes, estrategia, acuerdos, finanzas o información personal.
- `RESTRICTED`: secretos, credenciales y datos regulados.

## Ubicación

- Contexto, decisiones, tareas, perfiles, handoffs y estado: fuente compartida autorizada con permisos acordes a la clasificación.
- Artefactos de ejecución: repositorio o directorio separado, con una referencia visible en la fuente compartida.
- Credenciales: gestor de secretos o mecanismo nativo del proveedor; nunca archivos del kernel, logs ni registros compartidos en texto plano.
- Estado técnico de Riel: directorio externo al checkout, sin contenido de negocio y con acceso mínimo.
- Caché: temporal, reconstruible, con expiración y sin convertirse en fuente de verdad.

Si no existe un destino compartido adecuado para la clasificación, Riel no crea un sustituto local silencioso: informa el bloqueo.
