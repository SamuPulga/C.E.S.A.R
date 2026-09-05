# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 5 COMPLETA ✅

### ✅ Fase 0 — Setup e inventario
Repo, contrato de herramientas, VS Code remoto, zona horaria corregida.

### ✅ Fase 1 — MVP del orquestador (VALIDADA EN VIVO)
`consultar_hora`, `crear_recordatorio`, `listar_recordatorios`, `eliminar_recordatorio`.
Acceso remoto por Tailscale, probado desde iPhone.

### ✅ Fase 2 — Memoria persistente (VALIDADA EN VIVO)
`guardar_memoria`, `consultar_memoria`, `listar_memorias`, `olvidar_memoria`.

### ✅ Fase 3 — Agenda avanzada (VALIDADA EN VIVO)
Categorías, prioridades, `modificar_recordatorio`, migración de esquema automática.
Fix: system prompt incluye fecha/hora real.

### ✅ Fase 4 — Scheduler real de notificaciones (VALIDADA EN VIVO)
`scripts/scheduler.py` corriendo como servicio systemd, notificaciones push
reales al iPhone vía ntfy.sh. Fix: manejo robusto de cadenas de function
calling en el orquestador (Gemini puede reintentar antes de responder).

### ✅ Fase 5 — Herramientas de sistema (VALIDADA EN VIVO)
- [x] `consultar_recursos_sistema` — CPU, RAM, disco (vía `psutil`)
- [x] `consultar_temperatura` — sensor coretemp
- [x] `consultar_bateria` — porcentaje y si está conectado a corriente

### ⚠️ Deuda técnica pendiente (no urgente)
- [ ] `google-generativeai` está descontinuado por Google — migrar a `google-genai`
- [ ] Restringir el NOPASSWD de sudo antes de dar a JARVIS herramientas que
      modifiquen el sistema (las actuales de Fase 5 son solo lectura, sin riesgo)
- [ ] El topic de ntfy.sh es público por nombre — considerar self-host o auth

### 🔲 Pendiente / próxima sesión
- [ ] Fase 6 — Internet (búsqueda web, APIs externas, info actual del mundo)
- [ ] Fase 7 — Voz (STT/TTS, wake word) — decisión pendiente: local vs nube
