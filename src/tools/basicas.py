"""Herramientas triviales, usadas para validar el loop completo end-to-end."""
from datetime import datetime


def consultar_hora() -> dict:
    """Devuelve la fecha y hora actual del sistema."""
    ahora = datetime.now()
    return {
        "ok": True,
        "fecha_hora": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "dia_semana": ahora.strftime("%A"),
    }
