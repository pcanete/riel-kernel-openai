# Arquitectura de tres capas

El [contrato portable](coordination.md) define kernel, organización y trabajo. Los usuarios son parte de organización; los engagements, incluidos laboratorios, son trabajo. Los roles de adapter existentes se conservan sin migrar ni renombrar datos.

| Capa | Qué se configura | Dónde vive |
|---|---|---|
| Kernel | Contrato, skills genéricas, adapters de runtime, herramientas técnicas y pruebas | Checkout público reemplazable |
| Organización | Identidad, usuarios, autoridad, modelos, catálogo de capacidades y fuentes | Fuente `organization`, conocimiento privado y configuración externa |
| Trabajo | Casos, alcance, decisiones, pendientes y resultados | Fuente `work`, repositorios de artefactos y ejecución externa |

`knowledge` es un rol de información de la organización; `artifacts` localiza entregables del trabajo. No son capas adicionales. El estado técnico enlazado por `.riel-instance.json` contiene referencias, rutas y recibos declarativos; no memoria institucional ni autorizaciones.

## Reemplazabilidad

Otra organización recibe el mismo kernel y declara otras fuentes, usuarios, capacidades y responsables. Puede usar una wiki, un repositorio compartido o un gestor distinto. Ningún nombre de cliente, persona, modelo comercial o proveedor es obligatorio.

El contexto se recupera por demanda y se identifica su procedencia. Un conector ausente no se sustituye por memoria de otra instalación. El modelo principal ejecuta con skills; los subagentes son opcionales y su uso no amplía autoridad.

## Fuente del contrato común

`kernel/coordination.md` y las cinco skills `riel-*` de este repositorio son la fuente de mantenimiento del contrato portable. El adapter Claude distribuye copias equivalentes en `docs/coordination.md` y `.claude/skills/`. Comparar ambas distribuciones antes de publicar un cambio común; no requieren consultarse entre sí durante la ejecución. El método privado de una organización no se publica en ninguna de ellas.

Con ambos checkouts disponibles, ejecutar `python scripts/validate_repo.py --peer <checkout-claude>`. Falla si falta o difiere el contrato o alguna skill común; normaliza únicamente los finales de línea al leerlos.

## Compatibilidad

Las antiguas capas 0/1/2/3 se leen como kernel / organización y usuarios / trabajo. No cambiar schemas de instancia ni mover carpetas de clientes por esta aclaración. Las fuentes y artefactos siguen fuera del checkout. El kernel debe poder reinstalarse sin perder continuidad organizacional.
