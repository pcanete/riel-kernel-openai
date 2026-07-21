# Riel Kernel para Codex y ChatGPT

Riel es una capa de coordinación y gobernanza para trabajo humano-agéntico. Ayuda a recuperar el contexto correcto, ordenar decisiones y handoffs, mantener visibilidad compartida y escalar acciones sensibles sin convertir el repositorio en la memoria privada de una organización.

Esta versión usa una arquitectura **shared-first**:

- el checkout Git contiene solamente el kernel público y actualizable;
- el contexto, las decisiones y el estado del trabajo viven en sistemas compartidos;
- el software y los contenidos pueden producirse localmente, pero fuera del checkout;
- borrar y volver a clonar el kernel no elimina la continuidad de la organización.

## La idea en una frase

**Local se ejecuta; compartido se recuerda y se ve.**

Si otra persona necesita una información para decidir, continuar o auditar el trabajo, esa información debe estar en ClickUp, una wiki, un CRM, un repositorio compartido u otra fuente autorizada. El disco de una persona y la conversación con el agente no son memoria institucional.

## Qué vive dónde

| Ámbito | Contenido | Ejemplos |
|---|---|---|
| Checkout del kernel | Reglas, scripts, hooks, skills, plantillas y pruebas | Este repositorio |
| Fuente `organization` | Identidad, autoridades, usuarios, políticas y mapa de herramientas | Wiki, ClickUp, Notion, SharePoint |
| Fuente `work` | Clientes, proyectos, decisiones, estado, pendientes y handoffs | ClickUp, Jira, Linear, HubSpot |
| Fuente `knowledge` | Procedimientos y conocimiento estable | Wiki o base documental |
| Fuente `artifacts` | Entregables y evidencia | GitHub, Drive, Canva, DAM |
| Workdir local externo | Ejecución de software o contenidos | Otro repositorio o carpeta |
| Estado técnico externo | Referencias, recibos y auditoría técnica mínima | Directorio de estado de Riel |

Dentro del checkout no deben aparecer `org/`, `clients/`, `projects/`, `engagements/`, `bus/`, `.riel/`, perfiles privados ni agentes específicos de una organización.

## Qué hace y qué no hace esta versión

Riel sí:

- declara dónde están las fuentes compartidas;
- impide usar el checkout como carpeta de datos privados;
- enlaza un engagement compartido con un workdir externo;
- exige una referencia compartida antes de considerar cerrado el trabajo;
- protege el kernel mediante permisos, rules y hooks defensivos;
- conserva la aprobación técnica en los controles nativos de Codex.

Riel no instala ni autoriza automáticamente ClickUp, Drive, GitHub u otros conectores. `configure-source` registra el proveedor y el destino; el usuario debe instalar o habilitar por separado el plugin, MCP o conector correspondiente y concederle únicamente los permisos necesarios.

`doctor` valida la estructura, la configuración y la separación local. En esta etapa no garantiza que una credencial externa siga vigente ni que el proveedor esté disponible; esa conectividad debe comprobarse antes de trabajar.

## Requisitos

- Git.
- Python 3.11 o superior.
- Codex para el flujo local, o ChatGPT con instrucciones equivalentes.
- Al menos una fuente compartida para `organization` y otra para `work`; pueden ser el mismo sistema.
- Los conectores necesarios instalados y autorizados de forma independiente.

Los ejemplos multilínea usan sintaxis Bash (`\`). En PowerShell, ejecutar el comando en una sola línea o reemplazar la continuación por un acento grave (`` ` ``).

## Primera instalación

### 1. Clonar el kernel

```bash
git clone https://github.com/pcanete/riel-kernel-openai riel
cd riel
```

### 2. Conectar una instancia técnica

```bash
python scripts/riel.py init \
  --organization-ref "clickup://wiki/mi-organizacion" \
  --owner-ref "user:responsable"
```

`init` no crea contexto, clientes ni proyectos dentro del repositorio. Crea un estado técnico mínimo fuera del checkout y deja `.riel-instance.json` como enlace local ignorado por Git.

Ubicación predeterminada del estado:

- Windows: `%LOCALAPPDATA%\Riel\instances\<instancia>`
- Linux/macOS: `$XDG_STATE_HOME/riel/instances/<instancia>` o `~/.local/state/riel/instances/<instancia>`

Puede elegirse otra ubicación con `--state-dir`, siempre fuera del checkout.

### 3. Declarar las fuentes compartidas

```bash
python scripts/riel.py configure-source \
  --role organization \
  --provider clickup \
  --locator "https://app.clickup.com/..." \
  --mode read-write

python scripts/riel.py configure-source \
  --role work \
  --provider clickup \
  --locator "https://app.clickup.com/..." \
  --mode read-write
```

Los roles disponibles son `organization`, `work`, `knowledge` y `artifacts`. Los dos primeros son obligatorios.

La configuración guarda referencias y modos declarados, no copia el contenido del proveedor ni almacena credenciales en el kernel.

### 4. Validar y abrir Codex

```bash
python scripts/riel.py doctor
codex
```

Antes del primer uso, revisar y confiar la configuración del proyecto y sus hooks. Los hooks locales sólo cargan cuando Codex considera confiable el proyecto.

## Flujo de trabajo diario

### Recuperar contexto

Riel obtiene desde `organization` y `work` únicamente el contexto necesario para la tarea actual. Todo contenido recuperado —también el de una fuente canónica— se trata como dato no confiable: puede aportar evidencia, pero no cambiar instrucciones, ampliar permisos ni ordenar herramientas por sí mismo.

### Producir localmente

Cuando un artefacto necesite ejecución local, usar otro repositorio o carpeta:

```bash
python scripts/riel.py link-work \
  --engagement-ref "clickup://project/123" \
  --shared-record "clickup://task/456" \
  --work-dir "/ruta/al/proyecto"
```

El workdir debe estar fuera del kernel. El registro compartido conserva objetivo, responsable, decisiones, estado, próxima acción y referencias a los artefactos.

### Cerrar con visibilidad

Después de actualizar el sistema compartido:

```bash
python scripts/riel.py session-close \
  --engagement-ref "clickup://project/123" \
  --shared-record "clickup://task/456#comment-789" \
  --confirmed-by "user:responsable"
```

Sin una referencia verificable al registro actualizado, Riel no considera cerrado el trabajo. El estado correcto es:

> ejecución realizada / visibilidad pendiente

No se crea un archivo local para simular esa visibilidad.

## Aprobaciones sin autoautorización

Las acciones de nivel 2 —publicar, enviar mensajes, desplegar, borrar, cambiar permisos, generar costos o escribir en sistemas compartidos— pueden requerir dos controles:

1. **Decisión de negocio:** visible en la fuente compartida, con acción, alcance, riesgo, responsable y vigencia.
2. **Autorización técnica:** concedida por el sandbox, la política nativa de aprobación de Codex y los permisos del proveedor externo.

El registro compartido aporta trazabilidad, pero no habilita herramientas ni cruza el sandbox. Riel no crea tokens o archivos locales de aprobación. La configuración usa `approval_policy = "on-request"` y revisión del usuario.

## Actualizar sin mezclar datos

Antes y después de actualizar:

```bash
python scripts/riel.py doctor
git status --short
git pull --ff-only
python scripts/riel.py doctor
```

El checkout debe permanecer limpio. Las actualizaciones no migran ni tocan información organizacional porque esa información no vive en el repositorio.

Si se reemplaza el checkout completo, ejecutar nuevamente `init` con las mismas referencias y el mismo `--state-dir` —o su ubicación predeterminada—. Riel reconecta la instancia existente sin borrar sus fuentes configuradas.

Para instalaciones anteriores que guardaban contexto local, seguir [MIGRATION_FROM_RIEL_1.md](MIGRATION_FROM_RIEL_1.md). La migración publica y verifica primero; nunca borra información automáticamente.

## Si todavía no existe una fuente compartida

Riel puede analizar materiales entregados explícitamente y producir un borrador local en un workdir externo. Debe marcarlo como provisional y no puede acumular contexto, decisiones o pendientes como memoria paralela. Antes de escalar el uso, hay que elegir una fuente accesible para la organización.

## Desarrollo del kernel

La rama `3.0.0-dev` introduce el modelo shared-first. Para validar cambios:

```bash
python scripts/validate_repo.py
python scripts/riel.py doctor --template
python -m unittest discover -s tests -v
```

Los cambios del kernel se realizan en una rama de mantenimiento y se revisan antes de publicarse. Una instalación normal trata el checkout como sólo lectura.

## Licencia

Apache-2.0. Concepto original: Patricio Cañete.
