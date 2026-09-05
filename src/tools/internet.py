"""
Herramienta de búsqueda en internet (Fase 6), usando Tavily
(https://tavily.com) — una API de búsqueda diseñada para asistentes de IA:
devuelve un resumen ya listo para usar, en vez de solo links crudos.

Riesgo: 🟢 Bajo — es de solo lectura, consulta información pública externa.

Se eligió Tavily en vez de la búsqueda de Google integrada de Gemini
(`grounding`) porque esa última requiere facturación habilitada en el
proyecto de Google Cloud, incluso dentro de su cuota "gratuita". Tavily
ofrece 1,000 búsquedas/mes gratis sin necesitar tarjeta de crédito.
"""
import os
import requests

TAVILY_API_URL = "https://api.tavily.com/search"


def buscar_en_internet(consulta: str) -> dict:
    """
    Busca información actual en internet sobre una consulta.

    Args:
        consulta: la pregunta o tema a buscar, en lenguaje natural

    Returns:
        dict con 'respuesta_resumen' (un resumen generado por Tavily) y
        'fuentes' (lista de títulos y URLs de donde salió la información)
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return {"ok": False, "error": "TAVILY_API_KEY no está configurada en config/.env."}

    if not consulta or len(consulta) > 400:
        return {"ok": False, "error": "La consulta debe tener entre 1 y 400 caracteres."}

    try:
        respuesta = requests.post(
            TAVILY_API_URL,
            json={
                "api_key": api_key,
                "query": consulta,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 5,
            },
            timeout=15,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.RequestException as e:
        return {"ok": False, "error": f"Error al buscar en internet: {e}"}

    return {
        "ok": True,
        "respuesta_resumen": datos.get("answer"),
        "fuentes": [
            {"titulo": r.get("title"), "url": r.get("url")}
            for r in datos.get("results", [])
        ],
    }
