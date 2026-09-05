# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 1 COMPLETA ✅

### ✅ Fase 0 — Setup e inventario
- [x] Repo de GitHub creado y estructurado (`SamuPulga/VIS`)
- [x] Contrato de herramientas diseñado (`config/tools_contract.md`)
- [x] Verificación de estado del EliteBook: disco (426GB libres), red, rfkill reinstalado
- [x] VS Code + Remote-SSH configurado para trabajar cómodamente
- [x] Zona horaria corregida: estaba en `Etc/UTC`, ahora en `America/Bogota`

### ✅ Fase 1 — MVP del orquestador (VALIDADA EN VIVO en el EliteBook)
- [x] Esquema de base de datos con WAL mode (`src/db.py`)
- [x] Orquestador con function calling de Gemini (`src/orchestrator.py`, modelo `gemini-3.5-flash`)
- [x] `consultar_hora` — probada ✅
- [x] `crear_recordatorio` — probada ✅ (interpreta lenguaje natural correctamente)
- [x] `listar_recordatorios` — probada ✅
- [x] `eliminar_recordatorio` — probada ✅ (incluso con instrucciones genéricas tipo "cancela todos")
- [x] Logs de interacción guardándose en SQLite (tabla `logs`)

### 🔲 Pendiente / ideas para la próxima sesión
- [ ] Correr `scripts/setup_remote_access.sh` (Tailscale) — para poder seguir trabajando desde la universidad
- [ ] Decidir la siguiente herramienta o funcionalidad a construir (Fase 2)

### 🔲 Fase 2 en adelante
Ver `docs/PROYECTO_ORIGINAL.md` para el detalle completo de fases siguientes
(voz, wake word, scheduler persistente, integración con más herramientas,
seguridad reforzada del `sudo`, etc.)
