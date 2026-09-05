"""
Herramientas de recordatorios/agenda. Implementa el contrato definido en
config/tools_contract.md — leer ese archivo antes de modificar esto.
"""
from datetime import datetime
from src.db import get_connection

PRIORIDADES_VALIDAS = {"baja", "media", "alta"}


def crear_recordatorio(texto: str, fecha_hora: str, categoria: str = "general",
                        prioridad: str = "media") -> dict:
    """
    Crea un recordatorio nuevo.

    Args:
        texto: contenido del recordatorio (máx 500 caracteres)
        fecha_hora: formato ISO 'YYYY-MM-DD HH:MM'
        categoria: etiqueta libre, ej. 'trabajo', 'universidad', 'personal'
        prioridad: 'baja', 'media' o 'alta'

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

    prioridad = prioridad.lower().strip()
    if prioridad not in PRIORIDADES_VALIDAS:
        return {"ok": False, "error": f"Prioridad inválida. Usa una de: {PRIORIDADES_VALIDAS}."}

    categoria = categoria.lower().strip() or "general"

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO recordatorios (texto, fecha_hora, categoria, prioridad) VALUES (?, ?, ?, ?)",
        (texto, fecha_hora, categoria, prioridad),
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {"ok": True, "id": nuevo_id}


def listar_recordatorios(solo_pendientes: bool = True, categoria: str = None,
                          prioridad: str = None) -> dict:
    """Lista los recordatorios guardados, con filtros opcionales."""
    condiciones = []
    valores = []

    if solo_pendientes:
        condiciones.append("estado = 'pendiente'")
    if categoria:
        condiciones.append("categoria = ?")
        valores.append(categoria.lower().strip())
    if prioridad:
        condiciones.append("prioridad = ?")
        valores.append(prioridad.lower().strip())

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    conn = get_connection()
    rows = conn.execute(
        f"SELECT * FROM recordatorios {where} ORDER BY fecha_hora", valores
    ).fetchall()
    conn.close()

    return {"ok": True, "recordatorios": [dict(r) for r in rows]}


def modificar_recordatorio(id: int, texto: str = None, fecha_hora: str = None,
                            categoria: str = None, prioridad: str = None) -> dict:
    """
    Modifica uno o varios campos de un recordatorio existente.
    Solo se actualizan los campos que se pasen (no None).
    """
    campos = {}

    if texto is not None:
        if not texto or len(texto) > 500:
            return {"ok": False, "error": "El texto debe tener entre 1 y 500 caracteres."}
        campos["texto"] = texto

    if fecha_hora is not None:
        try:
            datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
        except ValueError:
            return {"ok": False, "error": "Formato de fecha inválido. Usa 'YYYY-MM-DD HH:MM'."}
        campos["fecha_hora"] = fecha_hora

    if categoria is not None:
        campos["categoria"] = categoria.lower().strip() or "general"

    if prioridad is not None:
        prioridad = prioridad.lower().strip()
        if prioridad not in PRIORIDADES_VALIDAS:
            return {"ok": False, "error": f"Prioridad inválida. Usa una de: {PRIORIDADES_VALIDAS}."}
        campos["prioridad"] = prioridad

    if not campos:
        return {"ok": False, "error": "No se especificó ningún campo para modificar."}

    set_clause = ", ".join(f"{campo} = ?" for campo in campos)
    valores = list(campos.values()) + [id]

    conn = get_connection()
    cursor = conn.execute(
        f"UPDATE recordatorios SET {set_clause} WHERE id = ? AND estado != 'cancelado'",
        valores,
    )
    conn.commit()
    afectados = cursor.rowcount
    conn.close()

    if afectados == 0:
        return {"ok": False, "error": f"No se encontró un recordatorio activo con id={id}."}
    return {"ok": True}


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
