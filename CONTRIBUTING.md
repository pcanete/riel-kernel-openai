# Contribuir

1. Trabajar en una rama de desarrollo, sin `.riel-instance.json`.
2. Crear una rama.
3. Ejecutar:

   ```bash
   python scripts/validate_repo.py
   python -m unittest discover -s tests -v
   ```

4. No crear ni incluir datos de `org/`, `engagements/`, `bus/`, `.riel/`, `.env` ni agentes `local-*`.
5. Documentar cambios de comportamiento en `CHANGELOG.md`.
6. Mantener compatibilidad con Windows, macOS y Linux cuando sea posible.
7. Una prueba end-to-end debe dejar limpio `git status` y guardar la instancia fuera del checkout.
