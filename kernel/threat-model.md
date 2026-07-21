# Modelo de amenazas

## Activos

- integridad del kernel público;
- contexto organizacional compartido;
- separación entre organizaciones y clientes;
- autoridad humana y aprobaciones;
- artefactos y evidencia;
- credenciales de adapters y herramientas.

## Amenazas principales

1. **Fuga al repositorio:** datos de una organización terminan versionados con el kernel.
2. **Silo local:** el agente trabaja correctamente pero el resto de la organización no ve decisiones, estado o handoffs.
3. **Cruce de tenant:** una referencia o credencial recupera contexto de otra organización o cliente.
4. **Fuente equivocada:** una copia local o una conversación desplaza un registro compartido más reciente.
5. **Sincronización falsa:** se declara cierre sin comprobar que la actualización compartida exista y sea accesible.
6. **Aprobación forjada:** el mismo actor que ejecuta crea o altera la evidencia de autorización.
7. **Caché convertida en memoria:** datos temporales persisten sin ciclo de vida ni visibilidad.
8. **Hook asumido como frontera total:** un control técnico parcial se interpreta como aislamiento completo.
9. **Inyección desde fuentes compartidas:** un ticket, documento, comentario o artefacto intenta hacerse pasar por instrucción autorizada.
10. **Aprobación local falsificable:** un archivo controlado por el agente se interpreta como permiso para cruzar el sandbox o actuar externamente.

## Controles

- checkout sin raíces privadas y `doctor` que bloquea estructuras heredadas;
- estado técnico fuera del repositorio y enlace ignorado por Git;
- adapters por rol y referencias explícitas a organización y engagement;
- mínimo contexto por demanda y verificación de autoridad;
- cierre condicionado a un registro compartido;
- aprobación de negocio en el sistema compartido y autorización técnica exclusivamente mediante controles nativos de la plataforma;
- separación física de artefactos locales;
- auditoría técnica como complemento, nunca como canon organizacional.
- tratamiento explícito de toda fuente externa como dato no confiable, con procedencia y alcance.

## Riesgo residual

Los hooks y el CLI son guardrails, no una frontera criptográfica completa. La seguridad efectiva depende también del sandbox, permisos del sistema compartido, protección de credenciales y revisión humana.
