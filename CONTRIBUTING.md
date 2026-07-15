# Contribuir

1. Trabajar en modo desarrollo, sin `.riel/instance.json`.
2. Crear una rama.
3. Ejecutar:

   ```bash
   python scripts/validate_repo.py
   python -m unittest discover -s tests -v
   ```

4. No incluir datos de `org/`, `engagements/`, `bus/`, `.riel/`, `.env` ni agentes `local-*`.
5. Documentar cambios de comportamiento en `CHANGELOG.md`.
6. Mantener compatibilidad con Windows, macOS y Linux cuando sea posible.
