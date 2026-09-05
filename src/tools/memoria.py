"""
Herramientas de memoria persistente (Fase 2).

Diferencia clave con recordatorios: esto NO tiene fecha de vencimiento.
Es información permanente sobre Samuel que JARVIS puede consultar en
cualquier momento (preferencias, datos personales, contexto general).
"""
from src.db import get_connection


def guardar_memoria(clave: str, valor: str) -> dict:
    """
    Guarda o actualiza un dato permanente sobre el usuario.

    Args:
        clave: identificador corto del dato, ej. 'color_favorito'
        valor: el contenido a recordar, ej. 'azul'

    Si la clave ya existe, se actualiza (no se duplica).
    """
    if not clave or len(clave) > 100:
        return {"ok": False, "error": "La clave debe tener entre 1 y 100 caracteres."}
    if not valor or len(valor) > 1000:
        return {"ok": False, "error": "El valor debe tener entre 1 y 1000 caracteres."}

    clave = clave.strip().lower().replace(" ", "_")

    conn = get_connection()
    conn.execute(
        """INSERT INTO memorias (clave, valor) VALUES (?, ?)
           ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor,
                                             actualizado_en = datetime('now')""",
        (clave, valor),
    )
    conn.commit()
    conn.close()

    return {"ok": True, "clave": clave}


def consultar_memoria(clave: str) -> dict:
    """Recupera un dato específico guardado previamente."""
    clave = clave.strip().lower().replace(" ", "_")
    conn = get_connection()
    row = conn.execute("SELECT * FROM memorias WHERE clave = ?", (clave,)).fetchone()
    conn.close()

    if row is None:
        return {"ok": False, "error": f"No hay ningún dato guardado con la clave '{clave}'."}
    return {"ok": True, "clave": row["clave"], "valor": row["valor"]}


def listar_memorias() -> dict:
    """Lista todos los datos permanentes guardados sobre el usuario."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM memorias ORDER BY clave").fetchall()
    conn.close()
    return {"ok": True, "memorias": [dict(r) for r in rows]}


def olvidar_memoria(clave: str) -> dict:
    """Elimina permanentemente un dato guardado (borrado real, no soft delete)."""
    clave = clave.strip().lower().replace(" ", "_")
    conn = get_connection()
    cursor = conn.execute("DELETE FROM memorias WHERE clave = ?", (clave,))
    conn.commit()
    afectados = cursor.rowcount
    conn.close()

    if afectados == 0:
        return {"ok": False, "error": f"No se encontró ningún dato con la clave '{clave}'."}
    return {"ok": True}
