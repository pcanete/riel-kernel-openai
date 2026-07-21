# Migración a Riel shared-first

Esta migración aplica a instalaciones 1.x y 2.x que guardaban contexto durable bajo `org/`, `engagements/`, `bus/`, `.riel/` o agentes locales dentro del checkout.

## Principio

Primero se publica y verifica el conocimiento en fuentes compartidas; recién después se retira la copia local. La migración nunca borra datos automáticamente.

## Procedimiento

1. Congelá cambios en la instalación anterior y hacé un inventario de organizaciones, usuarios, engagements, decisiones, pendientes, aprobaciones, agentes y artefactos.
2. Elegí las fuentes autorizadas para `organization`, `work`, `knowledge` y `artifacts`, con responsables y permisos claros.
3. Transferí cada dato durable a su registro compartido. Conservá fecha, autoridad, procedencia y referencias a evidencia.
4. Verificá con los usuarios responsables que el contenido sea completo, accesible y utilizable por el resto de la organización.
5. Instalá el kernel nuevo en un checkout limpio y ejecutá `init` con estado técnico fuera de ese checkout.
6. Configurá las fuentes mediante `configure-source` y ejecutá `doctor`.
7. Mové los artefactos locales necesarios a repositorios o directorios de ejecución separados y enlazalos con `link-work`.
8. Tratá cualquier `approvals/` o `active-approval` heredado como inválido: no concede permisos en esta versión. Conservá la decisión de negocio en la fuente compartida y usá la aprobación nativa de Codex para la frontera técnica.
9. Archivá la instalación anterior fuera del checkout actual según la política de retención. No la elimines hasta que un responsable lo apruebe.

## Criterios de salida

- No existen `org/`, `engagements/`, `bus/`, `.riel/` ni agentes específicos de una organización dentro del kernel.
- Las fuentes `organization` y `work` están configuradas y accesibles.
- Cada engagement activo tiene responsable, estado, decisiones, pendientes y próxima acción visibles.
- Los artefactos tienen referencias compartidas y no dependen del checkout para ser encontrados.
- `python scripts/riel.py doctor` termina sin errores.
