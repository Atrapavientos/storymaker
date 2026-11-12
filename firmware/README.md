# Firmware

Código Python que corre en la Raspberry Pi Zero 2W con la placa del proyecto, o
en una Raspberry Pi 3 con el Voice HAT de Google (kit AIY V1, solo voz).
Gestiona el botón físico, las salidas (e-ink, impresora térmica, audio) y el
portal web de configuración.

Licencia: **GPLv3** (ver `/LICENSE`).

Para instalarlo en un dispositivo nuevo, sigue
[el manual de despliegue](../docs/manuales/despliegue.md). Para usarlo una vez
instalado, [el manual de usuario](../docs/manuales/usuario.md).

## Requisitos

- Raspberry Pi OS Lite 64-bit (**Bookworm**, Debian 12)
- Python 3.11+
- Entorno virtual en `proyecto/venv/`, creado con `--system-site-packages`

> **No funciona en Debian 13 (Trixie).** `RPi.GPIO` está obsoleto allí y el
> firmware depende de él para el polling del botón. Ver `../docs/decisiones.md`.

## Estructura

```
firmware/
├── main.py                   # Punto de entrada: inicializa hardware y bucle principal
├── modules/
│   ├── boton.py              # Polling GPIO: pulsación corta/larga + LED
│   ├── eink.py               # Pantalla e-ink WeAct 4.2" (SSD1683, SPI0)
│   ├── audio.py              # Síntesis de voz edge-tts + reproducción mpg123
│   ├── impresora.py          # Impresora térmica QR701 o QR204 por UART (ESC/POS)
│   ├── generador.py          # Generador de premisas aleatorias desde perfiles .txt
│   ├── importador.py         # Importación masiva de premisas desde .txt
│   ├── salidas.py            # Orquesta las salidas activas + animación e-ink
│   ├── portal.py             # Portal web Flask (puerto 5000)
│   ├── config_manager.py     # Lectura/escritura atómica de config.json (thread-safe)
│   ├── netinfo.py            # Detecta modo de red (cliente/AP/sin red)
│   ├── placas.py             # Pines y salidas de cada placa (PCB, Voice HAT)
│   ├── anuncio_red.py        # Solo con altavoz: dicta el AP o la IP por voz
│   └── __init__.py
├── static/fuentes/           # Lora e Inter para el portal (SIL OFL 1.1, ver /CREDITS.md)
├── data/
│   ├── config.json           # Configuración activa del dispositivo
│   ├── config.template.json  # Plantilla para dispositivos nuevos
│   ├── pluma.png             # Animación "pensando" para e-ink
│   ├── logo_atrapa.png       # Logo del taller
│   ├── voz/                  # Avisos de red pregrabados (voz Elvira)
│   └── perfiles/
│       ├── juvenil/          # Perfil de ejemplo
│       │   ├── detonantes.txt
│       │   ├── protagonistas.txt
│       │   └── conflictos.txt
│       └── adultos/
└── deploy/                   # Scripts de instalación y creación de imagen
    ├── prepare_sd.sh         # Prepara la SD desde el PC (usuario, SSH, WiFi)
    ├── setup_sd.sh           # Instalación completa sobre una Pi recién arrancada
    ├── deploy.sh             # Actualización incremental de firmware
    ├── crear_imagen.sh       # Genera la imagen .img.xz distribuible
    ├── limpiar_pi.sh         # Limpieza previa a la imagen (Pi encendida)
    ├── limpiar_montada.sh    # Limpieza previa a la imagen (SD montada en el PC)
    ├── generar_voz.py        # Regenera los avisos de data/voz/ (se ejecuta en el PC)
    └── sistema/              # Servicios systemd, sudoers y scripts de red
```

## Salidas disponibles

| Salida | Módulo | Interfaz |
|---|---|---|
| Pantalla e-ink | `eink.py` | SPI0 (GPIO 10/11/8) + DC/RST/BUSY |
| Impresora térmica | `impresora.py` | UART (`/dev/serial0`, 9600 baud) |
| Audio | `audio.py` | I2S MAX98357A (GPIO 18/19/21) |

Las tres son independientes y se activan o desactivan desde el portal web. El
dispositivo funciona con cualquier combinación, incluida ninguna. Con el Voice
HAT solo hay audio, por el propio HAT; sus pines están en `modules/placas.py`.

## Perfiles

Cada perfil es una carpeta en `data/perfiles/<nombre>/` con tres archivos `.txt`,
una frase por línea: `detonantes.txt`, `protagonistas.txt`, `conflictos.txt`.
El perfil activo se guarda en `config.json` → `perfil_activo`.

La premisa se compone concatenando una frase de cada lista:

```
<detonante>, <protagonista> <conflicto>
```

Por eso los detonantes suelen terminar en coma, los protagonistas no llevan
puntuación final y los conflictos cierran la frase con punto.

### Importar premisas en bloque

`⇪ Importar .txt` en el portal (`/importar`): tres pasos, revisión antes de
escribir y un nivel de deshacer mediante `<tipo>.txt.bak`. Cómo se usa, en el
[manual de usuario](../docs/manuales/usuario.md#8-importar-listas-desde-un-txt);
las decisiones de diseño, en [`docs/decisiones.md`](../docs/decisiones.md).

## Despliegue

El servicio systemd se llama `historias.service` y corre como usuario
`storymaker`. Los pasos completos están en
[`../docs/manuales/despliegue.md`](../docs/manuales/despliegue.md); la
referencia de qué queda instalado dónde, en
[`../docs/sistema.md`](../docs/sistema.md).
