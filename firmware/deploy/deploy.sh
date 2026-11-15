#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Despliega el firmware actualizado en la Pi
# =============================================================================
# Preserva config.json y data/perfiles/ (datos de producción en el dispositivo).
# Solo actualiza el código Python y los recursos estáticos (imágenes, etc.)
#
# USO:
#   cd firmware/deploy
#   ./deploy.sh 192.168.1.50
#   ./deploy.sh storymaker@192.168.1.50       # usuario alternativo
#   ./deploy.sh --solo-firmware 192.168.1.50  # omite los ficheros de sistema
#
# SOBRE LA CONTRASEÑA DE sudo:
#   Las imágenes a partir de v2026-10-03 ya no traen el `NOPASSWD: ALL` que
#   Raspberry Pi OS instala de serie, así que instalar ficheros de sistema exige
#   la contraseña del dispositivo. Ese paso usa `ssh -t` para que sudo tenga
#   terminal donde pedirla; sin -t falla con «a terminal is required».
#   Reiniciar historias.service sí está en la lista corta de /etc/sudoers.d, por
#   eso no necesita terminal.
#
#   Con --solo-firmware se omite el paso privilegiado. Sirve cuando sólo ha
#   cambiado código Python, que es el caso habitual: comprueba antes con
#   `git diff --name-only <tag-de-la-imagen>..HEAD -- firmware/deploy/sistema/`
#   que no haya cambios ahí.
# =============================================================================

set -euo pipefail

SOLO_FIRMWARE=false
DESTINO=""
for ARG in "$@"; do
    case "$ARG" in
        --solo-firmware) SOLO_FIRMWARE=true ;;
        -*)              echo "Opción no reconocida: $ARG"; exit 1 ;;
        *)               DESTINO="$ARG" ;;
    esac
done

if [ -z "$DESTINO" ]; then
    echo "Uso: $0 [--solo-firmware] [usuario@]<ip>"
    echo "Ejemplo: $0 192.168.1.50"
    echo "         $0 storymaker@192.168.1.50"
    echo "         $0 --solo-firmware 192.168.1.50"
    exit 1
fi

# Añadir usuario por defecto si no se especificó
[[ "$DESTINO" == *@* ]] || DESTINO="storymaker@${DESTINO}"
IP="${DESTINO#*@}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PAQUETE="storymaker_deploy.tar.gz"
PROYECTO_REMOTO="/home/storymaker/proyecto"
CAPTIVE_SRC="${SCRIPT_DIR}/sistema/storymaker-captive.py"
SETPASS_SRC="${SCRIPT_DIR}/sistema/storymaker-setpass"
SUDOERS_SRC="${SCRIPT_DIR}/sistema/storymaker-shutdown"
PERFIL_SRC="${SCRIPT_DIR}/sistema/storymaker-perfil.sh"
PERFIL_SUDOERS_SRC="${SCRIPT_DIR}/sistema/storymaker-perfil.sudoers"
ARRANQUE_SRC="${SCRIPT_DIR}/sistema/storymaker-arranque"
SERVICIO_SRC="${SCRIPT_DIR}/sistema/historias.service"
ASOUND_SRC_DIR="${SCRIPT_DIR}/sistema/asound"

echo "╔══════════════════════════════════════════╗"
echo "║      StoryMaker — Deploy                 ║"
echo "╠══════════════════════════════════════════╣"
printf "║  Destino: %-33s║\n" "${DESTINO}"
echo "╚══════════════════════════════════════════╝"
echo ""

# [0] Verificar que los ficheros de sistema existen en local
for F in "$CAPTIVE_SRC" "$SETPASS_SRC" "$SUDOERS_SRC" "$PERFIL_SRC" "$PERFIL_SUDOERS_SRC" \
         "$ARRANQUE_SRC" "$SERVICIO_SRC" \
         "$ASOUND_SRC_DIR/storymaker_pcb.conf" "$ASOUND_SRC_DIR/voicehat_pi3.conf"; do
    if [ ! -f "$F" ]; then
        echo "ERROR: no se encuentra ${F}"
        exit 1
    fi
done
echo ""

# [1] Empaquetar
echo "[1/6] Empaquetando firmware..."
tar -czf "/tmp/$PAQUETE" \
    -C "$FIRMWARE_DIR" \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='./deploy' \
    --exclude='./data/config.json' \
    --exclude='./data/perfiles' \
    .

SIZE=$(du -h "/tmp/$PAQUETE" | cut -f1)
echo "      → $PAQUETE ($SIZE)"

# [2] Subir
echo "[2/6] Subiendo a la Pi..."
scp "/tmp/$PAQUETE" "${DESTINO}:/tmp/"
rm -f "/tmp/$PAQUETE"
echo "      → Subido"

# [3] Extraer
echo "[3/6] Extrayendo..."
ssh "$DESTINO" bash <<REMOTE
set -e
tar -xzf /tmp/${PAQUETE} -C ${PROYECTO_REMOTO}
rm -f /tmp/${PAQUETE}
echo "      → Extraído en ${PROYECTO_REMOTO}"
REMOTE

# [4] edge-tts al día. Microsoft cambia el protocolo de vez en cuando y las
# versiones antiguas reciben un 403: la caja se queda muda. Va en el venv del
# proyecto, sin sudo. Sin internet no se puede actualizar, y el despliegue sigue.
echo "[4/6] Actualizando edge-tts..."
ssh "$DESTINO" "${PROYECTO_REMOTO}/venv/bin/pip install -q -U edge-tts 2>&1 | grep -v -e notice -e '^[[:space:]]*$'; \
    ${PROYECTO_REMOTO}/venv/bin/pip show edge-tts | grep -i ^version" \
    | sed 's/^/      → edge-tts /' || echo "      AVISO: no se ha podido actualizar edge-tts"

# [5] Ficheros de sistema: captivo, ayudante de contraseña, cambio de placa y sudoers
# Van juntos y en una sola sesión `ssh -t`, para que sudo pida la contraseña una
# única vez y su caché cubra el resto de órdenes. Antes esto eran tres `ssh`
# sueltos sin terminal, que desde que la imagen no trae NOPASSWD: ALL fallan con
# «sudo: a terminal is required to read the password».
if [ "$SOLO_FIRMWARE" = true ]; then
    echo "[5/6] Ficheros de sistema — omitidos (--solo-firmware)"
else
    echo "[5/6] Instalando ficheros de sistema (sudo pedirá la contraseña del dispositivo)..."
    scp "$CAPTIVE_SRC" "${DESTINO}:/tmp/storymaker-captive.py"
    scp "$SETPASS_SRC" "${DESTINO}:/tmp/storymaker-setpass"
    scp "$SUDOERS_SRC" "${DESTINO}:/tmp/storymaker-shutdown"
    scp "$PERFIL_SRC"  "${DESTINO}:/tmp/storymaker-perfil.sh"
    scp "$PERFIL_SUDOERS_SRC" "${DESTINO}:/tmp/storymaker-perfil.sudoers"
    scp "$ARRANQUE_SRC" "${DESTINO}:/tmp/storymaker-arranque"
    scp "$SERVICIO_SRC" "${DESTINO}:/tmp/historias.service"
    ssh "$DESTINO" "mkdir -p /tmp/storymaker-asound"
    scp "$ASOUND_SRC_DIR"/*.conf "${DESTINO}:/tmp/storymaker-asound/"
    # El sudoers se valida ANTES de instalarlo: un fichero malformado en
    # /etc/sudoers.d deja el dispositivo sin sudo de ningún tipo.
    ssh -t "$DESTINO" "sudo sh -c '
        set -e
        visudo -c -f /tmp/storymaker-shutdown
        visudo -c -f /tmp/storymaker-perfil.sudoers
        install -m 755 -o root -g root /tmp/storymaker-captive.py /usr/local/bin/storymaker-captive.py
        install -m 755 -o root -g root /tmp/storymaker-setpass    /usr/local/bin/storymaker-setpass
        install -m 440 -o root -g root /tmp/storymaker-shutdown   /etc/sudoers.d/storymaker-shutdown
        install -m 755 -o root -g root /tmp/storymaker-perfil.sh  /usr/local/bin/storymaker-perfil.sh
        install -m 440 -o root -g root /tmp/storymaker-perfil.sudoers /etc/sudoers.d/storymaker-perfil
        install -d -m 755 -o root -g root /usr/local/share/storymaker/asound
        install -m 644 -o root -g root /tmp/storymaker-asound/*.conf /usr/local/share/storymaker/asound/
        install -m 755 -o root -g root /tmp/storymaker-arranque   /usr/local/bin/storymaker-arranque
        install -m 644 -o root -g root /tmp/historias.service     /etc/systemd/system/historias.service
        systemctl daemon-reload
        systemctl restart storymaker-captive.service
    ' ; rm -rf /tmp/storymaker-captive.py /tmp/storymaker-setpass /tmp/storymaker-shutdown \
             /tmp/storymaker-perfil.sh /tmp/storymaker-perfil.sudoers /tmp/storymaker-asound \
             /tmp/storymaker-arranque /tmp/historias.service"
    echo "      → Captivo, ayudantes, guardián de actualizaciones, servicio y permisos actualizados"
fi

# [6] Reiniciar servicio principal
# Esta orden sí está en /etc/sudoers.d/storymaker-shutdown, así que no necesita
# terminal ni contraseña.
echo "[6/6] Reiniciando historias.service..."
ssh "$DESTINO" "sudo -n systemctl restart historias.service"
echo "      → Servicio reiniciado"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Deploy completado.                      ║"
echo "╚══════════════════════════════════════════╝"
