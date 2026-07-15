# Clasificación de datos

## PUBLIC

Puede publicarse deliberadamente: documentación del kernel, ejemplos anonimizados y materiales aprobados.

## INTERNAL

Información operativa de la organización que no debe publicarse: procesos, notas, decisiones y contexto de equipo.

## CONFIDENTIAL

Información cuyo acceso debe limitarse: datos de clientes, contratos, métricas privadas, correos, credenciales parciales y estrategias no públicas.

## RESTRICTED

Secretos, tokens, contraseñas, datos médicos, financieros identificables, documentos legales sensibles y cualquier dato cuya exposición produzca daño significativo.

## Reglas

- El kernel solo contiene PUBLIC.
- `org/`, `engagements/` y `bus/` pueden contener INTERNAL o CONFIDENTIAL.
- RESTRICTED no se almacena salvo necesidad explícita, autorización y protección adicional.
- Logs guardan hashes y resúmenes mínimos; nunca secretos ni cuerpos completos.
- Promover información a una capa superior requiere revisión humana y minimización.
