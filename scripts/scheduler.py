"""
Scheduler de JARVIS (Fase 4).

Proceso INDEPENDIENTE del orquestador interactivo — corre en segundo plano
todo el tiempo, revisando la base de datos cada cierto intervalo para ver
si algún recordatorio ya venció. Si es así, envía una notificación push
real al celular vía ntfy.sh (servicio gratuito, sin necesidad de cuenta).

Se ejecuta como servicio de systemd (ver scripts/jarvis-scheduler.service)
para sobrevivir reinicios del EliteBook, siguiendo el principio de
"persistencia" del proyecto.
"""
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.db import get_connection, init_db

load_dotenv("config/.env")

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
INTERVALO_SEGUNDOS = 60


def enviar_notificacion(titulo: str, mensaje: str, prioridad: str = "media"):
    """Envía una notificación push al celular vía ntfy.sh."""
    if not NTFY_TOPIC:
        print("ADVERTENCIA: NTFY_TOPIC no está configurado en config/.env — no se puede notificar.")
        return

    # ntfy.sh usa prioridades 1-5; mapeamos nuestras 3 a ese rango
    mapa_prioridad = {"baja": "3", "media": "3", "alta": "5"}

    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=mensaje.encode("utf-8"),
            headers={
                # IMPORTANTE: los encabezados HTTP no soportan bien caracteres
                # especiales (acentos, guiones largos, etc.) — por eso el
                # título se mantiene simple/ASCII, y todo el detalle
                # (categoría, texto con acentos) va en el cuerpo del mensaje.
                "Title": "JARVIS",
                "Priority": mapa_prioridad.get(prioridad, "3"),
                "Tags": "robot",
            },
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"[{datetime.now()}] Error enviando notificación: {e}")


def revisar_recordatorios_vencidos() -> int:
    """
    Busca recordatorios pendientes cuya fecha_hora ya pasó, notifica cada
    uno, y los marca como 'cumplido'. Devuelve cuántos se procesaron.
    """
    conn = get_connection()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Comparación como texto funciona porque el formato 'YYYY-MM-DD HH:MM'
    # ordena correctamente de forma lexicográfica (es lo mismo que ISO 8601).
    vencidos = conn.execute(
        "SELECT * FROM recordatorios WHERE estado = 'pendiente' AND fecha_hora <= ?",
        (ahora,),
    ).fetchall()

    for r in vencidos:
        enviar_notificacion(
            titulo="C.E.S.A.R",
            mensaje=f"[{r['categoria']} · {r['prioridad']}] {r['texto']}",
            prioridad=r["prioridad"],
        )
        conn.execute("UPDATE recordatorios SET estado = 'cumplido' WHERE id = ?", (r["id"],))

    conn.commit()
    conn.close()
    return len(vencidos)


def main():
    init_db()
    print(f"Scheduler de JARVIS iniciado. Revisando cada {INTERVALO_SEGUNDOS}s...")
    if not NTFY_TOPIC:
        print("⚠️  NTFY_TOPIC no configurado — las notificaciones no se enviarán hasta configurarlo.")

    while True:
        n = revisar_recordatorios_vencidos()
        if n:
            print(f"[{datetime.now()}] {n} recordatorio(s) vencido(s) notificado(s).")
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    main()
