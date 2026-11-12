# Para quien desarrolle el firmware

Lo que no necesita quien monta o usa una máquina: generar la imagen de tarjeta
que se publica en las releases, y dónde está la referencia técnica.

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
sha256sum storymaker-$(date +%F).img.xz | tee storymaker-$(date +%F).img.xz.sha256
```

La imagen y su `.sha256` se publican como adjuntos de una release en Codeberg,
nunca dentro del repositorio.
