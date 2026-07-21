# Gobernanza

## Matriz de riesgo

| Nivel | Ejemplos | Conducta |
|---|---|---|
| 0 | lectura, análisis, borrador, edición privada reversible | ejecutar |
| 1 | validación rutinaria, mantenimiento local de bajo impacto | ejecutar y avisar |
| 2 | mensajes externos, publicación, despliegue, borrado, permisos, costos, agentes | esperar aprobación formal |

## Aprobación

La aprobación tiene dos capas que no se sustituyen:

- **Decisión de negocio:** queda en el sistema compartido con identificador, solicitante, autoridad, acción, alcance, riesgo, reversibilidad, vigencia y estado.
- **Autorización técnica:** la conceden el sandbox, la política nativa de aprobación de Codex y los permisos del proveedor externo al momento de ejecutar.

Un registro compartido nunca se transforma en permiso técnico. Riel no genera tokens locales ni permite que un hook eleve permisos. La acción permanece pendiente si falta cualquiera de las capas aplicables o si el alcance no coincide exactamente.

## Decisiones

Registrar en el sistema compartido las decisiones que cambian dirección, alcance, permisos, arquitectura o una recomendación que el humano decide ignorar. No registrar cada preferencia menor ni usar un archivo local como única copia.

## Visibilidad

El cierre de trabajo requiere un registro compartido con resultado, estado, dueño y próxima acción. Si la sincronización no ocurre, el trabajo permanece `visibilidad pendiente` aunque el artefacto local esté terminado.

## Escalación

Escalar cuando la decisión es difícil de revertir, cruza contextos, afecta terceros, expone datos, genera costos o carece de dueño autorizado.
