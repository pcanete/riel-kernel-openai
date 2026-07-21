# Política de seguridad

## Alcance

Riel reduce riesgos operativos mediante sandbox, aprobación nativa, hooks defensivos, separación de datos y permisos de conectores. No constituye una frontera de seguridad absoluta: los hooks no interceptan todas las rutas posibles y nunca conceden permisos; sólo complementan los controles nativos del runtime y del sistema operativo.

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
