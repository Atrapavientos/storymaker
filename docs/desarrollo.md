# Para quien desarrolle el firmware

Lo que no necesita quien monta o usa una máquina: generar la imagen de tarjeta
que se publica en las releases, publicar actualizaciones, y dónde está la
referencia técnica.

Antes de esto, la Ruta B del [manual de despliegue](manuales/despliegue.md)
explica cómo instalar desde el código y cómo actualizar una máquina con
`deploy.sh`.

## Referencia técnica

| Documento | Contenido |
|---|---|
| [`decisiones.md`](decisiones.md) | Por qué el firmware está hecho así y qué alternativas se descartaron |
| [`hardware.md`](hardware.md) | Pinout, periféricos, Voice HAT y problemas de audio vistos en desarrollo |
| [`sistema.md`](sistema.md) | Qué deja instalado `setup_sd.sh` fuera de la carpeta del proyecto: servicios, sudoers, red |
| [`troubleshooting.md`](troubleshooting.md) | Trampas encontradas durante el desarrollo, para no repetirlas |

## Crear una imagen distribuible

Para empaquetar un dispositivo ya configurado como imagen `.img.xz`. Hace
falta Linux con `bash`, `ssh`, `rsync`, `xz` y `pishrink.sh`:

```bash
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh && sudo mv pishrink.sh /usr/local/bin/
```

Dos modos:

```bash
cd firmware/deploy
./crear_imagen.sh 192.168.1.XX   # limpia la Pi por SSH y la apaga
./crear_imagen.sh --local        # la Pi ya está apagada y la SD en el PC
```

El proceso limpia el dispositivo (WiFi, configuración, claves SSH, historial y
registros), deja todas las salidas apagadas, devuelve `config.txt` y el audio a
la placa del proyecto aunque la Pi de origen lleve el Voice HAT, sustituye
`data/perfiles/` por los perfiles del repositorio, captura la tarjeta con `dd`,
la encoge con `pishrink` y la comprime con `xz`. Los dos modos dejan la imagen
igual, sea cual sea la Pi de la que salga.

**Antes de capturar, verifica la tarjeta a mano.** Monta la partición raíz en
sólo lectura y comprueba que no quedan claves de host SSH, que
`authorized_keys` y `.bash_history` están vacíos, que ha desaparecido
`/etc/sudoers.d/010_pi-nopasswd`, que `storymaker-setpass` sigue instalado, que
sólo queda el perfil de red del punto de acceso y que `config.json` tiene
`setup_completado: false`. Ese repaso es el que detecta los fallos de limpieza;
durante meses la limpieza se ejecutó a medias sin que nadie lo notara,
precisamente porque nadie miraba.

> **Después de capturar, la tarjeta queda inservible tal cual.** El sistema de
> ficheros se ha encogido al mínimo y el gancho que lo vuelve a expandir lo
> añade `pishrink` a la imagen, no a la tarjeta. Vuelve a grabarla con la imagen
> recién generada antes de usar esa Pi otra vez.

Por último, genera la huella que acompaña a la descarga:

```bash
sha256sum storymaker-v1.0.img.xz | tee storymaker-v1.0.img.xz.sha256
```

La imagen se nombra con la versión de `firmware/VERSION` (`X.Y`). Ella y su
`.sha256` se publican como adjuntos de una release en Codeberg, nunca dentro
del repositorio.

## Publicar una actualización

Las máquinas instalan desde el panel las versiones `X.Y.Z` que solo cambian el
firmware de `/home/storymaker/proyecto`, sin tocar perfiles ni configuración
(ver [`decisiones.md`](decisiones.md)). Lo que toque `firmware/deploy/sistema/`,
`setup_sd.sh` o paquetes del sistema necesita una imagen nueva, `X.(Y+1)`.

```bash
cd firmware/deploy
./crear_actualizacion.sh --clave            # una sola vez: par de claves Ed25519
# firmware/VERSION = 1.0.1, commit, y que exista el tag v1.0 de la imagen
./crear_actualizacion.sh "Qué cambia"
```

El script empaqueta el firmware de `HEAD`, lo firma con la clave privada
(`~/.config/storymaker/`, fuera del repositorio) y deja en `releases/` el
`.tar`, su `.sha256` y `actualizacion.json`. Se niega a seguir si hay cambios
de sistema desde la imagen. El `.tar` se adjunta a la release **de la imagen**
y `actualizacion.json` va a la raíz de este repositorio, que es donde lo leen
las máquinas. Con una imagen nueva, `--manifiesto-imagen` genera un
`actualizacion.json` sin actualización, que hace que las máquinas avisen de
que tienen que regrabar.

**Si replicas el proyecto con tus propias actualizaciones:** genera tu par de
claves (la pública, `firmware/clave_actualizaciones.pem`, viaja en tu imagen)
y cambia `MANIFIESTO` en `modules/actualizador.py` para que apunte a tu
repositorio. Si no, tus máquinas buscarán actualizaciones de este proyecto, y
rechazarán por la firma las que publique.
