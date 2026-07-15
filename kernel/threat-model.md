# Threat model

## Activos

- datos de organización y clientes;
- decisiones y aprobaciones;
- integridad del kernel;
- credenciales y conectores;
- repositorios y sistemas externos.

## Amenazas y mitigaciones

### Prompt injection

Contenido externo puede pedir ignorar reglas o exfiltrar datos. Mitigación: tratar contenido recuperado como datos, no como autoridad; mínimo privilegio; revisión humana para escrituras.

### Fuga a Git

Datos privados pueden terminar en commits. Mitigación: raíces ignoradas, agentes `local-*`, `doctor` que revisa `git ls-files` y CI sin fixtures privadas.

### Aprobación demasiado amplia

Una autorización genérica puede reutilizarse. Mitigación: patrón específico, vencimiento, activación explícita y consumo de un solo uso.

### Deriva de agentes

Un agente puede expandir su frontera. Mitigación: agentes estrechos, solo lectura por defecto, evaluación y retiro.

### Acciones destructivas

Comandos pueden borrar historial o datos. Mitigación: rules y hook con denegación directa; ramas y copias reversibles.

### Carreras en el bus

Varios agentes pueden escribir simultáneamente. Mitigación: un único escritor lógico, append-only y bloqueo de archivo en la CLI.

### Logs sensibles

La auditoría puede convertirse en otra fuga. Mitigación: hash de entrada, resumen limitado y redacción de patrones de secreto.
