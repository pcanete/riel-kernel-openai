# Riel

Riel ayuda a una organización a trabajar con IA conservando contexto, autoridad y continuidad. El agente principal puede producir y coordinar directamente con skills; no requiere una cadena de coordinadores.

## Tres capas

| Capa | Contenido |
|---|---|
| Kernel | Contrato portable, procedimientos genéricos y adapter del entorno |
| Organización | Identidad, usuarios, autoridad, fuentes, modelos y capacidades privadas |
| Trabajo | Clientes, proyectos, casos o laboratorios; decisiones, pendientes y artefactos |

Una organización nueva recibe el mismo kernel, con otras fuentes y otra identidad. Los usuarios pertenecen a organización; los engagements a trabajo. Las skills son capacidades reutilizables, no una cuarta capa.

## Uso

La persona pide un resultado. El agente recupera contexto suficiente, carga capacidades pertinentes, ejecuta y verifica. Delega solo cuando está autorizado y aporta paralelismo, aislamiento o revisión. Una consulta simple no necesita un workflow de agencia completo.

Cuando el trabajo requiere continuidad y el registro está autorizado, actualiza y lee la fuente compartida. Un link o recibo local no prueba que el resultado quedó visible. Los conectores, permisos y automatizaciones se configuran por separado.

El [contrato común](kernel/coordination.md) se distribuye con ambos adapters. Las cinco skills genéricas están en `.agents/skills`; los métodos privados de una organización y los datos de sus casos nunca se publican con el kernel.

## Instalar y mantener

Ver [LEEME.md](LEEME.md) y [CHANGELOG.md](CHANGELOG.md). No mover ni eliminar datos existentes al actualizar. El modelo se elige en la instalación y puede cambiar sin reescribir las tres capas.

El agente principal ya actúa como Riel. Un perfil con ese nombre es una entrada opcional. Mantener el núcleo común equivalente entre adapters y evaluar con casos reales antes de atribuir mejoras de rendimiento.

## Licencia

[Apache-2.0](LICENSE). Conservar [NOTICE](NOTICE) al redistribuir. Concepto original: Patricio Cañete. La identidad, los agentes privados y el trabajo de cada organización pertenecen a esa organización y quedan fuera de este repositorio.
