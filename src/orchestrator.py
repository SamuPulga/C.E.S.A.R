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
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.db import init_db, log_interaccion
from src.tools.registry import FUNCIONES, DECLARACIONES

load_dotenv("config/.env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")


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
cuando corresponde en vez de inventar información. Si no tienes una
herramienta para algo, dilo claramente en vez de simular que lo hiciste.

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


def procesar_mensaje(chat, mensaje_usuario: str) -> str:
    """
    Procesa un mensaje del usuario, incluyendo el ciclo de function calling.

    IMPORTANTE: Gemini puede encadenar VARIAS llamadas a herramientas antes
    de dar una respuesta final en texto (ej. si la primera falla y necesita
    reintentar con otros parámetros). Por eso este es un LOOP, no una sola
    verificación — se repite hasta que la respuesta sea texto normal.
    """
    respuesta = chat.send_message(message=mensaje_usuario)

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
        respuesta = chat.send_message(message=function_response_part)
        intentos += 1

    return "Se alcanzó el límite de intentos encadenados sin obtener una respuesta final. Intenta reformular tu mensaje."


def main():
    if not GEMINI_API_KEY:
        print("ERROR: falta GEMINI_API_KEY en config/.env — copia config/.env.example primero.")
        return

    init_db()
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

    print("JARVIS listo. Escribe 'salir' para terminar.\n")
    while True:
        mensaje = input("Tú: ").strip()
        if mensaje.lower() in ("salir", "exit", "quit"):
            break
        if not mensaje:
            continue

        respuesta = procesar_mensaje(chat, mensaje)
        print(f"JARVIS: {respuesta}\n")


if __name__ == "__main__":
    main()
