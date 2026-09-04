# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 0 → Fase 1

### ✅ Hecho (adelantado desde la universidad, sin acceso físico al EliteBook)
- [x] Repo de GitHub creado y estructurado
- [x] Contrato de herramientas diseñado (`config/tools_contract.md`)
- [x] Esquema de base de datos diseñado (`src/db.py`, con WAL mode)
- [x] Esqueleto del orquestador escrito (`src/orchestrator.py`)
- [x] Primeras 4 herramientas implementadas (código, sin probar en el equipo real):
      `consultar_hora`, `crear_recordatorio`, `listar_recordatorios`, `eliminar_recordatorio`
- [x] Script de acceso remoto preparado (`scripts/setup_remote_access.sh`)

### 🔲 Pendiente — próxima vez en casa, frente al EliteBook
- [ ] Correr `scripts/setup_remote_access.sh` (Tailscale)
- [ ] `git clone` del repo en el EliteBook
- [ ] Conseguir la API key de Gemini (si no se hizo antes) y ponerla en `config/.env`
- [ ] Verificación rápida de estado: espacio en disco, red actual, `sudo systemctl status`
- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Primera corrida real de `python3 -m src.orchestrator` — validar el loop completo
- [ ] Confirmar que las 4 herramientas base funcionan de principio a fin

### 🔲 Fase 2 en adelante
Ver `docs/PROYECTO_ORIGINAL.md` para el detalle completo de fases siguientes
(voz, wake word, scheduler persistente, integración con más herramientas,
seguridad reforzada del `sudo`, etc.)
