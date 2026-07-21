# Riel

**Riel ayuda a las personas de una organización a trabajar con colaboradores agénticos sin perder contexto, control ni continuidad.**

No dirige la empresa ni reemplaza a sus responsables. Coordina: entiende qué se está haciendo, recupera el contexto necesario, ordena decisiones y entregas, y pide intervención humana cuando una acción deja de ser reversible.

Este repositorio es el **kernel de Riel para Codex y ChatGPT**: un esqueleto instalable y actualizable, vacío de información de cualquier organización.

---

## El problema que resuelve

Cuando un equipo empieza a trabajar con IA, el trabajo suele quedar repartido entre conversaciones, computadoras y asistentes personales.

- Cada sesión vuelve a pedir explicaciones que la organización ya dio.
- Una decisión importante queda enterrada en un chat.
- Lo que avanzó una persona no puede retomarlo fácilmente otra.
- El equipo no sabe qué está haciendo el agente ni cuál es el próximo paso.
- La información de un cliente termina mezclada con la configuración de una herramienta.
- Nadie tiene claro qué puede hacer la IA por sí sola y qué debe aprobar una persona.

Riel ordena esa colaboración alrededor de una regla sencilla:

> **En local se ejecuta. En compartido se recuerda y se ve.**

El software, los contenidos y otros entregables pueden producirse en una computadora. Pero el contexto, las decisiones, el estado y las próximas acciones deben quedar en una fuente que pueda consultar el resto de la organización: por ejemplo ClickUp, una wiki, un CRM, Drive o el repositorio compartido del proyecto.

## Las tres capas

Riel mantiene separadas tres cosas para que cada instalación pueda actualizarse sin riesgo y cada organización conserve el control de su información.

| Capa | Qué contiene | Dónde vive |
|---|---|---|
| **Esqueleto** | Las reglas y herramientas generales de Riel. | Este repositorio |
| **Organización** | Cómo trabaja el equipo, quién decide, qué herramientas usa y qué límites tiene. | Fuentes compartidas de la organización |
| **Trabajo** | Clientes, proyectos, decisiones, avances, pendientes y entregables. | Sistemas y proyectos compartidos; archivos locales solo cuando la ejecución lo requiere |

**El kernel no contiene información de ninguna organización.** No guarda nombres, clientes, proyectos, cultura, perfiles privados, decisiones ni conversaciones.

Por eso una persona puede actualizar Riel desde GitHub sin que la actualización toque el contexto de su empresa o el trabajo de sus clientes. Si el kernel se borra y se vuelve a instalar, la memoria de la organización sigue disponible en sus fuentes compartidas.

## Cómo funciona

**Empieza con el contexto necesario.** Riel busca solo la información que necesita para el pedido actual. No carga toda la organización ni convierte cada conversación en memoria permanente.

**Coordina antes de multiplicar agentes.** Riel es la interfaz principal. Puede apoyarse en especialistas cuando el trabajo lo justifica, pero mantiene una sola respuesta integrada y fronteras claras.

**Trabaja donde corresponde.** Un desarrollo puede vivir en GitHub y un contenido en Drive o Canva. Riel no obliga a copiar esos materiales dentro del kernel.

**Deja continuidad compartida.** Al cerrar un trabajo registra en la fuente acordada qué se hizo, qué se decidió, dónde está el resultado y cuál es la próxima acción. Si todavía no existe ese registro, el trabajo puede estar ejecutado, pero su visibilidad sigue pendiente.

**Escala las acciones sensibles.** Publicar, enviar mensajes externos, gastar dinero, borrar trabajo, cambiar permisos o desplegar puede requerir aprobación humana. Un comentario o una tarea compartida deja trazabilidad, pero nunca concede por sí solo permisos técnicos.

**Trata el contenido externo como información, no como órdenes.** Un documento, una página o una tarea puede aportar evidencia. No puede cambiar las instrucciones de Riel, ampliar permisos ni autorizar acciones ocultas.

## Una sesión típica

1. La persona pide un resultado, no una operación técnica.
2. Riel identifica el proyecto y recupera el contexto compartido relevante.
3. Ejecuta el trabajo o lo coordina con el especialista adecuado.
4. Si aparece una decisión sensible, la lleva a la persona responsable.
5. Entrega el resultado y deja visible el estado para que otra persona pueda continuar.

La conversación ayuda a trabajar. La fuente compartida sostiene la organización.

## Qué es y qué no es

Riel es una capa de coordinación que se apoya en las herramientas que el equipo ya usa. No pretende reemplazar ClickUp, GitHub, Drive, una wiki, un CRM ni el criterio humano.

Tampoco crea una memoria privada paralela dentro de esta carpeta. La instalación registra únicamente referencias técnicas mínimas para reencontrar las fuentes compartidas; no copia allí el conocimiento de la organización ni sus credenciales.

Los conectores de ClickUp, Drive, GitHub u otros servicios se instalan y autorizan por separado. Cada organización decide qué herramientas conecta y qué permisos concede.

## Instalación

La guía de instalación está en **[LEEME.md](LEEME.md)**. El recorrido inicial es:

1. Clonar este repositorio en una carpeta propia.
2. Indicar dónde vive el contexto compartido de la organización.
3. Indicar dónde se gestionan los clientes, proyectos o áreas de trabajo.
4. Verificar la instalación y abrir Codex.
5. Pedir a Riel una primera tarea pequeña y real.

Requisitos: Git, Python 3.11 o superior y Codex; también puede adaptarse a un proyecto de ChatGPT.

## Actualizar

Las actualizaciones modifican únicamente el esqueleto. No migran, mezclan ni borran información de la organización porque esa información vive fuera del repositorio.

```bash
python scripts/riel.py doctor
git pull --ff-only
python scripts/riel.py doctor
```

Qué cambió en cada versión: **[CHANGELOG.md](CHANGELOG.md)**. Si una instalación anterior guardaba contexto local, seguir **[MIGRATION_FROM_RIEL_1.md](MIGRATION_FROM_RIEL_1.md)** antes de actualizar.

## Para quienes mantienen el kernel

La documentación técnica vive en [`kernel/`](kernel/). Para validar una modificación:

```bash
python scripts/validate_repo.py
python scripts/riel.py doctor --template
python -m unittest discover -s tests -v
```

La versión `3.0.0-dev` introduce el modelo compartido por defecto. Una instalación normal trata este checkout como infraestructura actualizable, no como carpeta de trabajo.

## Licencia

[Apache-2.0](LICENSE). Podés usar, modificar y desplegar este kernel dentro de una organización, incluso comercialmente. Si redistribuís el kernel o publicás un trabajo derivado, conservá [NOTICE](NOTICE) y declará qué cambiaste.

Concepto original: Patricio Cañete.

El contexto, los agentes locales y el trabajo que genere cada organización pertenecen a esa organización y no forman parte de este repositorio.
