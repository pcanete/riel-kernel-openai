# Ciclo de vida de agentes

## Nacimiento

Un agente local requiere necesidad repetida, frontera estable, entrada y salida claras, no duplicación, evaluación de riesgo y aprobación nivel 2.

La implementación vive en `.codex/agents/local-<id>.toml` y se ignora en Git. El registro conceptual vive en `org/context.md`.

## Entrevista mínima

Debe responder:

- para qué existe;
- cuándo debe invocarse;
- qué no hará;
- qué archivos puede leer o escribir;
- cuándo escala;
- cómo se mide su utilidad.

## Evaluación

Revisar después de uso real: calidad, costo, tiempos, escalaciones, fronteras invadidas y trabajo duplicado.

## Retiro

Retirar cuando no se usa, duplica funciones, genera más coordinación que valor o su conocimiento debe convertirse en una skill. Requiere aprobación nivel 2 y registro de la decisión.
