# Instalación y uso

## Opción recomendada: workspace nuevo

1. Crear una carpeta mediante Git:

   ```bash
   git clone https://github.com/pcanete/riel-kernel-openai riel
   cd riel
   ```

2. Inicializar la capa privada:

   ```bash
   python scripts/riel.py init --org-name "Nombre de la organización" --owner "Nombre del responsable"
   ```

3. Validar:

   ```bash
   python scripts/riel.py doctor
   ```

4. Abrir Codex en la raíz. En el primer inicio, usar `/hooks` para revisar y confiar los hooks del repositorio.

5. Pedirle a Riel una primera tarea real y pequeña. El onboarding es progresivo; no se completa un formulario gigante.

## Instalar en una carpeta que ya tiene archivos

No usar `git init + checkout` sobre trabajo existente. Clonar este repositorio en una carpeta temporal y ejecutar:

```bash
python scripts/installer.py --target /ruta/de/la/carpeta-existente
```

El instalador compara archivos y se detiene ante colisiones. No reemplaza nada silenciosamente.

## Comandos principales

```bash
python scripts/riel.py init
python scripts/riel.py doctor
python scripts/riel.py new-engagement --id ejemplo --type client --name "Cliente Ejemplo"
python scripts/riel.py set-context --user nombre --engagement ejemplo
python scripts/riel.py request-approval --action "Publicar sitio" --tool-pattern "git push|deploy" --scope ejemplo --risk medium --reversible
python scripts/riel.py approve <id> --by nombre
python scripts/riel.py activate-approval <id>
python scripts/riel.py session-close --summary "..." --next-action "..." --owner nombre
```

## Actualizaciones

Las capas privadas están ignoradas por Git. Antes de actualizar:

```bash
python scripts/riel.py doctor
git pull --ff-only
python scripts/riel.py doctor
```

Leer `CHANGELOG.md`. Nunca resolver conflictos copiando datos privados dentro del kernel.

## ChatGPT

1. Crear un Project.
2. Copiar `CHATGPT_PROJECT_INSTRUCTIONS.md` en Project settings.
3. Subir `chatgpt/RIEL_CHATGPT_CONTEXT.md`.
4. Para trabajo con un engagement, adjuntar únicamente los archivos privados necesarios y autorizados.

Las instrucciones del Project no reemplazan los hooks ni permisos locales. Las acciones persistentes deben ejecutarse desde Codex o conectores con aprobación explícita.
