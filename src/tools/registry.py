"""
Registro central de herramientas disponibles para Gemini.

Cada entrada conecta:
  1. El nombre que Gemini usará para llamar a la herramienta
  2. La función Python real que se ejecuta
  3. La declaración en el formato que espera la API de Gemini (function calling)

Ver config/tools_contract.md para el detalle de qué hace cada una y su nivel de riesgo.
"""
from src.tools.basicas import consultar_hora
from src.tools.recordatorios import crear_recordatorio, listar_recordatorios, eliminar_recordatorio

# Mapeo nombre -> función real ejecutable
FUNCIONES = {
    "consultar_hora": consultar_hora,
    "crear_recordatorio": crear_recordatorio,
    "listar_recordatorios": listar_recordatorios,
    "eliminar_recordatorio": eliminar_recordatorio,
}

# Declaraciones en formato Gemini function calling
# (esquema tipo OpenAPI, lo que la API necesita para saber cuándo y cómo llamarlas)
DECLARACIONES = [
    {
        "name": "consultar_hora",
        "description": "Devuelve la fecha y hora actual del sistema.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "crear_recordatorio",
        "description": "Crea un recordatorio para el usuario en una fecha y hora futura.",
        "parameters": {
            "type": "object",
            "properties": {
                "texto": {"type": "string", "description": "Contenido del recordatorio"},
                "fecha_hora": {
                    "type": "string",
                    "description": "Fecha y hora en formato 'YYYY-MM-DD HH:MM'",
                },
            },
            "required": ["texto", "fecha_hora"],
        },
    },
    {
        "name": "listar_recordatorios",
        "description": "Lista los recordatorios guardados del usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "solo_pendientes": {
                    "type": "boolean",
                    "description": "Si es true, solo muestra los que no se han cumplido.",
                },
            },
        },
    },
    {
        "name": "eliminar_recordatorio",
        "description": "Cancela un recordatorio existente por su ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "ID del recordatorio a cancelar"},
            },
            "required": ["id"],
        },
    },
]
