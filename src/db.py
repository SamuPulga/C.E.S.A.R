"""
Capa de acceso a la base de datos de JARVIS.

Usa SQLite con WAL mode activado desde el inicio para soportar
múltiples procesos leyendo/escribiendo sin bloqueos (importante para
cuando el scheduler y el orquestador corran en paralelo, fases futuras).
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = os.environ.get("JARVIS_DB_PATH", "./data/jarvis.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS recordatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    fecha_hora TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente',  -- pendiente | cumplido | cancelado
    creado_en TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    input_usuario TEXT,
    tool_llamada TEXT,
    tool_parametros TEXT,
    tool_resultado TEXT,
    error TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    """
    Abre (o crea) la base de datos con WAL mode activado.
    Llamar a esta función cada vez que se necesite acceso a la DB;
    sqlite3 maneja bien conexiones cortas y frecuentes.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen. Llamar una vez al arrancar JARVIS."""
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def log_interaccion(input_usuario, tool_llamada=None, tool_parametros=None,
                     tool_resultado=None, error=None):
    """Registra cada interacción para poder debuggear qué hizo JARVIS y por qué."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO logs (input_usuario, tool_llamada, tool_parametros, tool_resultado, error)
           VALUES (?, ?, ?, ?, ?)""",
        (input_usuario, tool_llamada, str(tool_parametros), str(tool_resultado), error),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Base de datos inicializada en: {DB_PATH}")
