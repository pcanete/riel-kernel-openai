# Gobernanza

## Matriz de riesgo

| Nivel | Ejemplos | Conducta |
|---|---|---|
| 0 | lectura, análisis, borrador, edición privada reversible | ejecutar |
| 1 | validación rutinaria, mantenimiento local de bajo impacto | ejecutar y avisar |
| 2 | mensajes externos, publicación, despliegue, borrado, permisos, costos, agentes | esperar aprobación formal |

## Aprobación

Una aprobación contiene:

- identificador;
- solicitante y aprobador;
- acción y alcance;
- patrón técnico de herramienta/comando;
- riesgo y reversibilidad;
- creación, aprobación y vencimiento;
- estado y consumo.

No es válida si falta alguno de los controles verificables, está vencida, fue consumida o la acción no coincide.

## Decisiones

Registrar decisiones que cambian dirección, alcance, permisos, arquitectura o una recomendación que el humano decide ignorar. No registrar cada preferencia menor.

## Escalación

Escalar cuando la decisión es difícil de revertir, cruza contextos, afecta terceros, expone datos, genera costos o carece de dueño autorizado.
