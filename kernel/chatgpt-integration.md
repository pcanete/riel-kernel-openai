# Integración con ChatGPT

ChatGPT Projects permite instrucciones específicas del proyecto y archivos de contexto. Riel usa esa capa como interfaz de conversación, análisis y coordinación.

## División de responsabilidades

- ChatGPT: conversación, síntesis, ideación, investigación y coordinación con conectores disponibles.
- Codex: lectura/escritura del workspace, validación, ejecución, hooks, bus y fuente de verdad local.

## Reglas

- Las instrucciones del Project deben copiarse desde `CHATGPT_PROJECT_INSTRUCTIONS.md`.
- Subir `chatgpt/RIEL_CHATGPT_CONTEXT.md` como base.
- Adjuntar contexto privado solo cuando sea necesario y autorizado.
- Después de trabajar en ChatGPT, devolver un handoff estructurado para que Codex actualice los archivos canónicos.
- Una escritura mediante conector sigue siendo nivel 2 aunque se ejecute desde ChatGPT.
