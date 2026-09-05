# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 3 COMPLETA ✅

### ✅ Fase 0 — Setup e inventario
- [x] Repo de GitHub creado y estructurado (`SamuPulga/VIS`)
- [x] Contrato de herramientas diseñado (`config/tools_contract.md`)
- [x] Verificación de estado del EliteBook: disco (426GB libres), red, rfkill reinstalado
- [x] VS Code + Remote-SSH configurado para trabajar cómodamente
- [x] Zona horaria corregida: estaba en `Etc/UTC`, ahora en `America/Bogota`

### ✅ Fase 1 — MVP del orquestador (VALIDADA EN VIVO)
- [x] Esquema de base de datos con WAL mode (`src/db.py`)
- [x] Orquestador con function calling de Gemini
- [x] `consultar_hora`, `crear_recordatorio`, `listar_recordatorios`, `eliminar_recordatorio`
- [x] Acceso remoto por Tailscale, probado desde iPhone

### ✅ Fase 2 — Memoria persistente (VALIDADA EN VIVO)
- [x] `guardar_memoria`, `consultar_memoria`, `listar_memorias`, `olvidar_memoria`
- [x] Confirmado que persiste entre reinicios del programa

### ✅ Fase 3 — Agenda avanzada (VALIDADA EN VIVO)
- [x] Recordatorios con `categoria` y `prioridad` (baja/media/alta)
- [x] `modificar_recordatorio` — actualiza campos parciales
- [x] `listar_recordatorios` con filtros por categoría/prioridad
- [x] Migración de esquema automática (columnas nuevas sin romper datos viejos)
- [x] Fix importante: system prompt ahora incluye la fecha/hora real, para
      que Gemini no asuma un año incorrecto al interpretar fechas relativas

### ⚠️ Deuda técnica pendiente (no urgente)
- [ ] `google-generativeai` está descontinuado por Google — migrar a `google-genai`
      antes de construir mucho más encima (no rompe nada por ahora)
- [ ] Restringir el NOPASSWD de sudo antes de dar a JARVIS herramientas de sistema (Fase 5+)

### 🔲 Pendiente / próxima sesión
- [ ] Fase 4 — Scheduler real (que los recordatorios avisen de verdad, no solo se guarden)
- [ ] Fase 5 — Herramientas de sistema Linux (CPU, RAM, batería, disco)
