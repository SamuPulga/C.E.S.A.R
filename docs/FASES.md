# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 9 COMPLETA ✅ — 14 herramientas, voz con personalidad

### ✅ Fases 0-8: núcleo, memoria, agenda, scheduler, sistema, internet, voz, wake word
Todas completas y validadas en vivo. Ver commits anteriores para detalle
completo. 3 modos de interacción: texto, "presiona Enter para hablar",
y wake word pasivo ("hey jarvis") — los 3 corriendo simultáneamente
gracias a threading con locks para evitar conflictos de audio.

### ✅ Ajustes de calidad de voz/transcripción
- Voz: `es_AR-daniela-high` (femenina, calidad alta)
- Whisper: `large-v3-turbo`, `cpu_threads=10`, `beam_size=1`,
  `temperature=0.0`, `condition_on_previous_text=False`, VAD filter,
  vocabulario de contexto — buen balance precisión/velocidad
- Personalidad: JARVIS ahora es sarcástico y gracioso (system prompt)

### ✅ Fase 9 — Seguridad (VALIDADA EN VIVO)
- [x] `consultar_logs_recientes` — transparencia, JARVIS puede reportar qué ha hecho
- [x] Confirmación obligatoria antes de `olvidar_memoria` (borrado permanente)
- [x] **Fix crítico real**: un bug donde decir "No, no lo borres, olvídalo"
      causaba que JARVIS SÍ borrara el dato (confundido por la palabra
      "olvídalo", ambigua en español). Se corrigió reforzando en el
      system prompt que las negaciones explícitas SIEMPRE ganan sobre
      palabras gatillo ambiguas. Validado en vivo tras el fix.
- [x] Autenticación/autorización: decisión consciente de NO implementar
      (un solo usuario, entrada ya protegida por SSH/Tailscale)
- [x] Control de comandos: ya existía desde el inicio (registro central
      FUNCIONES actúa como whitelist)

### 🔲 Pendiente / próxima sesión
- [ ] Fase 10 — Interfaz web/dashboard
- [ ] Wake word personalizado ("VAL") — requiere entrenar modelo custom
- [ ] Caché de búsquedas para cuidar cuota de Tavily
- [ ] Fase 11 (IoT), 12 (Visión), 13 (Sistemas distribuidos) — futuro lejano
