# Roadmap de fases — C.E.S.A.R (antes JARVIS)

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 10a COMPLETA ✅ — Renombrado a C.E.S.A.R

### ✅ Fases 0-10a: núcleo, memoria, agenda, scheduler, sistema, internet,
### voz, wake word, seguridad, dashboard web
Todas completas y validadas en vivo. 14 herramientas, 3 modos de
interacción, dashboard web holográfico en `http://100.70.139.115:8080`.

### ✅ Renombrado: JARVIS → C.E.S.A.R
- [x] System prompt, mensajes en pantalla, notificaciones push, README,
      y el dashboard web ahora dicen "C.E.S.A.R" (en honor a un profesor
      que Samuel aprecia)
- [x] Fix de pronunciación: "C.E.S.A.R" se leía letra por letra en voz
      alta (como sigla) — se corrigió para que Piper diga "César" natural
- [x] La palabra de activación técnica POR AHORA sigue siendo "hey jarvis"
      (openWakeWord no tiene un modelo pre-entrenado para "Cesar")

### 🔲 Pendiente / próxima sesión
- [ ] **Entrenar wake word personalizado para "Cesar"** — requiere Google
      Colab, generación de audio sintético (TTS variado), y entrenar un
      modelo pequeño con el pipeline de entrenamiento de openWakeWord.
      Es la tarea grande pendiente más importante ahora mismo.
- [ ] Fase 10b — chat también por la web (no solo dashboard de lectura)
- [ ] Caché de búsquedas para cuidar cuota de Tavily
- [ ] Fase 11 (IoT), 12 (Visión), 13 (Sistemas distribuidos) — futuro lejano
