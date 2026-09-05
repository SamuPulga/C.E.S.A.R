# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 6 COMPLETA ✅

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
`consultar_recursos_sistema`, `consultar_temperatura`, `consultar_bateria`.

### ✅ Fase 6 — Internet (VALIDADA EN VIVO)
- [x] `buscar_en_internet` vía Tavily (1,000 búsquedas/mes gratis, sin tarjeta)
- [x] Se descartó la búsqueda de Google integrada de Gemini (`grounding`)
      porque requiere facturación habilitada incluso dentro de su cuota
      "gratuita" — causó un 429 inmediato en el primer intento
- [x] Validado: JARVIS busca en internet para info actual (ej. noticias de
      hoy) pero responde de su propio conocimiento para temas atemporales
      (ej. La Odisea), sin gastar búsquedas innecesarias

### ✅ Deuda técnica — Migración de SDK y seguridad
- Migrado a `google-genai`. Sudo restringido con lista blanca. ntfy topic
  público aceptado como riesgo bajo (decisión consciente).

### 🔲 Pendiente / próxima sesión
- [ ] Fase 7 — Voz (STT/TTS, wake word) — decisión pendiente: local vs nube
- [ ] Considerar caché simple de búsquedas repetidas para cuidar la cuota de Tavily
