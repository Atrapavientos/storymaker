#!/bin/bash
# Aplica la placa elegida en el portal. Uso: storymaker-perfil.sh {storymaker_pcb|voicehat_pi3}
# Instalar en: /usr/local/bin/ (root:root 0755). Lo invoca el portal vía sudo,
# con los dos argumentos fijados en /etc/sudoers.d/storymaker-perfil.
#
# El keepalive de audio no se gestiona aquí: es un hilo de modules/audio.py.
set -uo pipefail

CONFIG="/boot/firmware/config.txt"
ASOUND_DIR="/usr/local/share/storymaker/asound"
ASOUND_DEST="/etc/asound.conf"
MARCA_OFF="#storymaker-off# "
INICIO="# >>> storymaker placa"
FIN="# <<< storymaker placa"
OVERLAYS='^[[:space:]]*dtoverlay=(max98357a|hifiberry-dac|googlevoicehat-soundcard)([,[:space:]].*)?$'

placa="${1:-}"
case "$placa" in
  storymaker_pcb|voicehat_pi3) ;;
  *) echo "Placa no válida: $placa" >&2; exit 2 ;;
esac

if [ ! -f "$ASOUND_DIR/$placa.conf" ]; then
  echo "Falta $ASOUND_DIR/$placa.conf" >&2
  exit 3
fi

[ -f "$CONFIG.storymaker.bak" ] || cp "$CONFIG" "$CONFIG.storymaker.bak" || exit 4

tmp="$CONFIG.storymaker.tmp"
# Parte siempre del estado original: quita el bloque y reactiva lo desactivado
sed -e "/^$INICIO\$/,/^$FIN\$/d" -e "s/^$MARCA_OFF//" "$CONFIG" > "$tmp" || exit 4

if [ "$placa" = "voicehat_pi3" ]; then
  sed -E -i "/$OVERLAYS/s/^/$MARCA_OFF/" "$tmp" || exit 4
  printf '%s\n[all]\ndtoverlay=googlevoicehat-soundcard\n%s\n' "$INICIO" "$FIN" >> "$tmp" || exit 4
fi

[ -s "$tmp" ] || { echo "config.txt resultante vacío" >&2; exit 4; }
mv "$tmp" "$CONFIG" || exit 4
sync

install -m 0644 "$ASOUND_DIR/$placa.conf" "$ASOUND_DEST" || exit 5
exit 0
