"""
Herramientas de sistema (Fase 5). Todas son de solo lectura (riesgo 🟢 Bajo)
— consultan el estado del EliteBook, nunca lo modifican.
"""
import psutil


def consultar_recursos_sistema() -> dict:
    """Devuelve el uso actual de CPU, RAM y disco del EliteBook."""
    cpu_porcentaje = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disco = psutil.disk_usage("/")

    return {
        "ok": True,
        "cpu_uso_porcentaje": cpu_porcentaje,
        "ram_total_gb": round(ram.total / (1024**3), 1),
        "ram_usada_gb": round(ram.used / (1024**3), 1),
        "ram_uso_porcentaje": ram.percent,
        "disco_total_gb": round(disco.total / (1024**3), 1),
        "disco_usado_gb": round(disco.used / (1024**3), 1),
        "disco_uso_porcentaje": disco.percent,
    }


def consultar_temperatura() -> dict:
    """Devuelve la temperatura actual del CPU, si el sensor está disponible."""
    try:
        sensores = psutil.sensors_temperatures()
    except AttributeError:
        return {"ok": False, "error": "psutil no soporta sensores de temperatura en este sistema."}

    if not sensores:
        return {"ok": False, "error": "No se encontraron sensores de temperatura (revisar lm-sensors)."}

    # Tomamos el primer sensor disponible (normalmente 'coretemp' en Intel)
    nombre_sensor = next(iter(sensores))
    lecturas = sensores[nombre_sensor]
    if not lecturas:
        return {"ok": False, "error": "El sensor no devolvió lecturas."}

    return {
        "ok": True,
        "sensor": nombre_sensor,
        "temperatura_celsius": lecturas[0].current,
    }


def consultar_bateria() -> dict:
    """Devuelve el estado de la batería, si el equipo tiene una."""
    bateria = psutil.sensors_battery()
    if bateria is None:
        return {"ok": False, "error": "Este equipo no reporta información de batería (puede estar siempre conectado a corriente, o no tener sensor)."}

    return {
        "ok": True,
        "porcentaje": bateria.percent,
        "conectado_a_corriente": bateria.power_plugged,
        "tiempo_restante_segundos": bateria.secsleft if bateria.secsleft != psutil.POWER_TIME_UNLIMITED else None,
    }


def consultar_logs_recientes(cantidad: int = 10) -> dict:
    """
    Devuelve las últimas interacciones registradas (transparencia/auditoría).
    Útil para preguntas como "¿qué has hecho últimamente?".
    """
    from src.db import get_connection

    cantidad = max(1, min(cantidad, 50))  # límite razonable, entre 1 y 50

    conn = get_connection()
    rows = conn.execute(
        "SELECT timestamp, input_usuario, tool_llamada, tool_resultado, error "
        "FROM logs ORDER BY id DESC LIMIT ?",
        (cantidad,),
    ).fetchall()
    conn.close()

    return {"ok": True, "logs": [dict(r) for r in rows]}
