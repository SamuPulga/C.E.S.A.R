"""
Detección pasiva de wake word ("hey jarvis") - Fase 7, parte 3.

Corre en un loop bloqueante escuchando el micrófono todo el tiempo hasta
detectar la palabra de activación. Cuando la detecta, cierra su propia
captura de audio (para no chocar con la grabación del comando que viene
después, ya que el hardware no soporta dos capturas simultáneas del mismo
dispositivo) y devuelve el control a quien la llamó.

IMPORTANTE - requisito de instalación no automatizado: openwakeword en su
versión actual (0.4.0, la única compatible con Python 3.14 por ahora) no
trae el método download_models(), así que estos 3 archivos se descargaron
a mano dentro del propio paquete instalado:
  <venv>/lib/python3.14/site-packages/openwakeword/resources/models/
    - melspectrogram.onnx
    - embedding_model.onnx
    - hey_jarvis_v0.1.onnx
Si se reinstala el entorno virtual desde cero, hay que repetir esa descarga
(ver docs/FASES.md para los comandos exactos).
"""
import os
import numpy as np
import alsaaudio
import openwakeword
import time
import threading
from openwakeword.model import Model

PKG_DIR = os.path.dirname(openwakeword.__file__)
MODELO_PATH = os.path.join(PKG_DIR, "resources", "models", "hey_jarvis_v0.1.onnx")
UMBRAL = 0.3
SAMPLE_RATE = 16000
CHUNK = 1280  # 80 ms a 16kHz

_modelo = None


def _cargar_modelo():
    global _modelo
    if _modelo is None:
        _modelo = Model(wakeword_model_paths=[MODELO_PATH])
    return _modelo


def esperar_wake_word(pausar: threading.Event = None):
    """
    Bloquea hasta detectar "hey jarvis". Abre y cierra su propia captura
    de audio, para dejar el micrófono libre mientras se graba el comando
    después (usando `sox` desde src/escucha.py).

    Si se pasa un `pausar` (threading.Event) y se activa desde afuera,
    suelta el micrófono y espera hasta que se desactive de nuevo — esto
    permite que otro modo (ej. "presiona Enter para hablar") use el
    micrófono sin chocar con esta escucha continua en segundo plano.
    """
    modelo = _cargar_modelo()
    captura = None

    try:
        while True:
            if pausar is not None and pausar.is_set():
                if captura is not None:
                    captura.close()
                    captura = None
                    time.sleep(0.3)
                time.sleep(0.1)
                continue

            if captura is None:
                captura = alsaaudio.PCM(
                    alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device="plughw:0,6"
                )
                captura.setchannels(1)
                captura.setrate(SAMPLE_RATE)
                captura.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                captura.setperiodsize(CHUNK)

            longitud, datos = captura.read()
            if longitud <= 0:
                continue

            audio = np.frombuffer(datos, dtype=np.int16)
            if len(audio) != CHUNK:
                continue

            prediccion = modelo.predict(audio)
            if prediccion.get("hey_jarvis_v0.1", 0) > UMBRAL:
                return
    finally:
        if captura is not None:
            captura.close()
            # Pausa breve para que el driver de audio (chip con DSP tipo SOF)
            # libere de verdad el dispositivo antes de que otro proceso (sox)
            # intente abrirlo.
            time.sleep(0.3)
