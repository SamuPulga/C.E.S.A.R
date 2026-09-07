# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 10a COMPLETA ✅ — Dashboard web holográfico

### ✅ Fases 0-9: núcleo, memoria, agenda, scheduler, sistema, internet,
### voz, wake word, seguridad
Todas completas y validadas en vivo. 14 herramientas, 3 modos de
interacción (texto, presiona-Enter, wake word "hey jarvis"),
confirmaciones antes de borrados permanentes, logs de auditoría.

### ✅ Fase 10a — Dashboard web de solo lectura (VALIDADA EN VIVO)
- [x] `src/web/app.py` — FastAPI, una sola página con auto-refresh cada 15s
- [x] Muestra: CPU/RAM/disco/temperatura/batería, agenda pendiente, memoria
- [x] Estética holográfica tipo HUD (cian brillante, esquinas tipo
      interfaz de ciencia ficción, fuente Orbitron) — pedido explícito
      del usuario para que "se sienta vivo"
- [x] Corriendo como servicio systemd (`jarvis-web.service`), puerto 8080
- [x] Accesible desde cualquier dispositivo en la red Tailscale:
      `http://100.70.139.115:8080`
- [x] Sin autenticación propia (decisión de Fase 9: se apoya en que
      Tailscale/SSH ya son la barrera de entrada)

### 🔲 Pendiente / próxima sesión
- [ ] Fase 10b — Chat vía web (opcional, ya existe por voz/texto en terminal)
- [ ] Wake word personalizado ("VAL") — requiere entrenar modelo custom
- [ ] Caché de búsquedas para cuidar cuota de Tavily
- [ ] Fase 11 (IoT), 12 (Visión), 13 (Sistemas distribuidos) — futuro lejano
