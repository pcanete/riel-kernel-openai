# Instalación shared-first

## Antes de empezar

Riel no guardará la organización dentro de esta carpeta. Prepará dos destinos compartidos:

1. `organization`: Wiki o registro de identidad, gobierno, usuarios y herramientas.
2. `work`: sistema de clientes, proyectos, decisiones, estado y próximas acciones.

Pueden ser dos áreas de ClickUp, una Wiki y un gestor de proyectos, u otras herramientas accesibles para la organización.

## Instalar

1. Clonar el kernel en una carpeta propia y vacía.
2. Desde una terminal humana, ejecutar `riel.py init` con referencias técnicas, no con dossiers ni contexto.
3. Configurar las fuentes `organization` y `work`.
4. Ejecutar `riel.py doctor`.
5. Abrir Codex, revisar `/hooks` y pedir una primera tarea pequeña.

## Regla para el usuario

> Riel es infraestructura actualizable. El conocimiento de tu organización pertenece a sistemas compartidos. El trabajo local es ejecución, no memoria institucional.

## Qué nunca se crea aquí

- carpetas de clientes o proyectos;
- contexto de organización o perfiles de usuarios;
- decisiones, open loops o session logs;
- agentes propios de una organización;
- secretos o credenciales.

## Qué puede existir localmente

- `.riel-instance.json`, enlace técnico recreable e ignorado por Git;
- un proyecto de software o contenidos en otra carpeta;
- cachés y borradores descartables sin valor canónico.

## Actualizar

Ejecutar `doctor`, comprobar un `git status` limpio, hacer `git pull --ff-only` y volver a ejecutar `doctor`.

Si una versión anterior dejó `org/`, `engagements/`, `bus/`, `.riel/` o agentes `local-*`, `doctor` se detendrá. Primero hay que llevar el contexto y la visibilidad a fuentes compartidas; no borrarlos por reflejo.
