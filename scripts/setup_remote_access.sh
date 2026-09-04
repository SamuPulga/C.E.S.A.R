#!/bin/bash
# Configura acceso remoto al EliteBook vía Tailscale (VPN mesh).
# Correr esto UNA VEZ, físicamente en el EliteBook, conectado a la red de casa.
#
# Qué hace:
#   1. Instala Tailscale
#   2. Lo levanta y te da un link para autenticarlo con tu cuenta
#   3. A partir de ahí, el EliteBook es accesible por SSH desde cualquier
#      dispositivo logueado en tu misma cuenta de Tailscale (celular,
#      laptop de la universidad, etc.) sin abrir puertos en el router.
#
# Después de correr esto, revisa tu IP de Tailscale con: tailscale ip -4

set -e

echo "=== Instalando Tailscale ==="
curl -fsSL https://tailscale.com/install.sh | sh

echo ""
echo "=== Levantando Tailscale ==="
echo "Se abrirá un link para autenticarte con tu cuenta de Google/GitHub."
sudo tailscale up

echo ""
echo "=== Listo ==="
echo "IP de Tailscale de este equipo:"
tailscale ip -4
echo ""
echo "Desde ahora puedes conectarte por SSH usando esa IP, desde cualquier"
echo "otro dispositivo donde también tengas Tailscale instalado y logueado"
echo "con la misma cuenta (ej. tu celular o la laptop de la universidad)."
