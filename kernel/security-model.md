# Modelo de seguridad

## Controles

1. `.gitignore` separa datos privados.
2. El perfil Codex limita escritura a capas privadas y niega secretos.
3. Rules bloquean o solicitan aprobación para comandos sensibles.
4. `PreToolUse` aplica protección adicional y aprobación consumible.
5. `PostToolUse` registra trazabilidad mínima con redacción.
6. CLI valida esquemas, estructura y archivos privados rastreados por Git.

## Límites conocidos

- Los hooks no interceptan todas las rutas de herramientas posibles.
- Un usuario con acceso al sistema operativo puede desactivar o modificar controles.
- Los conectores aplican permisos propios fuera del sandbox local.
- La clasificación semántica de una herramienta por nombre puede producir falsos positivos o negativos.

Por eso, Riel usa defensa en profundidad y no presenta los hooks como una frontera absoluta.

## Secretos

Nunca versionar ni registrar secretos. Usar almacenes de secretos o variables de entorno fuera del alcance de lectura. El perfil niega patrones `.env`, `credentials` y `secret`, pero la nomenclatura no sustituye una política real.
