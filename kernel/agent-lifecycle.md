# Ciclo de vida de agentes

El kernel publica solamente perfiles genéricos y portables. Los agentes específicos de una organización o cliente pertenecen al entorno privado de esa organización y nunca al checkout actualizable.

El uso de un perfil como método o de un subagente efímero autorizado no crea un rol persistente. La existencia de un especialista no obliga a delegarle.

## Alta

Un agente nuevo requiere propósito concreto, propietario, autoridad, herramientas, clasificación máxima y criterio de retiro. Esa definición se registra en la fuente organizacional compartida; su archivo ejecutable se instala fuera del kernel.

## Operación

- recuperar contexto por adapters y referencias, no por carpetas privadas del kernel;
- limitar permisos y acceso a fuentes;
- publicar resultados y handoffs donde el equipo pueda verlos;
- no conservar memoria paralela local.

## Revisión y retiro

Revisar uso, valor, solapamiento, permisos e incidentes. Al retirar un agente con autorización humana y revisando sus dependencias, revocar las credenciales que corresponda, actualizar el registro compartido y conservar únicamente la evidencia exigida por la política organizacional.

No existe un comando del kernel que cree automáticamente agentes privados dentro de `.codex/agents/`.
