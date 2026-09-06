"""
Registro central de herramientas disponibles para Gemini.

Cada entrada conecta:
  1. El nombre que Gemini usará para llamar a la herramienta
  2. La función Python real que se ejecuta
  3. La declaración en el formato que espera la API de Gemini (function calling)

Ver config/tools_contract.md para el detalle de qué hace cada una y su nivel de riesgo.
"""
from src.tools.basicas import consultar_hora
from src.tools.recordatorios import (
    crear_recordatorio, listar_recordatorios, modificar_recordatorio, eliminar_recordatorio
)
from src.tools.memoria import guardar_memoria, consultar_memoria, listar_memorias, olvidar_memoria
from src.tools.sistema import (
    consultar_recursos_sistema, consultar_temperatura, consultar_bateria, consultar_logs_recientes
)
from src.tools.internet import buscar_en_internet

# Mapeo nombre -> función real ejecutable
FUNCIONES = {
    "consultar_hora": consultar_hora,
    "crear_recordatorio": crear_recordatorio,
    "listar_recordatorios": listar_recordatorios,
    "modificar_recordatorio": modificar_recordatorio,
    "eliminar_recordatorio": eliminar_recordatorio,
    "guardar_memoria": guardar_memoria,
    "consultar_memoria": consultar_memoria,
    "listar_memorias": listar_memorias,
    "olvidar_memoria": olvidar_memoria,
    "consultar_recursos_sistema": consultar_recursos_sistema,
    "consultar_temperatura": consultar_temperatura,
    "consultar_bateria": consultar_bateria,
    "consultar_logs_recientes": consultar_logs_recientes,
    "buscar_en_internet": buscar_en_internet,
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
                "categoria": {
                    "type": "string",
                    "description": "Categoría libre, ej. 'trabajo', 'universidad', 'personal'. Si no se especifica, usar 'general'.",
                },
                "prioridad": {
                    "type": "string",
                    "description": "Una de: 'baja', 'media', 'alta'. Si no se especifica, usar 'media'.",
                },
            },
            "required": ["texto", "fecha_hora"],
        },
    },
    {
        "name": "listar_recordatorios",
        "description": "Lista los recordatorios guardados del usuario, con filtros opcionales.",
        "parameters": {
            "type": "object",
            "properties": {
                "solo_pendientes": {
                    "type": "boolean",
                    "description": "Si es true, solo muestra los que no se han cumplido.",
                },
                "categoria": {"type": "string", "description": "Filtrar solo por esta categoría"},
                "prioridad": {"type": "string", "description": "Filtrar solo por esta prioridad"},
            },
        },
    },
    {
        "name": "modificar_recordatorio",
        "description": (
            "Modifica uno o más campos de un recordatorio existente (texto, fecha, "
            "categoría o prioridad). Solo se cambian los campos que se especifiquen."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "ID del recordatorio a modificar"},
                "texto": {"type": "string", "description": "Nuevo texto (opcional)"},
                "fecha_hora": {"type": "string", "description": "Nueva fecha 'YYYY-MM-DD HH:MM' (opcional)"},
                "categoria": {"type": "string", "description": "Nueva categoría (opcional)"},
                "prioridad": {"type": "string", "description": "Nueva prioridad: baja/media/alta (opcional)"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "eliminar_recordatorio",
        "description": (
            "Cancela un recordatorio existente por su ID. IMPORTANTE: confirma "
            "con el usuario cuál recordatorio quiere cancelar (di el texto del "
            "recordatorio en voz alta) ANTES de llamar esta función, para evitar "
            "cancelar el equivocado."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "ID del recordatorio a cancelar"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "guardar_memoria",
        "description": (
            "Guarda o actualiza un dato PERMANENTE sobre el usuario (preferencias, "
            "datos personales, contexto general que no tiene fecha de vencimiento). "
            "No usar para recordatorios con fecha, para eso usar crear_recordatorio."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "clave": {"type": "string", "description": "Identificador corto, ej. 'color_favorito'"},
                "valor": {"type": "string", "description": "El dato a recordar, ej. 'azul'"},
            },
            "required": ["clave", "valor"],
        },
    },
    {
        "name": "consultar_memoria",
        "description": "Recupera un dato permanente específico guardado previamente sobre el usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "clave": {"type": "string", "description": "Identificador del dato a buscar"},
            },
            "required": ["clave"],
        },
    },
    {
        "name": "listar_memorias",
        "description": "Lista todos los datos permanentes que JARVIS sabe sobre el usuario.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "olvidar_memoria",
        "description": (
            "Elimina PERMANENTEMENTE (sin posibilidad de recuperar) un dato "
            "guardado sobre el usuario. IMPORTANTE: esta acción es irreversible "
            "— SIEMPRE pregunta al usuario '¿seguro que quieres que olvide "
            "[dato]? No podré recuperarlo después' y espera su confirmación "
            "explícita en un mensaje aparte ANTES de llamar esta función. "
            "Nunca la llames en el mismo turno en que el usuario lo pidió por "
            "primera vez."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "clave": {"type": "string", "description": "Identificador del dato a olvidar"},
            },
            "required": ["clave"],
        },
    },
    {
        "name": "consultar_recursos_sistema",
        "description": "Devuelve el uso actual de CPU, RAM y disco del EliteBook.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_temperatura",
        "description": "Devuelve la temperatura actual del CPU del EliteBook.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_bateria",
        "description": "Devuelve el porcentaje de batería y si está conectado a corriente.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_logs_recientes",
        "description": (
            "Devuelve las últimas interacciones/acciones que has realizado "
            "(transparencia). Úsala si el usuario pregunta algo como '¿qué has "
            "hecho últimamente?' o '¿qué acciones has tomado hoy?'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cantidad": {
                    "type": "integer",
                    "description": "Cuántas interacciones recientes mostrar (por defecto 10, máximo 50)",
                },
            },
        },
    },
    {
        "name": "buscar_en_internet",
        "description": (
            "Busca información actual en internet (noticias, eventos recientes, "
            "datos que cambian con el tiempo, o cualquier cosa que no sepas con "
            "certeza). Úsala en vez de decir que no tienes la información."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "La pregunta o tema a buscar"},
            },
            "required": ["consulta"],
        },
    },
]
