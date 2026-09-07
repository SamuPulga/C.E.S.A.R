"""
Dashboard web de JARVIS (Fase 10a) — solo lectura.

Muestra en una sola página: estado del sistema, agenda (recordatorios
pendientes), y memoria (datos permanentes guardados). Se ve desde
cualquier navegador en la misma red de Tailscale/LAN, ej.:
    http://100.70.139.115:8080

Decisión de seguridad (ver config/tools_contract.md, sección Fase 9):
no tiene autenticación propia — se apoya en que Tailscale/SSH ya son la
barrera de entrada. Si esto se expusiera a internet público en el
futuro, habría que revisar esta decisión.

Corre con: uvicorn src.web.app:app --host 0.0.0.0 --port 8080
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.db import init_db
from src.tools.sistema import consultar_recursos_sistema, consultar_temperatura, consultar_bateria
from src.tools.recordatorios import listar_recordatorios
from src.tools.memoria import listar_memorias

app = FastAPI()
init_db()


def _fila_recordatorio(r: dict) -> str:
    emoji_prioridad = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(r["prioridad"], "⚪")
    return f"""
    <tr>
        <td>{emoji_prioridad} {r['prioridad']}</td>
        <td>{r['texto']}</td>
        <td>{r['fecha_hora']}</td>
        <td>{r['categoria']}</td>
    </tr>"""


def _fila_memoria(m: dict) -> str:
    return f"""
    <tr>
        <td>{m['clave']}</td>
        <td>{m['valor']}</td>
    </tr>"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    recursos = consultar_recursos_sistema()
    temperatura = consultar_temperatura()
    bateria = consultar_bateria()
    recordatorios = listar_recordatorios(solo_pendientes=True)
    memorias = listar_memorias()

    temp_texto = f"{temperatura['temperatura_celsius']}°C" if temperatura.get("ok") else "N/D"
    bat_texto = (
        f"{bateria['porcentaje']}% ({'⚡ cargando' if bateria['conectado_a_corriente'] else 'batería'})"
        if bateria.get("ok") else "N/D"
    )

    filas_recordatorios = "".join(_fila_recordatorio(r) for r in recordatorios.get("recordatorios", []))
    if not filas_recordatorios:
        filas_recordatorios = "<tr><td colspan='4' class='vacio'>No hay recordatorios pendientes</td></tr>"

    filas_memorias = "".join(_fila_memoria(m) for m in memorias.get("memorias", []))
    if not filas_memorias:
        filas_memorias = "<tr><td colspan='2' class='vacio'>JARVIS no tiene datos guardados todavía</td></tr>"

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="15">
    <title>C.E.S.A.R — Panel de control</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            background:
                radial-gradient(ellipse at center, #0a1620 0%, #030608 100%);
            background-size: 100% 100%, 40px 40px, 40px 40px;
            color: #7fe8ff;
            font-family: 'Share Tech Mono', monospace;
            margin: 0;
            padding: 30px;
            min-height: 100vh;
            background-image:
                radial-gradient(ellipse at center, #0a1620 0%, #030608 100%),
                linear-gradient(#0ff1ff11 1px, transparent 1px),
                linear-gradient(90deg, #0ff1ff11 1px, transparent 1px);
        }}
        h1 {{
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 2.2em;
            color: #00e5ff;
            text-shadow: 0 0 8px #00e5ff, 0 0 20px #00e5ff88, 0 0 40px #00e5ff44;
            letter-spacing: 4px;
            border-bottom: 2px solid #00e5ff55;
            padding-bottom: 14px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }}
        h1 .estado {{
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.35em;
            color: #00ff9d;
            text-shadow: 0 0 8px #00ff9d;
            letter-spacing: 2px;
        }}
        h2 {{
            font-family: 'Orbitron', sans-serif;
            color: #00e5ff;
            text-shadow: 0 0 6px #00e5ff88;
            letter-spacing: 3px;
            font-size: 1.1em;
            margin-top: 40px;
            border-left: 4px solid #00e5ff;
            padding-left: 12px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 18px;
            margin-bottom: 20px;
        }}
        .card {{
            position: relative;
            background: linear-gradient(160deg, #06131a 0%, #030a0e 100%);
            border: 1px solid #00e5ff44;
            padding: 20px 15px;
            text-align: center;
            clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px);
            box-shadow: 0 0 15px #00e5ff22, inset 0 0 20px #00e5ff0d;
        }}
        .card::before, .card::after {{
            content: '';
            position: absolute;
            width: 10px; height: 10px;
            border: 2px solid #00e5ff;
        }}
        .card::before {{ top: -1px; left: -1px; border-right: none; border-bottom: none; }}
        .card::after {{ bottom: -1px; right: -1px; border-left: none; border-top: none; }}
        .card .valor {{
            font-family: 'Orbitron', sans-serif;
            font-size: 2em;
            color: #00e5ff;
            text-shadow: 0 0 10px #00e5ff;
            font-weight: 700;
        }}
        .card .etiqueta {{
            color: #4fd8e8aa;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 6px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #030a0ecc;
            border: 1px solid #00e5ff33;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #00e5ff22;
        }}
        th {{
            background: #00e5ff11;
            color: #00e5ff;
            text-transform: uppercase;
            font-size: 0.78em;
            letter-spacing: 2px;
            font-family: 'Orbitron', sans-serif;
        }}
        td {{ color: #a9eefc; }}
        .vacio {{
            text-align: center;
            color: #4fd8e888;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            color: #4fd8e877;
            font-size: 0.8em;
            text-align: center;
            letter-spacing: 2px;
        }}
        @keyframes parpadeo {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        .punto {{
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #00ff9d;
            box-shadow: 0 0 8px #00ff9d;
            animation: parpadeo 2s infinite;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <h1>C.E.S.A.R<span class="estado"><span class="punto"></span>ONLINE</span></h1>

    <div class="grid">
        <div class="card">
            <div class="valor">{recursos.get('cpu_uso_porcentaje', 'N/D')}%</div>
            <div class="etiqueta">CPU</div>
        </div>
        <div class="card">
            <div class="valor">{recursos.get('ram_uso_porcentaje', 'N/D')}%</div>
            <div class="etiqueta">RAM</div>
        </div>
        <div class="card">
            <div class="valor">{recursos.get('disco_uso_porcentaje', 'N/D')}%</div>
            <div class="etiqueta">Disco</div>
        </div>
        <div class="card">
            <div class="valor">{temp_texto}</div>
            <div class="etiqueta">Temperatura</div>
        </div>
        <div class="card">
            <div class="valor">{bat_texto}</div>
            <div class="etiqueta">Energía</div>
        </div>
    </div>

    <h2>▸ AGENDA — PENDIENTES</h2>
    <table>
        <tr><th>Prioridad</th><th>Recordatorio</th><th>Fecha</th><th>Categoría</th></tr>
        {filas_recordatorios}
    </table>

    <h2>▸ MEMORIA</h2>
    <table>
        <tr><th>Clave</th><th>Valor</th></tr>
        {filas_memorias}
    </table>

    <div class="footer">// ÚLTIMA SINCRONIZACIÓN: {ahora} // REFRESCO AUTOMÁTICO: 15s //</div>
</body>
</html>"""
    return html
