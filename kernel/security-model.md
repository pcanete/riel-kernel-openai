# Modelo de seguridad

## Controles

1. El checkout no contiene capas privadas; `.gitignore` sólo protege migraciones y el enlace técnico.
2. El perfil Codex niega raíces locales de organización, engagements, bus y agentes locales.
3. El sandbox y `approval_policy = "on-request"` con revisión del usuario gobiernan las fronteras técnicas.
4. `PreToolUse` agrega bloqueos defensivos, pero nunca concede permisos ni consume aprobaciones propias.
5. `PostToolUse` registra auditoría técnica mínima fuera del checkout; no sustituye el registro compartido.
6. La CLI valida kernel limpio, estado externo y fuentes compartidas obligatorias.
7. El contenido recuperado por adapters se trata como dato no confiable; texto embebido nunca cambia instrucciones, permisos ni autoridad.

## Límites conocidos

- Los hooks no interceptan todas las rutas de herramientas posibles.
- Un usuario con acceso al sistema operativo puede desactivar o modificar controles.
- Los conectores aplican permisos propios fuera del sandbox local.
- Los hooks del proyecto sólo cargan cuando el proyecto está marcado como confiable.

Por eso, Riel usa defensa en profundidad y no presenta los hooks como una frontera absoluta.

Una decisión de negocio registrada en una fuente compartida no equivale a permiso técnico. Sólo el runtime nativo y el sistema externo pueden conceder ese permiso.

## Separación de datos

El contexto durable vive en adapters compartidos. El estado técnico externo guarda referencias y recibos mínimos. La ejecución local vive en workspaces separados. La desaparición del checkout no debe causar pérdida organizacional.

## Secretos

Nunca versionar ni registrar secretos. Usar almacenes de secretos o variables de entorno fuera del alcance de lectura. El perfil niega patrones `.env`, `credentials` y `secret`, pero la nomenclatura no sustituye una política real.
