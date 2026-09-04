# JARVIS — Asistente personal en EliteBook

Asistente personal ejecutándose de forma nativa en un HP EliteBook 630 13" G9
("elitebook1samuel1hpl"), corriendo Ubuntu Server 24.04 LTS headless.

## Filosofía

- **Gemini piensa, JARVIS ejecuta.** El modelo (Gemini, vía API) decide qué
  herramienta usar y con qué parámetros. El orquestador en Python ejecuta
  esa herramienta y devuelve el resultado. Gemini nunca ejecuta código
  directamente.
- **Un paso a la vez.** El proyecto avanza por fases (ver `docs/FASES.md`),
  sin saltar pasos ni asumir capacidades del equipo sin comprobarlas.
- **Persistencia real.** Todo estado importante (recordatorios, config,
  logs) vive en SQLite, no en memoria de un proceso que puede reiniciarse.
- **Seguridad por diseño.** Cada herramienta tiene un contrato explícito
  (ver `config/tools_contract.md`) definido ANTES de implementarla.

## Hardware / entorno

Ver `docs/ESTADO_ELITEBOOK.md` para el inventario completo del equipo
(hardware, red, software instalado, lecciones del proyecto HPL previo).

## Estructura del repo

```
jarvis/
├── config/
│   └── tools_contract.md    # Contrato de cada herramienta que JARVIS puede usar
├── src/
│   ├── orchestrator.py      # Loop principal: recibe input -> llama a Gemini -> ejecuta tool
│   ├── db.py                # Capa de acceso a SQLite (WAL mode)
│   └── tools/                # Una función por herramienta disponible
├── docs/
│   ├── FASES.md              # Roadmap completo del proyecto
│   └── ESTADO_ELITEBOOK.md   # Inventario de hardware/software del equipo
├── scripts/
│   └── setup_remote_access.sh # Instalación de Tailscale (acceso remoto)
└── data/                      # jarvis.db vive aquí (NO se sube a git)
```

## Estado actual

🟡 Fase 0 en progreso — repo creado, contrato de herramientas en diseño.

## Setup rápido (cuando estés en el EliteBook)

```bash
git clone <url-de-tu-repo> ~/jarvis
cd ~/jarvis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config/.env.example config/.env   # y pega ahí tu GEMINI_API_KEY
```
