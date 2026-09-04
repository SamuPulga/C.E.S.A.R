# Contrato de herramientas de JARVIS

Este documento define, para cada herramienta que JARVIS puede ejecutar:
qué hace, qué parámetros recibe, qué puede y qué NO puede hacer, y qué
nivel de riesgo tiene. Se define ANTES de implementar cada herramienta.

Regla general: Gemini nunca ejecuta nada directamente. Gemini solo
devuelve "quiero usar la herramienta X con estos parámetros" (function
calling). El orquestador valida los parámetros contra este contrato
antes de ejecutar nada.

## Niveles de riesgo

- 🟢 **Bajo** — solo lee información, no cambia nada. Se ejecuta sin confirmación.
- 🟡 **Medio** — modifica datos propios de JARVIS (ej. recordatorios). Se ejecuta sin confirmación pero queda logueado.
- 🔴 **Alto** — toca el sistema operativo o algo irreversible. Requiere confirmación explícita del usuario o whitelist estricta de comandos permitidos.

---

## Herramientas Fase 1 (MVP)

### `consultar_hora()`
- **Riesgo:** 🟢 Bajo
- **Parámetros:** ninguno
- **Devuelve:** hora y fecha actual del sistema
- **Notas:** primera herramienta a implementar, sirve para validar el loop completo.

### `crear_recordatorio(texto: str, fecha_hora: str)`
- **Riesgo:** 🟡 Medio
- **Parámetros:**
  - `texto` — string, máx 500 caracteres
  - `fecha_hora` — formato ISO 8601 (`YYYY-MM-DD HH:MM`)
- **Valida:** que `fecha_hora` sea una fecha futura válida
- **Devuelve:** ID del recordatorio creado
- **Persistencia:** tabla `recordatorios` en SQLite (ver `db.py`)

### `listar_recordatorios(solo_pendientes: bool = True)`
- **Riesgo:** 🟢 Bajo
- **Parámetros:** `solo_pendientes` — filtra los ya cumplidos
- **Devuelve:** lista de recordatorios

### `eliminar_recordatorio(id: int)`
- **Riesgo:** 🟡 Medio
- **Parámetros:** `id` — debe existir en la tabla
- **Notas:** no borra físicamente, marca `estado = 'cancelado'` (soft delete)

---

## Herramientas futuras (fases posteriores — NO implementar aún)

### `ejecutar_comando_sistema(comando: str)` — Fase 9+
- **Riesgo:** 🔴 Alto
- **Regla:** NUNCA parámetro de texto libre ejecutado directo. Debe
  mapearse a una whitelist fija de comandos predefinidos
  (ej. `reiniciar_wifi`, `revisar_espacio_disco`), nunca shell arbitrario.
- **Pendiente de diseño:** mecanismo de confirmación antes de ejecutar.

### `consultar_clima(ciudad: str)` — Fase futura
- **Riesgo:** 🟢 Bajo
- **Notas:** requiere API externa de clima (por definir cuál)

---

## Registro de decisiones

| Fecha | Decisión |
|---|---|
| Sep 2026 | Se define este contrato antes de escribir código de la Fase 1, para no retrofitear seguridad después. |
| Sep 2026 | `sudo` en el EliteBook tiene NOPASSWD amplio (heredado de HPL) — pendiente restringir a comandos específicos antes de implementar cualquier tool de riesgo 🔴 Alto. |
