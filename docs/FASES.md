# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 5 COMPLETA ✅ — Toda la deuda técnica resuelta o aceptada

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

### ✅ Deuda técnica — Migración de SDK
Migrado de `google-generativeai` (descontinuado) a `google-genai`. Validado
en vivo: chat normal + function calling encadenado.

### ✅ Deuda técnica — Seguridad de sudo
- [x] Se quitó la regla amplia `samupulga ALL=(ALL) NOPASSWD:ALL` (heredada del HPL)
- [x] Se instaló `/etc/sudoers.d/jarvis-samupulga` con lista blanca específica:
      systemctl (solo para jarvis-scheduler), apt, rfkill, tailscale,
      timedatectl set-timezone, netplan apply
- [x] Validado: comandos de la lista blanca funcionan sin contraseña;
      cualquier otro comando SÍ pide la contraseña normal del usuario

### ⚪ Riesgo aceptado (decisión consciente, no pendiente)
- El topic de ntfy.sh (`jarvis-samupulga2026`) es público por nombre en el
  servidor gratuito de ntfy.sh. Se decidió mantenerlo así: el nombre es
  suficientemente único, y el riesgo práctico es bajo. Revisar si en algún
  momento se vuelve una preocupación real (self-host de ntfy sería la
  alternativa).

### 🔲 Pendiente / próxima sesión
- [ ] Fase 6 — Internet (búsqueda web, APIs externas, info actual del mundo)
- [ ] Fase 7 — Voz (STT/TTS, wake word) — decisión pendiente: local vs nube
