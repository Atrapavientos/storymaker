# Configuración del sistema

Referencia de **qué deja instalado** el proceso de despliegue en la Raspberry Pi:
ficheros, servicios y ajustes del sistema operativo que quedan fuera de la carpeta
del proyecto.

Esto **no son pasos manuales**: lo instala todo `firmware/deploy/setup_sd.sh`.
Los pasos están en [`manuales/despliegue.md`](manuales/despliegue.md).

## Archivos instalados

| Archivo en el repositorio | Destino en la Pi | Descripción |
|---|---|---|
| `deploy/sistema/historias.service` | `/etc/systemd/system/` | Servicio principal de Python |
| `deploy/sistema/storymaker-wifi.service` | `/etc/systemd/system/` | Decide modo de red al arrancar |
| `deploy/sistema/storymaker-captive.service` | `/etc/systemd/system/` | Portal cautivo (puerto 8080) |
| `deploy/sistema/storymaker-wifi.sh` | `/usr/local/bin/` | Script de gestión WiFi (cliente/AP) |
| `deploy/sistema/storymaker-captive.py` | `/usr/local/bin/` | Portal cautivo Flask |
| `deploy/sistema/storymaker-shutdown` | `/etc/sudoers.d/` | `NOPASSWD` para apagar, reiniciar el servicio y fijar contraseña |
| `deploy/sistema/storymaker-setpass` | `/usr/local/bin/` | Fija la contraseña SSH del dispositivo (lo llama el portal) |

El firmware en sí vive en `/home/storymaker/proyecto/`, con su entorno virtual
en `proyecto/venv/`.

## Acceso y credenciales

El dispositivo tiene dos credenciales:

- **PIN del portal web** — protege el panel de control. Opcionalmente se cambia
  en el asistente de primer arranque.
- **Contraseña SSH del usuario `storymaker`** — acceso al sistema operativo. El
  asistente **obliga** a definir una propia; sin ella no deja terminar la
  configuración.

Los valores con los que sale la imagen distribuible se muestran en la propia
pantalla del dispositivo durante el primer arranque, así que no hay que
buscarlos aquí. Son iguales en todas las unidades descargadas, y por eso el
asistente no permite dejar la de SSH como viene.

### Cómo se aplica el cambio de contraseña

Lo hace `/usr/local/bin/storymaker-setpass`, que el portal invoca vía `sudo` con
una línea `NOPASSWD`. Tres detalles que no son casuales:

- La contraseña le llega por **stdin**, nunca como argumento: un argumento sería
  visible en `ps` para cualquier otro proceso de la máquina.
- El usuario va **fijado dentro del script**. Permitir `sudo chpasswd` a secas
  dejaría cambiar la de cualquier cuenta, `root` incluida.
- La validación se repite dentro del script, por ser la frontera de privilegio:
  lo que valide el portal no es garantía de nada.

### Retirada de `NOPASSWD: ALL`

`setup_sd.sh` y los dos scripts de limpieza **eliminan
`/etc/sudoers.d/010_pi-nopasswd`**, el `NOPASSWD: ALL` que Raspberry Pi OS
instala de serie. Sin ese recorte, entrar por SSH equivale a ser `root`, y
entonces tener una contraseña propia por dispositivo serviría de poco.

Quedan permitidas sin contraseña sólo las tres órdenes de
`storymaker-shutdown`. `sudo` sigue funcionando para todo lo demás pidiendo la
contraseña del dispositivo.

## Red y WiFi

- **NetworkManager** gestiona `wlan0`.
- **mDNS** vía `avahi-daemon` → el dispositivo responde a `storymaker.local`.
- **Sin red conocida** → levanta el punto de acceso `StoryMaker-Setup`
  (abierto, `10.42.0.1`).
- **Portal cautivo** Flask en el puerto 8080; `iptables` redirige el 80 al 8080,
  de modo que el móvil abra la página de configuración por su cuenta.
- Script de decisión: `/usr/local/bin/storymaker-wifi.sh`.

## Servicios habilitados

```
historias.service           # arranca con el sistema
storymaker-wifi.service     # antes de historias
storymaker-captive.service  # siempre activo (sólo responde en modo AP)
avahi-daemon                # mDNS → storymaker.local
NetworkManager-wait-online  # DESHABILITADO (arranque más rápido)
```

## Otros ajustes

- SPI habilitado (`dtparam=spi=on` en `config.txt`)
- UART estable para la impresora (`enable_uart=1` + `dtoverlay=disable-bt`)
- Audio I2S (`dtoverlay=hifiberry-dac`)
- Consola serie eliminada de `cmdline.txt`, para dejar el UART libre
- El usuario `storymaker` pertenece a los grupos `spi`, `gpio`, `dialout`, `audio`
- `/etc/asound.conf` con `dmix` para el MAX98357A: evita el chasquido entre premisas
- Perfil de AP en NetworkManager: `StoryMaker-Setup`, `10.42.0.1`, modo
  `infrastructure`/`ap`
- `iptables`: `PREROUTING -i wlan0 -p tcp --dport 80 → :8080`
- `journald` con `Storage=auto` (volátil), para no saturar la tarjeta SD
