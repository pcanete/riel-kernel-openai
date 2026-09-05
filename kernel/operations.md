# Operaciones técnicas del adapter Codex

Leer solo si hace falta configurar la instancia o conservar un recibo. Son referencias técnicas, no permisos. Consultar `python scripts/riel.py --help` para opciones.

## Onboarding autorizado

`init --organization-ref <ref> --owner-ref <ref>` enlaza estado externo. `configure-source --role organization|work --provider <proveedor> --locator <ref> --mode read|read-write` configura cada fuente. `doctor` comprueba estructura y referencias; después hacer una lectura real con el conector para comprobar acceso.

No cambiar permisos para ejecutar estos comandos. Si el runtime requiere intervención técnica humana, preparar el comando y explicar la restricción concreta. Ningún archivo local concede autorización.

## Ejecución

`link-work --engagement-ref <ref> --shared-record <ref> --work-dir <ruta> [--artifact-ref <ref>]` vincula un directorio autorizado fuera del kernel. Solo se necesita si el workflow utiliza el enlace técnico.

## Recibo de cierre

Después del cierre verificado por el agente, puede ejecutarse `session-close --engagement-ref <ref> --shared-record <ref> --confirmed-by <ref>`. Por compatibilidad, `confirmed_by` conserva su nombre: es una identidad declarada por quien llama, no autenticación.

La CLI no accede al sistema compartido. Sus recibos nuevos indican `visibility_status: not_verified_by_cli`; ni la referencia ni el nombre del usuario certifican lectura, actualización, acceso de terceros o permisos. El recibo es opcional y no es requisito para terminar una consulta.

Los recibos 1.0 anteriores se conservan y tampoco deben interpretarse como evidencia de acceso. No hay que reescribirlos para migrar.
