"""
Entrada de voz (Fase 7, parte 2) usando faster-whisper para transcripción.

Modo "presiona Enter y habla" (push-to-talk): graba audio del micrófono
con detección automática de silencio (usando `sox`) — deja de grabar solo
cuando dejas de hablar, en vez de una duración fija. Todavía NO hay wake
word pasivo ("Jarvis, ...") — eso queda para una fase futura.

100% local: el modelo de Whisper corre en el CPU del EliteBook, sin
depender de ninguna API externa (solo necesita internet la primera vez,
para descargar los pesos del modelo).
"""
import subprocess
import tempfile
import os
import time

DURACION_MAXIMA_SEGUNDOS = 20  # límite de seguridad si nunca detecta silencio
SILENCIO_UMBRAL = "2%"  # nivel por debajo del cual se considera "silencio" (antes 3%, bajado para captar voz más baja)
SILENCIO_DURACION = "2.0"  # segundos de silencio seguidos para dejar de grabar
MODELO_WHISPER = "large-v3-turbo"  # subido de 'medium' — más preciso, optimizado para velocidad

_modelo = None  # se carga una sola vez (lazy load), porque tarda unos segundos


def _cargar_modelo():
    global _modelo
    if _modelo is None:
        from faster_whisper import WhisperModel
        print("(cargando modelo de voz por primera vez, puede tardar un momento...)")
        _modelo = WhisperModel(MODELO_WHISPER, device="cpu", compute_type="int8", cpu_threads=8)
    return _modelo


def escuchar():
    """
    Graba audio del micrófono hasta detectar silencio, y lo transcribe.

    Devuelve el texto transcrito, o None si algo falla o no se detectó
    nada — un problema de voz nunca debe romper el loop principal, que
    siempre puede seguir funcionando por teclado.
    """
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        print("🎙️  Escuchando... habla ahora (se detiene sola cuando dejes de hablar)")
        resultado = subprocess.run(
            [
                "sox", "-t", "alsa", "plughw:0,6",
                "-c", "1", "-r", "16000", "-b", "16",
                wav_path,
                "silence", "1", "0.1", SILENCIO_UMBRAL,
                "1", SILENCIO_DURACION, SILENCIO_UMBRAL,
                "gain", "-n",  # normaliza el volumen grabado (ayuda si se habla bajo)
            ],
            capture_output=True,
            timeout=DURACION_MAXIMA_SEGUNDOS,
        )
        if resultado.returncode != 0:
            error_real = resultado.stderr.decode(errors="replace").strip()
            print(f"(⚠️  sox falló: {error_real})")
            time.sleep(1)  # pausa defensiva, para no reintentar en loop inmediato
            return None

        modelo = _cargar_modelo()
        segmentos, _ = modelo.transcribe(
            wav_path,
            language="es",
            vad_filter=True,  # filtra silencios/ruido internos, mejora precisión
            beam_size=1,  # bajado de 5 (default) — más rápido, precisión casi igual
            initial_prompt=(
                "Conversación con JARVIS, un asistente personal. Se habla de "
                "recordatorios, categorías como trabajo, universidad y personal, "
                "prioridades baja media y alta, memoria, clima, y consultas generales."
            ),
        )
        texto = " ".join(seg.text for seg in segmentos).strip()

        if not texto:
            print("(no se detectó nada, intenta de nuevo)")
            return None

        return texto

    except subprocess.TimeoutExpired:
        print(f"(se alcanzó el límite de {DURACION_MAXIMA_SEGUNDOS}s sin detectar silencio)")
        return None
    except Exception as e:
        print(f"(⚠️  No se pudo procesar el audio: {e})")
        return None
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
