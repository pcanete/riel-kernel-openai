# Changelog

## 2.0.1 — 2026-07-15

Correcciones de compatibilidad verificadas en Windows y Codex CLI.

- El guard reconoce rutas absolutas de Windows aunque el workspace contenga espacios, caracteres no ASCII o una ruta corta 8.3.
- Compatibilidad de hooks tanto con el flag estable actual como con `codex_hooks` en Codex CLI 0.118.x.
- Suite completa validada en Windows con 14 pruebas aprobadas.

## 2.0.0 — 2026-07-15

Reconstrucción para Codex y ChatGPT.

- `AGENTS.md` como contrato principal con carga por capas.
- Separación estricta entre kernel versionado y datos privados.
- Raíz única `engagements/` con tipos declarativos.
- CLI estándar sin dependencias para inicialización, validación, bus, engagements, aprobaciones y agentes locales.
- Aprobaciones formales, temporales y consumibles.
- Hooks Codex para protección del kernel, acciones destructivas, conectores con escritura y auditoría mínima.
- Perfil de permisos de mínimo privilegio y rules para comandos sensibles.
- Skills de onboarding, engagements, aprobaciones, ciclo de agentes y cierre de sesión.
- Subagentes base de exploración y auditoría en modo de solo lectura.
- Esquemas JSON, threat model, clasificación de datos y política de seguridad.
- Instalador con detección de colisiones.
- Pruebas unitarias y GitHub Actions.
- Paquete de instrucciones para ChatGPT Projects.
