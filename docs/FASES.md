# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 4 COMPLETA ✅

### ✅ Fase 0 — Setup e inventario
- [x] Repo de GitHub, contrato de herramientas, VS Code remoto, zona horaria corregida

### ✅ Fase 1 — MVP del orquestador (VALIDADA EN VIVO)
- [x] `consultar_hora`, `crear_recordatorio`, `listar_recordatorios`, `eliminar_recordatorio`
- [x] Acceso remoto por Tailscale, probado desde iPhone

### ✅ Fase 2 — Memoria persistente (VALIDADA EN VIVO)
- [x] `guardar_memoria`, `consultar_memoria`, `listar_memorias`, `olvidar_memoria`

### ✅ Fase 3 — Agenda avanzada (VALIDADA EN VIVO)
- [x] Categorías, prioridades, `modificar_recordatorio`, migración de esquema automática
- [x] Fix: system prompt incluye fecha/hora real (evita años incorrectos en fechas relativas)

### ✅ Fase 4 — Scheduler real de notificaciones (VALIDADA EN VIVO)
- [x] `scripts/scheduler.py` — revisa recordatorios vencidos cada 60s
- [x] Notificaciones push reales al iPhone vía ntfy.sh
- [x] Corriendo como servicio de **systemd** (`jarvis-scheduler.service`):
      arranca solo al encender el EliteBook, se reinicia solo si falla
- [x] Bug resuelto: caracteres especiales (guión largo) en el título HTTP
      hacían que ntfy.sh descartara la notificación silenciosamente —
      ahora el título es ASCII fijo, el detalle va en el cuerpo del mensaje

### ⚠️ Deuda técnica pendiente (no urgente)
- [ ] `google-generativeai` está descontinuado por Google — migrar a `google-genai`
- [ ] Restringir el NOPASSWD de sudo antes de dar a JARVIS herramientas de sistema (Fase 5+)
- [ ] El topic de ntfy.sh es público por nombre — considerar self-host de ntfy
      o autenticación si se vuelve una preocupación real más adelante

### 🔲 Pendiente / próxima sesión
- [ ] Fase 5 — Herramientas de sistema Linux (CPU, RAM, batería, disco)
- [ ] Fase 6 — Internet (búsqueda, APIs externas)
