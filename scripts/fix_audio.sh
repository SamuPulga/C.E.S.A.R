#!/bin/bash
# Asegura que todos los controles de audio necesarios para JARVIS estén
# activos y en buen volumen. Se corre automáticamente al iniciar
# orchestrator.py, porque en este hardware (chip de audio con DSP SOF)
# algunos controles no sobreviven confiablemente un reinicio incluso con
# `alsactl store` (en particular 'Dmic0', descubierto en vivo).
#
# Es idempotente: correrlo varias veces no causa ningún problema.

amixer sset Master 100% unmute > /dev/null 2>&1
amixer sset Speaker 100% unmute > /dev/null 2>&1
amixer sset Headphone 100% unmute > /dev/null 2>&1
amixer sset 'Auto-Mute Mode' Disabled > /dev/null 2>&1
amixer sset Capture 90% cap > /dev/null 2>&1
amixer sset 'Mic Boost' 100% > /dev/null 2>&1
amixer sset 'Dmic0' cap > /dev/null 2>&1

exit 0
