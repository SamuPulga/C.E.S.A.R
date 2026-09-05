# Roadmap de fases — JARVIS

Documento completo original: `docs/PROYECTO_ORIGINAL.md`.
Este archivo es el resumen vivo de progreso.

## Estado actual: Fase 7 COMPLETA ✅ — JARVIS es 100% manos libres

### ✅ Fases 0-6: núcleo, memoria, agenda, scheduler, sistema, internet
Todas completas y validadas en vivo. 13 herramientas: hora, 4 de
recordatorios, 4 de memoria, 3 de sistema, 1 de búsqueda en internet.

### ✅ Fase 7 — Voz completa (VALIDADA EN VIVO, de punta a punta)

**Parte 1 — Salida de voz (TTS):**
- Piper TTS, 100% local, voz `es_MX-ald-medium`
- Fix de audio: Mic Boost y volúmenes ALSA en 0/muted por defecto,
  corregidos y guardados con `alsactl store`

**Parte 2 — Entrada de voz (STT):**
- faster-whisper (modelo `small`, 100% local, CPU)
- Detección automática de silencio con `sox` (deja de grabar solo)
- Dispositivo correcto: DMIC integrado (`plughw:0,6`), no el genérico

**Parte 3 — Wake word pasivo ("hey jarvis"):**
- openWakeWord, modelo pre-entrenado `hey_jarvis_v0.1`
- Nota técnica importante: Python 3.14 (el que corre el EliteBook) es
  demasiado reciente para la versión moderna de openwakeword (necesita
  tflite-runtime, sin wheels para 3.14 aún) — pip instaló silenciosamente
  la versión vieja 0.4.0, con una API distinta (`wakeword_model_paths`
  en vez de `wakeword_models`, sin `download_models()`)
- Los 3 archivos del modelo (`melspectrogram.onnx`, `embedding_model.onnx`,
  `hey_jarvis_v0.1.onnx`) se descargaron a mano desde los releases de
  GitHub de openWakeWord v0.5.1, directo a la carpeta de recursos del
  paquete instalado (`venv/.../site-packages/openwakeword/resources/models/`)
  — **si se recrea el venv desde cero, hay que repetir esta descarga**:
```bash
  PKG_DIR=$(python3 -c "import openwakeword, os; print(os.path.dirname(openwakeword.__file__))")
  mkdir -p "$PKG_DIR/resources/models" && cd "$PKG_DIR/resources/models"
  curl -LO https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx
  curl -LO https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx
  curl -LO https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_jarvis_v0.1.onnx
```
- Umbral de detección ajustado a 0.3 (el default de 0.5 nunca disparaba
  con la pronunciación real del usuario, aunque el modelo sí reaccionaba)
- Decisión de producto: la palabra de activación quedó en inglés
  ("hey jarvis"), aunque la idea original era una palabra personalizada
  ("VAL") — eso requeriría entrenar un modelo custom (proceso de ML
  aparte, con datos sintéticos y Colab), queda como posible fase futura

**Cambio de arquitectura:** el modo principal de `orchestrator.py` ya NO
usa `input()` de teclado — ahora es un loop continuo: espera wake word →
graba comando → transcribe → procesa → responde en voz. Se perdió la
opción de escribir texto en este modo (trade-off consciente, se puede
recuperar más adelante si hace falta).

### ✅ Robustez — Reintentos ante errores de Gemini
Errores 500/503 ya no cierran el programa — reintenta con espera progresiva.

### 🔲 Pendiente / próxima sesión
- [ ] Considerar recuperar la opción de escribir texto como alternativa al wake word
- [ ] Wake word personalizado ("VAL") — requiere entrenar modelo custom
- [ ] Caché simple de búsquedas repetidas (cuidar cuota de Tavily)
