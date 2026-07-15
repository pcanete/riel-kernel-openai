# Política de seguridad

## Alcance

Riel reduce riesgos operativos mediante permisos, hooks, rules, separación de datos y aprobaciones. No constituye una frontera de seguridad absoluta: los hooks no interceptan todas las rutas posibles y deben combinarse con sandbox, permisos del sistema operativo y controles de los conectores.

## Reportes

No publicar secretos ni datos de clientes en issues. Informar vulnerabilidades de manera privada al mantenedor del repositorio.

## Reglas de despliegue

- Python 3.11 o superior.
- Proyecto Codex marcado como confiable únicamente después de revisar `.codex/`.
- Hooks revisados mediante `/hooks`.
- Perfil `riel-workspace` como postura predeterminada.
- `.env`, credenciales, tokens y claves fuera del repositorio.
- Acciones externas únicamente con aprobación formal.

## Datos

Ver `kernel/security-model.md`, `kernel/data-classification.md` y `kernel/threat-model.md`.
