# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 5 COMPLETA ✅ (+ deuda técnica resuelta)

### ✅ Fase 0 — Setup e inventario
Repo, contrato de herramientas, VS Code remoto, zona horaria corregida.

### ✅ Fase 1 — MVP del orquestador (VALIDADA EN VIVO)
`consultar_hora`, `crear_recordatorio`, `listar_recordatorios`, `eliminar_recordatorio`.
Acceso remoto por Tailscale, probado desde iPhone.

### ✅ Fase 2 — Memoria persistente (VALIDADA EN VIVO)
`guardar_memoria`, `consultar_memoria`, `listar_memorias`, `olvidar_memoria`.

### ✅ Fase 3 — Agenda avanzada (VALIDADA EN VIVO)
Categorías, prioridades, `modificar_recordatorio`, migración de esquema automática.

### ✅ Fase 4 — Scheduler real de notificaciones (VALIDADA EN VIVO)
`scripts/scheduler.py` corriendo como servicio systemd, notificaciones push
reales al iPhone vía ntfy.sh.

### ✅ Fase 5 — Herramientas de sistema (VALIDADA EN VIVO)
`consultar_recursos_sistema`, `consultar_temperatura`, `consultar_bateria` (vía `psutil`).

### ✅ Migración de SDK (deuda técnica resuelta)
- [x] Migrado de `google-generativeai` (descontinuado) a `google-genai`
- [x] Nuevo cliente: `genai.Client()` + `client.chats.create()`
- [x] Function calling manual reescrito con `types.FunctionDeclaration`,
      `types.Tool`, `AutomaticFunctionCallingConfig(disable=True)`
- [x] Validado en vivo: chat normal + function calling encadenado (2 tools
      en un mismo mensaje: hora + batería)

### ⚠️ Deuda técnica restante (no urgente)
- [ ] Restringir el NOPASSWD de sudo antes de dar a JARVIS herramientas que
      modifiquen el sistema (las actuales de Fase 5 son solo lectura, sin riesgo)
- [ ] El topic de ntfy.sh es público por nombre — considerar self-host o auth

### 🔲 Pendiente / próxima sesión
- [ ] Fase 6 — Internet (búsqueda web, APIs externas, info actual del mundo)
- [ ] Fase 7 — Voz (STT/TTS, wake word) — decisión pendiente: local vs nube
