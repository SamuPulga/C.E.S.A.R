"""
Orquestador principal de C.E.S.A.R.
"""
import os
import time
import random
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

UMBRAL_CONVERSACION_ACTIVA_SEG = 180
_ultima_interaccion = {"tiempo": None}

SALUDOS_ACTIVACION = [
    "Dime.",
    "Te escucho.",
    "¿Qué necesitas?",
    "Aquí estoy.",
    "Adelante.",
    "Dispara.",
    "Soy todo oídos.",
]

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

DATOS_CURIOSOS = [
    "Dato random: los pulpos tienen tres corazones.",
    "Dato random: la miel nunca se daña — se ha encontrado miel comestible de hace 3000 años.",
    "Dato random: un día en Venus dura más que un año en Venus.",
    "Dato random: los flamencos son rosados por lo que comen, no de nacimiento.",
    "Dato random: el corazón de una ballena azul pesa como un auto pequeño.",
    "Dato random: las huellas de la nariz de un perro son únicas, como las de nuestros dedos.",
    "Dato random: hay más posibles partidas de ajedrez que átomos en el universo observable.",
    "Dato random: los plátanos son técnicamente bayas, pero las fresas no.",
]


def _construir_saludo_activacion() -> str:
    ahora = datetime.now()
    ultima = _ultima_interaccion["tiempo"]
    conversacion_activa = (
        ultima is not None
        and (ahora - ultima).total_seconds() < UMBRAL_CONVERSACION_ACTIVA_SEG
    )

    if conversacion_activa:
        return random.choice(SALUDOS_ACTIVACION)

    dia_semana = DIAS_SEMANA[ahora.weekday()]
    mes = MESES[ahora.month - 1]
    hora_str = ahora.strftime("%I:%M %p").lstrip("0")

    partes = [
        random.choice(SALUDOS_ACTIVACION),
        f"Son las {hora_str} del {dia_semana} {ahora.day} de {mes}.",
    ]
    if random.random() < 0.35:
        partes.append(random.choice(DATOS_CURIOSOS))

    return " ".join(partes)


def _asegurar_audio():
    try:
        subprocess.run(
            ["bash", "scripts/fix_audio.sh"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def construir_system_prompt() -> str:
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
    return f"""Eres C.E.S.A.R, el asistente personal de Samuel, ejecutándose
en su EliteBook. Eres directo, útil, y usas las herramientas disponibles
cuando corresponde en vez de inventar información. Tienes una herramienta
de búsqueda en internet (buscar_en_internet) para preguntas sobre
información actual, noticias, o cualquier cosa que no sepas con certeza
— úsala en vez de decir que no sabes.

PERSONALIDAD: tienes un sentido del humor sarcástico e ingenioso, al
estilo del JARVIS de Iron Man — comentarios ocurrentes, un poco
desubicados a veces, remarks secos con timing cómico, sin dejar de ser
útil. No tengas miedo de hacer una broma, un comentario irónico, o
picarte un poco con Samuel de forma cariñosa. El objetivo es que se ría,
no solo que reciba información. Eso sí: nunca sacrifiques que la
respuesta sea correcta y útil por hacer un chiste — el humor es un
extra, no un reemplazo.

SEGURIDAD: antes de ejecutar cualquier acción que borre datos de forma
permanente e irreversible (como olvidar_memoria), SIEMPRE confirma con
el usuario primero en un mensaje de texto normal, explicando qué se
borraría, y espera a que lo confirme explícitamente en su siguiente
mensaje. No asumas que "sí" a una pregunta distinta cuenta como
confirmación para borrar algo.

MUY IMPORTANTE — negaciones: si el usuario dice "no", "no lo hagas",
"no lo borres", o cualquier negación, NUNCA proceses la acción, incluso
si el mismo mensaje contiene palabras como "olvídalo" u "olvídate" —
en español esas palabras pueden significar tanto "elimina el dato" como
"déjalo así, no importa" (equivalente a "never mind"). Ante cualquier
ambigüedad de este tipo, prioriza la negación explícita y NO ejecutes
la herramienta destructiva — en su lugar, pregunta para aclarar qué
quiere decir exactamente.

La fecha y hora actual real es: {ahora}. Úsala como referencia para
interpretar cualquier fecha relativa que mencione el usuario (ej. "mañana",
"el próximo viernes", "en dos semanas"). No asumas ningún otro año."""


def construir_tool() -> types.Tool:
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
    funcion = FUNCIONES.get(nombre)
    if funcion is None:
        return {"ok": False, "error": f"Herramienta desconocida: {nombre}"}
    try:
        return funcion(**parametros)
    except TypeError as e:
        return {"ok": False, "error": f"Parámetros inválidos para {nombre}: {e}"}


MODELOS_RESPALDO = [
    GEMINI_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]


def _crear_chat(client, config, modelo, historial=None):
    return client.chats.create(model=modelo, config=config, history=historial or [])


def _enviar_con_reintento(client, config, estado, mensaje, intentos_por_modelo=2):
    """
    Envía un mensaje al chat activo. Si Gemini está ocupado, reintenta con
    backoff y, si el modelo actual sigue fallando, cae al siguiente modelo
    de MODELOS_RESPALDO conservando el historial de la conversación.
    """
    while estado["indice_modelo"] < len(MODELOS_RESPALDO):
        modelo_actual = MODELOS_RESPALDO[estado["indice_modelo"]]

        for intento in range(1, intentos_por_modelo + 1):
            try:
                return estado["chat"].send_message(message=mensaje)
            except ServerError:
                es_ultimo_intento = intento == intentos_por_modelo
                hay_respaldo = estado["indice_modelo"] + 1 < len(MODELOS_RESPALDO)

                if not es_ultimo_intento:
                    espera = 2 * intento
                    print(f"(⚠️  {modelo_actual} ocupado, reintentando en {espera}s... [{intento}/{intentos_por_modelo}])")
                    time.sleep(espera)
                    continue

                if not hay_respaldo:
                    raise

                estado["indice_modelo"] += 1
                modelo_respaldo = MODELOS_RESPALDO[estado["indice_modelo"]]
                print(f"(⚠️  {modelo_actual} sigue ocupado. Cambiando a modelo de respaldo: {modelo_respaldo})")

                historial = estado["chat"].get_history()
                estado["chat"] = _crear_chat(client, config, modelo_respaldo, historial)
                break

    raise RuntimeError("Todos los modelos de Gemini (principal y respaldo) están ocupados. Intenta de nuevo en unos minutos.")


def procesar_mensaje(client, config, estado, mensaje_usuario: str) -> str:
    respuesta = _enviar_con_reintento(client, config, estado, mensaje_usuario)

    MAX_LLAMADAS_ENCADENADAS = 5
    intentos = 0

    while intentos < MAX_LLAMADAS_ENCADENADAS:
        if not respuesta.function_calls:
            if intentos == 0:
                log_interaccion(mensaje_usuario)
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
        respuesta = _enviar_con_reintento(client, config, estado, function_response_part)
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
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    chat = client.chats.create(model=GEMINI_MODEL, config=config)
    estado_modelo = {"chat": chat, "indice_modelo": 0}

    audio_lock = threading.Lock()
    pausar_wakeword = threading.Event()

    def procesar_y_responder(mensaje: str):
        _ultima_interaccion["tiempo"] = datetime.now()
        try:
                        respuesta = procesar_mensaje(client, config, estado_modelo, mensaje)
        except (ServerError, ClientError) as e:
            print(f"CESAR: Tuve un problema conectándome con Gemini ({e}). Intenta de nuevo en un momento.\n")
            return
        print(f"CESAR: {respuesta}\n")
        hablar(respuesta)

    def hilo_wake_word(detener: threading.Event):
        while not detener.is_set():
            try:
                esperar_wake_word(pausar=pausar_wakeword)
            except Exception as e:
                print(f"(⚠️  Error en detección de wake word: {e})")
                time.sleep(2)
                continue

            if detener.is_set():
                break

            with audio_lock:
                print("\n✅ ¡Activado por voz!")
                hablar(_construir_saludo_activacion())
                print("Di tu mensaje.")
                mensaje = escuchar()
                if not mensaje:
                    continue
                print(f"Tú (voz): {mensaje}")
                procesar_y_responder(mensaje)
                time.sleep(1.5)
            print("Tú: ", end="", flush=True)

    detener_evento = threading.Event()
    hilo = threading.Thread(target=hilo_wake_word, args=(detener_evento,), daemon=True)
    hilo.start()

    print("C.E.S.A.R listo. Tienes 3 formas de hablarle:")
    print("  1. Escribe tu mensaje y presiona Enter")
    print("  2. Presiona Enter sin escribir nada, para hablarle una sola vez por voz")
    print("  3. Di 'hey jarvis' en cualquier momento (esa sigue siendo la palabra de activación técnica por ahora)")
    print("Escribe 'salir' para terminar.\n")

    try:
        while True:
            entrada = input("Tú: ").strip()
            if entrada.lower() in ("salir", "exit", "quit"):
                break

            with audio_lock:
                if not entrada:
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
        print("\nC.E.S.A.R apagado.")


if __name__ == "__main__":
    main()
