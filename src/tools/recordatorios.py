"""
Herramientas de recordatorios. Implementa el contrato definido en
config/tools_contract.md — leer ese archivo antes de modificar esto.
"""
from datetime import datetime
from src.db import get_connection


def crear_recordatorio(texto: str, fecha_hora: str) -> dict:
    """
    Crea un recordatorio nuevo.

    Args:
        texto: contenido del recordatorio (máx 500 caracteres)
        fecha_hora: formato ISO 'YYYY-MM-DD HH:MM'

    Returns:
        dict con el resultado, incluyendo 'ok' (bool) y 'id' o 'error'
    """
    if not texto or len(texto) > 500:
        return {"ok": False, "error": "El texto debe tener entre 1 y 500 caracteres."}

    try:
        fecha_parseada = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"ok": False, "error": "Formato de fecha inválido. Usa 'YYYY-MM-DD HH:MM'."}

    if fecha_parseada < datetime.now():
        return {"ok": False, "error": "La fecha debe ser futura."}

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO recordatorios (texto, fecha_hora) VALUES (?, ?)",
        (texto, fecha_hora),
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {"ok": True, "id": nuevo_id}


def listar_recordatorios(solo_pendientes: bool = True) -> dict:
    """Lista los recordatorios guardados."""
    conn = get_connection()
    if solo_pendientes:
        rows = conn.execute(
            "SELECT * FROM recordatorios WHERE estado = 'pendiente' ORDER BY fecha_hora"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM recordatorios ORDER BY fecha_hora").fetchall()
    conn.close()

    return {"ok": True, "recordatorios": [dict(r) for r in rows]}


def eliminar_recordatorio(id: int) -> dict:
    """Cancela (soft delete) un recordatorio por su ID."""
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE recordatorios SET estado = 'cancelado' WHERE id = ? AND estado != 'cancelado'",
        (id,),
    )
    conn.commit()
    afectados = cursor.rowcount
    conn.close()

    if afectados == 0:
        return {"ok": False, "error": f"No se encontró un recordatorio activo con id={id}."}
    return {"ok": True}
