#!/usr/bin/env bash
# =============================================================================
# crear_actualizacion.sh — Empaqueta y firma una actualización menor
# =============================================================================
# Una actualización lleva solo el firmware (lo mismo que deploy.sh) y la caja
# la instala desde el portal sin tocar perfiles ni configuración. El diseño
# está en modules/actualizador.py.
#
# USO:
#   ./crear_actualizacion.sh --clave
#       Genera el par de claves (una sola vez). La privada queda en
#       ~/.config/storymaker/ y la pública en firmware/clave_actualizaciones.pem,
#       que viaja en la imagen.
#
#   ./crear_actualizacion.sh "Notas de la versión"
#       Empaqueta el firmware de HEAD. firmware/VERSION tiene que ser X.Y.Z con
#       Z ≥ 1, y tiene que existir el tag vX.Y de la imagen sobre la que se
#       instala. Deja en releases/ el .tar, su .sha256 y actualizacion.json.
#
#   ./crear_actualizacion.sh --manifiesto-imagen
#       Al publicar una imagen nueva (VERSION = X.Y): genera actualizacion.json
#       sin actualización, solo con la imagen vigente.
#
# CLAVE PRIVADA: STORYMAKER_CLAVE la cambia de sitio. Sin ella no se pueden
# publicar actualizaciones para las cajas que llevan su pública: guárdala con
# copia de seguridad. Si se pierde, la siguiente imagen tiene que llevar una
# pública nueva.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
CLAVE_PRIV="${STORYMAKER_CLAVE:-$HOME/.config/storymaker/clave_actualizaciones.key}"
CLAVE_PUB="$REPO/firmware/clave_actualizaciones.pem"
# Repositorio canónico: el del QR. Las cajas leen allí actualizacion.json
PUBLICO="https://codeberg.org/atrapavientos/storymaker"
SALIDA_DIR="$REPO/releases"

error() { echo "ERROR: $*" >&2; exit 1; }

# ── Generar claves ───────────────────────────────────────────────────
if [ "${1:-}" = "--clave" ]; then
    [ -e "$CLAVE_PRIV" ] && error "ya existe $CLAVE_PRIV; no se sobrescribe."
    mkdir -p "$(dirname "$CLAVE_PRIV")"
    chmod 700 "$(dirname "$CLAVE_PRIV")"
    (umask 077; openssl genpkey -algorithm ed25519 -out "$CLAVE_PRIV")
    openssl pkey -in "$CLAVE_PRIV" -pubout -out "$CLAVE_PUB"
    echo "Clave privada: $CLAVE_PRIV  (haz copia de seguridad; no la subas a ningún repo)"
    echo "Clave pública: $CLAVE_PUB  (se commitea; viaja en la imagen)"
    exit 0
fi

VERSION="$(git -C "$REPO" show HEAD:firmware/VERSION 2>/dev/null | tr -d '[:space:]')"
[ -n "$VERSION" ] || error "no hay firmware/VERSION en HEAD."

escribir_manifiesto() {   # $1 = versión de la imagen, $2.. = actualización (opcional)
    python3 - "$SALIDA_DIR/actualizacion.json" "$PUBLICO" "$@" <<'PYEOF'
import json, sys
ruta, publico, imagen = sys.argv[1:4]
m = {"imagen": {"version": imagen, "url": f"{publico}/releases/tag/v{imagen}"},
     "actualizacion": None}
if len(sys.argv) > 4:
    version, fichero, sha, notas = sys.argv[4:8]
    m["actualizacion"] = {"version": version,
                          "url": f"{publico}/releases/download/v{imagen}/{fichero}",
                          "sha256": sha, "notas": notas}
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
    f.write("\n")
PYEOF
}

# ── Manifiesto de una imagen nueva ───────────────────────────────────
if [ "${1:-}" = "--manifiesto-imagen" ]; then
    [[ "$VERSION" =~ ^[0-9]+\.[0-9]+$ ]] || error "VERSION es $VERSION; para una imagen debe ser X.Y."
    mkdir -p "$SALIDA_DIR"
    escribir_manifiesto "$VERSION"
    echo "→ $SALIDA_DIR/actualizacion.json (imagen v$VERSION, sin actualización)"
    echo "  Cópialo a la raíz del repo público y empuja."
    exit 0
fi

# ── Actualización ────────────────────────────────────────────────────
NOTAS="${1:-}"
[ -n "$NOTAS" ] || error "faltan las notas de la versión: $0 \"Qué cambia\""
[ -f "$CLAVE_PRIV" ] || error "no se encuentra la clave privada en $CLAVE_PRIV."
[ -f "$CLAVE_PUB" ]  || error "no se encuentra $CLAVE_PUB."

[ -z "$(git -C "$REPO" status --porcelain -- firmware)" ] \
    || error "hay cambios sin commit en firmware/: el paquete se hace desde HEAD."

[[ "$VERSION" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]] \
    || error "VERSION es $VERSION; una actualización debe ser X.Y.Z (p. ej. 1.0.1)."
BASE="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
[ "${BASH_REMATCH[3]}" -ge 1 ] || error "el tercer número debe ser 1 o más."
git -C "$REPO" rev-parse -q --verify "refs/tags/v$BASE" >/dev/null \
    || error "no existe el tag v$BASE de la imagen sobre la que se instala."

# Lo que no puede llegar por esta vía: ficheros de sistema o dependencias
SISTEMA="$(git -C "$REPO" diff --name-only "v$BASE" HEAD -- \
    firmware/deploy/sistema firmware/deploy/setup_sd.sh)"
if [ -n "$SISTEMA" ]; then
    echo "Cambios desde v$BASE que una actualización no puede instalar:" >&2
    echo "$SISTEMA" | sed 's/^/  /' >&2
    error "esto necesita una imagen nueva (v${BASH_REMATCH[1]}.$(( ${BASH_REMATCH[2]} + 1 )))."
fi
git -C "$REPO" diff --quiet "v$BASE" HEAD -- firmware/clave_actualizaciones.pem \
    || error "la clave pública ha cambiado desde v$BASE: las cajas rechazarían el paquete."

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[1/3] Empaquetando el firmware de HEAD (v$VERSION, sobre la imagen v$BASE)..."
git -C "$REPO" archive HEAD firmware | tar -x -C "$TMP"
F="$TMP/firmware"
rm -rf "$F/deploy" "$F/data/config.json" "$F/data/perfiles"
tar --sort=name --owner=0 --group=0 --numeric-owner \
    -czf "$TMP/contenido.tar.gz" -C "$F" .

echo "[2/3] Firmando..."
openssl pkeyutl -sign -inkey "$CLAVE_PRIV" -rawin \
    -in "$TMP/contenido.tar.gz" -out "$TMP/contenido.tar.gz.sig"
openssl pkeyutl -verify -pubin -inkey "$CLAVE_PUB" -rawin \
    -in "$TMP/contenido.tar.gz" -sigfile "$TMP/contenido.tar.gz.sig" >/dev/null \
    || error "la clave privada no corresponde a firmware/clave_actualizaciones.pem."

echo "[3/3] Generando paquete y manifiesto..."
mkdir -p "$SALIDA_DIR"
FICHERO="storymaker-actualizacion-$VERSION.tar"
tar --owner=0 --group=0 --numeric-owner -cf "$SALIDA_DIR/$FICHERO" \
    -C "$TMP" contenido.tar.gz contenido.tar.gz.sig
SHA="$(sha256sum "$SALIDA_DIR/$FICHERO" | cut -d' ' -f1)"
echo "$SHA  $FICHERO" > "$SALIDA_DIR/$FICHERO.sha256"
escribir_manifiesto "$BASE" "$VERSION" "$FICHERO" "$SHA" "$NOTAS"

echo ""
echo "Listo: releases/$FICHERO ($(du -h "$SALIDA_DIR/$FICHERO" | cut -f1))"
echo ""
echo "Para publicarla:"
echo "  1. Adjuntarla a la release v$BASE del repo público:"
echo "     tea releases assets create --login codeberg --repo atrapavientos/storymaker v$BASE \\"
echo "         releases/$FICHERO"
echo "  2. Copiar releases/actualizacion.json a la raíz del repo público, commit y push."
echo "     Desde ese momento las cajas la ven (comprueban una vez al día o con «Buscar ahora»)."
