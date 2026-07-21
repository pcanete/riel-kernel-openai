# Riel Kernel para Codex y ChatGPT

Riel es un kernel local de coordinación y gobernanza para trabajo asistido por agentes. Convierte instrucciones conceptuales en una arquitectura verificable basada en archivos, permisos, hooks, aprobaciones consumibles, registros append-only, skills y subagentes acotados.

Esta edición está diseñada para:

- **Codex local/desktop/IDE:** opera sobre el workspace con `AGENTS.md`, permisos, hooks, rules, skills y agentes personalizados.
- **ChatGPT Projects/Work:** usa instrucciones equivalentes y un paquete de contexto portable, sin convertir la conversación en fuente de verdad.

## Qué resuelve

- separa kernel público de datos privados;
- evita que agentes locales o datos de clientes entren a Git;
- formaliza aprobaciones para acciones externas;
- unifica clientes, proyectos y casos bajo `engagements/`;
- valida el bus y la estructura mediante una CLI;
- crea agentes tarde, solo cuando aparece una función repetitiva;
- conserva trazabilidad entre sesiones.

## Inicio rápido

```bash
git clone https://github.com/pcanete/riel-kernel-openai riel
cd riel
python scripts/riel.py init --org-name "Mi organización" --owner "Nombre"
python scripts/riel.py doctor
codex
```

En Codex, revisar y confiar los hooks del repositorio con `/hooks` antes del primer uso.

Para una carpeta existente, no mezclar con `git checkout`. Usar el instalador con detección de colisiones:

```bash
python scripts/installer.py --target /ruta/al/workspace
```

## Estructura

```text
AGENTS.md                     identidad y reglas de arranque
.codex/                       configuración, hooks, rules y subagentes
.agents/skills/               workflows cargados bajo demanda
kernel/                       constitución, seguridad y contratos
scripts/riel.py               CLI operativa
org/                          contexto privado de la organización (ignorado)
engagements/                  trabajo privado por unidad (ignorado)
bus/                          eventos, colas y aprobaciones (ignorado)
.riel/                        estado local de la instancia (ignorado)
```

## Modos

- **Modo desarrollo:** no existe `.riel/instance.json`; el kernel puede editarse y probarse.
- **Modo instancia:** `riel init` crea `.riel/instance.json`; los hooks protegen los archivos del kernel y habilitan únicamente las áreas privadas.
- **Modo mantenimiento:** para editar deliberadamente el kernel de una instancia, iniciar Codex con `RIEL_MAINTENANCE=1` y revisar cada cambio.

## ChatGPT

Copiar `CHATGPT_PROJECT_INSTRUCTIONS.md` en las instrucciones de un Project y subir `chatgpt/RIEL_CHATGPT_CONTEXT.md`. El proyecto de ChatGPT coordina y razona; Codex mantiene la fuente de verdad local y aplica los guardrails técnicos.

## Migración desde Riel 1.x

Seguir `MIGRATION_FROM_RIEL_1.md`. La migración es deliberadamente a un repositorio nuevo para no mezclar contratos antiguos, datos privados e historial del kernel.

## Estado

Versión 2.0.1. Requiere Python 3.11 o superior. No necesita dependencias de ejecución externas.

## Licencia

Apache-2.0. Concepto original: Patricio Cañete.
