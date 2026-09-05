"""
Síntesis de voz (Fase 7, primera parte) usando Piper TTS.

JARVIS convierte sus respuestas de texto a voz y las reproduce por los
parlantes del EliteBook. 100% local: no depende de ninguna API externa,
así que no tiene costo ni límite de uso.

Pendiente para la próxima sesión: entrada de voz (micrófono + wake word).
"""
import subprocess
import tempfile
import os
import re

VOICE_MODEL = "voices/es_MX-ald-medium.onnx"


def _limpiar_para_voz(texto: str) -> str:
    """Quita símbolos de Markdown que sonarían raro leídos en voz alta."""
    texto = re.sub(r"[*_#`]", "", texto)
    texto = re.sub(r"\n+", ". ", texto)
    return texto.strip()


def hablar(texto: str):
    """
    Convierte texto a voz y lo reproduce por los parlantes.

    Si algo falla (Piper no instalado, sin audio, etc.), falla en silencio
    con un aviso en la terminal — un problema de voz nunca debe romper el
    chat de texto, que sigue siendo la forma principal de usar JARVIS.
    """
    if not texto:
        return

    texto_limpio = _limpiar_para_voz(texto)
    if not texto_limpio:
        return

    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        subprocess.run(
            ["piper", "--model", VOICE_MODEL, "--output_file", wav_path],
            input=texto_limpio.encode("utf-8"),
            check=True,
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["aplay", "-q", wav_path],
            check=True,
            capture_output=True,
            timeout=600,  # límite amplio (10 min) — solo para evitar que quede colgado para siempre
        )
    except Exception as e:
        print(f"(⚠️  No se pudo reproducir la voz: {e})")
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
