"""
Orquestador principal de JARVIS.

Filosofía: Gemini piensa, JARVIS ejecuta.
  1. El usuario escribe algo.
  2. Se le manda a Gemini junto con la lista de herramientas disponibles.
  3. Gemini responde con texto normal, O con una petición de function call.
  4. Si pide function call: el orquestador VALIDA y ejecuta la función real,
     y le devuelve el resultado a Gemini para que genere la respuesta final.
     Esto puede encadenarse varias veces antes de la respuesta final.
  5. Todo se loguea en SQLite (tabla `logs`) para poder debuggear después.

Requiere: pip install google-genai (ver requirements.txt)

NOTA: este archivo usa el SDK nuevo `google-genai` (el que reemplaza al
descontinuado `google-generativeai`). Ver docs/FASES.md para el historial
de esta migración.
"""
import os
import time
import subprocess
import threading
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

from src.db import init_db, log_interaccion
from src.tools.registry import FUNCIONES, DECLARACIONES
from src.voz import hablar
from src.escucha import escuchar
from src.wakeword import esperar_wake_word

load_dotenv("config/.env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")


def _asegurar_audio():
    """
    Corre scripts/fix_audio.sh al arrancar, para garantizar que los
    controles de volumen/mute de ALSA estén bien configurados — en este
    hardware específico, algunos no sobreviven confiablemente un reinicio.
    Falla en silencio si el script no está o algo sale mal; no debe
    impedir que JARVIS arranque.
    """
    try:
        subprocess.run(
            ["bash", "scripts/fix_audio.sh"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass  # si falla, seguimos igual; el usuario puede ajustarlo a mano


def construir_system_prompt() -> str:
    """
    Genera el prompt de sistema incluyendo la fecha/hora actual real.

    Esto es importante: sin esto, Gemini no sabe qué día es "hoy" y puede
    asumir un año incorrecto (basado en su fecha de entrenamiento) al
    interpretar fechas relativas como "el 15 de diciembre" o "mañana".
    """
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
    return f"""Eres JARVIS, el asistente personal de Samuel, ejecutándose
en su EliteBook. Eres directo, útil, y usas las herramientas disponibles
cuando corresponde en vez de inventar información. Tienes una herramienta
de búsqueda en internet (buscar_en_internet) para preguntas sobre
información actual, noticias, o cualquier cosa que no sepas con certeza
— úsala en vez de decir que no sabes.

La fecha y hora actual real es: {ahora}. Úsala como referencia para
interpretar cualquier fecha relativa que mencione el usuario (ej. "mañana",
"el próximo viernes", "en dos semanas"). No asumas ningún otro año."""


def construir_tool() -> types.Tool:
    """Convierte nuestro registro de herramientas (dicts) al formato del SDK nuevo."""
    declaraciones = [
        types.FunctionDeclaration(
            name=d["name"],
            description=d["description"],
            parameters_json_schema=d["parameters"],
        )
        for d in DECLARACIONES
    ]
    return types.Tool(function_declarations=declaraciones)


def ejecutar_tool(nombre: str, parametros: dict) -> dict:
    """
    Ejecuta una herramienta por nombre, validando que exista en el registro.
    Este es el punto central de seguridad: nada se ejecuta si no está
    explícitamente registrado en src/tools/registry.py.
    """
    funcion = FUNCIONES.get(nombre)
    if funcion is None:
        return {"ok": False, "error": f"Herramienta desconocida: {nombre}"}
    try:
        return funcion(**parametros)
    except TypeError as e:
        return {"ok": False, "error": f"Parámetros inválidos para {nombre}: {e}"}


def _enviar_con_reintento(chat, mensaje, intentos_maximos=3):
    """
    Envía un mensaje al chat, reintentando automáticamente si Google
    devuelve un error temporal del servidor (500/503 - "alta demanda").
    Esto evita que JARVIS se cierre por completo por un problema pasajero
    que se resuelve solo en unos segundos.
    """
    for intento in range(1, intentos_maximos + 1):
        try:
            return chat.send_message(message=mensaje)
        except ServerError as e:
            if intento == intentos_maximos:
                raise
            espera = 2 * intento  # espera un poco más en cada reintento
            print(f"(⚠️  Servidor de Gemini ocupado, reintentando en {espera}s... [{intento}/{intentos_maximos}])")
            time.sleep(espera)


def procesar_mensaje(chat, mensaje_usuario: str) -> str:
    """
    Procesa un mensaje del usuario, incluyendo el ciclo de function calling.

    IMPORTANTE: Gemini puede encadenar VARIAS llamadas a herramientas antes
    de dar una respuesta final en texto (ej. si la primera falla y necesita
    reintentar con otros parámetros). Por eso este es un LOOP, no una sola
    verificación — se repite hasta que la respuesta sea texto normal.
    """
    respuesta = _enviar_con_reintento(chat, mensaje_usuario)

    MAX_LLAMADAS_ENCADENADAS = 5  # límite de seguridad para evitar loops infinitos
    intentos = 0

    while intentos < MAX_LLAMADAS_ENCADENADAS:
        if not respuesta.function_calls:
            # Ya no hay más llamadas a herramientas, esto es la respuesta final
            if intentos == 0:
                log_interaccion(mensaje_usuario)  # no se usó ninguna herramienta
            return respuesta.text

        function_call = respuesta.function_calls[0]
        nombre_tool = function_call.name
        params = dict(function_call.args)

        resultado = ejecutar_tool(nombre_tool, params)
        log_interaccion(mensaje_usuario, nombre_tool, params, resultado)

        function_response_part = types.Part.from_function_response(
            name=nombre_tool,
            response={"result": resultado},
        )
        respuesta = _enviar_con_reintento(chat, function_response_part)
        intentos += 1

    return "Se alcanzó el límite de intentos encadenados sin obtener una respuesta final. Intenta reformular tu mensaje."


def main():
    if not GEMINI_API_KEY:
        print("ERROR: falta GEMINI_API_KEY en config/.env — copia config/.env.example primero.")
        return

    init_db()
    _asegurar_audio()
    client = genai.Client(api_key=GEMINI_API_KEY)

    config = types.GenerateContentConfig(
        system_instruction=construir_system_prompt(),
        tools=[construir_tool()],
        # Deshabilitado a propósito: queremos ejecutar las herramientas
        # nosotros mismos (vía ejecutar_tool), validándolas contra el
        # registro central, no dejar que el SDK las llame automáticamente.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    chat = client.chats.create(model=GEMINI_MODEL, config=config)

    # Un solo candado compartido entre el hilo de wake word y el hilo
    # principal (teclado), para que nunca intenten usar el micrófono o
    # hablarle a Gemini al mismo tiempo — se turnan.
    audio_lock = threading.Lock()
    # Señal para pausar el wake word mientras el modo "presiona Enter para
    # hablar" usa el micrófono directamente (si no, chocan por el mismo
    # dispositivo de audio exclusivo).
    pausar_wakeword = threading.Event()

    def procesar_y_responder(mensaje: str):
        try:
            respuesta = procesar_mensaje(chat, mensaje)
        except (ServerError, ClientError) as e:
            print(f"JARVIS: Tuve un problema conectándome con Gemini ({e}). Intenta de nuevo en un momento.\n")
            return
        print(f"JARVIS: {respuesta}\n")
        hablar(respuesta)

    def hilo_wake_word(detener: threading.Event):
        """Corre en segundo plano todo el tiempo, escuchando 'hey jarvis'."""
        while not detener.is_set():
            try:
                esperar_wake_word(pausar=pausar_wakeword)
            except Exception as e:
                print(f"(⚠️  Error en detección de wake word: {e})")
                time.sleep(2)  # evita un loop agresivo si el error persiste
                continue

            if detener.is_set():
                break

            with audio_lock:
                print("\n✅ ¡Activado por voz! Di tu mensaje.")
                mensaje = escuchar()
                if not mensaje:
                    continue
                print(f"Tú (voz): {mensaje}")
                procesar_y_responder(mensaje)
            print("Tú: ", end="", flush=True)

    detener_evento = threading.Event()
    hilo = threading.Thread(target=hilo_wake_word, args=(detener_evento,), daemon=True)
    hilo.start()

    print("JARVIS listo. Tienes 3 formas de hablarle:")
    print("  1. Escribe tu mensaje y presiona Enter")
    print("  2. Presiona Enter sin escribir nada, para hablarle una sola vez por voz")
    print("  3. Di 'hey jarvis' en cualquier momento (manos libres, sin tocar nada)")
    print("Escribe 'salir' para terminar.\n")

    try:
        while True:
            entrada = input("Tú: ").strip()
            if entrada.lower() in ("salir", "exit", "quit"):
                break

            with audio_lock:
                if not entrada:
                    # Pausamos el wake word para liberar el micrófono,
                    # esperamos un instante a que realmente lo suelte, y
                    # solo entonces grabamos el comando manual.
                    pausar_wakeword.set()
                    time.sleep(0.5)
                    mensaje = escuchar()
                    pausar_wakeword.clear()

                    if not mensaje:
                        continue
                    print(f"Tú (voz): {mensaje}")
                else:
                    mensaje = entrada

                procesar_y_responder(mensaje)

    except KeyboardInterrupt:
        pass
    finally:
        detener_evento.set()
        print("\nJARVIS apagado.")


if __name__ == "__main__":
    main()
