# Referencia de hardware

## OS
Raspberry Pi OS Lite 64-bit Bookworm (estable)

## Pinout (BCM)
| Función | GPIO |
|---|---|
| Botón físico | 5 |
| LED estado | 23 |
| E-ink DC | 25 |
| E-ink RST | 17 |
| E-ink BUSY | 24 |
| E-ink SPI0 MOSI | 10 |
| E-ink SPI0 CLK | 11 |
| E-ink SPI0 CS0 | 8 |
| Impresora UART TX | 14 |
| Impresora UART RX | 15 |
| Audio I2S BCLK | 18 |
| Audio I2S LRCLK | 19 |
| Audio I2S DATA | 21 |

## Periféricos
- **E-ink:** WeAct 4.2" B&W (SSD1683) — refresco parcial NO soportado
- **Impresora:** QR701 UART térmica (ESC/POS, QR nativo GS(k) modelo 2)
  - Compatible sin cambios: **QR204 TTL+USB**, conectada por TTL a 9600 bps (probada el 2026-11-07)
- **Audio:** MAX98357A I2S — TTS edge-tts (es-ES-ElviraNeural) + mpg123
- **Fallback TTS offline:** espeak (voz local, entra cuando no hay red)

## Audio: la caja recibe la premisa pero no suena
Mirar el registro: `journalctl -u historias.service -n 50`.
- **`edge-tts fallo (403, message='Invalid response status' …)`.** Microsoft ha
  cambiado el protocolo y la versión instalada de edge-tts ya no vale. Pasó con
  la release del 3 de octubre de 2026 (edge-tts 7.2.8). Arreglo:
  `~/proyecto/venv/bin/pip install -U edge-tts` y
  `sudo systemctl restart historias.service`. `deploy.sh` lo actualiza en cada
  despliegue.
- **espeak «completado» sin sonido.** En versiones anteriores a v2026-11-07,
  espeak abría la tarjeta directamente y chocaba con el keepalive
  («Device or resource busy»). Ahora sale por `plug:dmixed`.

## LED (GPIO 23; GPIO 25 en el Voice HAT)
- Fijo encendido → sistema listo
- Parpadeo → feedback de pulsación
- Apagado → en proceso de shutdown

## Voice HAT de Google (kit AIY V1) con Raspberry Pi 3

Alternativa a la PCB solo con voz: sin e-ink ni impresora. Se elige en el
asistente (`/setup` → Placa) y `storymaker-perfil.sh` cambia el overlay y el
`asound.conf` (ver `sistema.md` › Cambio de placa). Pines y salidas en
`firmware/modules/placas.py`.

| Función | GPIO | Notas |
|---|---|---|
| Botón | 23 | Pull-up interno, activo LOW. En la PCB, GPIO23 es el LED |
| LED del botón | 25 | Activo en alto. En la PCB, GPIO25 es D/C de la e-ink |
| Apagado del amplificador | 16 | Lo gestiona el driver del overlay: el firmware no lo toca |
| Audio I2S | 18, 19, 21 | Overlay `googlevoicehat-soundcard` |

- **Tarjeta ALSA:** `sndrpigooglevoi`. Su número cambia según los overlays (en
  la Pi 3 el jack y el HDMI también son tarjetas), por eso `asound.conf` la
  nombra en vez de usar `hw:0`.
- **Formato:** solo S32_LE, 48000 Hz, 2 canales. Sin controles de mezclador: el
  volumen lo aplican `mpg123 -f` y la amplitud de espeak.
- **Detección automática.** El HAT lleva una EEPROM que se presenta como
  «Google AIY audioHAT Board v1» (`/proc/device-tree/hat/product`). En el primer
  arranque de una imagen recién grabada, sin placa guardada, `main.py` la
  reconoce, aplica `voicehat_pi3` con `storymaker-perfil.sh` y reinicia una vez:
  así el altavoz tiene driver y la caja puede decir a qué red conectarse desde
  el principio. La PCB del proyecto no tiene EEPROM y sigue el camino normal.
- **Sin placa elegida** (imagen recién grabada y ningún HAT reconocido) el
  firmware no toca ni el botón ni el LED: GPIO23 cambia de sentido entre las dos
  placas, y ponerlo en alto como LED con el botón del HAT pulsado lo
  cortocircuitaría a masa.
- **Rescate AP con el botón al arrancar:** lo hace `storymaker-wifi.sh`, como
  root y antes del servicio, leyendo GPIO23 si reconoce el HAT (por su EEPROM o
  por la placa guardada) y GPIO5 en la PCB. El botón se mantiene pulsado desde
  el encendido; `main.py` solo da la señal del LED. Antes lo intentaba
  `main.py`, pero el servicio corre como `storymaker` y polkit no le deja
  cambiar de red.
- **Contraseña WiFi errónea en el primer arranque:** el AP cae unos 5 s y el
  portal cautivo lo reactiva renovando `/run/storymaker-ap-mode`. El modo de
  configuración de `main.py` vigila esa marca y repite el aviso por voz (sin
  tique ni e-ink). Los avisos usan los clips de `data/voz/`, que suenan sin
  internet: en modo AP edge-tts no puede funcionar.
- **Raspberry Pi 3 Model B (sin «+»):** su WiFi solo ve redes de 2,4 GHz.
- **Dictado de la dirección:** sin e-ink ni impresora, la caja dice por voz el
  AP al que conectarse o su IP con el puerto 5000, cada vez que cambia la red
  (`modules/anuncio_red.py`). Si una premisa está sonando, el aviso espera.
  Suena con clips de Elvira grabados de antemano en `firmware/data/voz/`
  (`firmware/deploy/generar_voz.py`, que se ejecuta en el PC); si falta alguno,
  lo dice con espeak.

### Problemas encontrados

- **La tarjeta del HAT no aparece en `aplay -l`.** Falta el overlay o la Pi no
  se ha reiniciado tras elegir la placa: `config.txt` debe acabar con el bloque
  `# >>> storymaker placa` y, tras reiniciar, `aplay -l` muestra `sndrpigooglevoi`.
- **`mpg123` muere con `SIGSEGV` y entra espeak.** `asound.conf` apunta a otra
  tarjeta: pasó en la Pi 3 con el de la PCB, cuyo `hw:0` es el jack.
- **Tras una contraseña WiFi errónea, la caja se queda sin red y sin AP.** Al
  probar la red, wlan0 suelta el AP y NetworkManager no lo recupera, porque su
  perfil no autoconecta. Afectaba también a la PCB. Ahora el portal cautivo lo
  reactiva y renueva `/run/storymaker-ap-mode`, y la caja vuelve a anunciarlo
  (el AP cae solo unos 5 s, demasiado poco para detectarlo sondeando).
- **espeak no se oye o da «Device or resource busy».** Abría la tarjeta
  directamente, que ya tenía abierta el dmix. Ahora sale por `plug:dmixed`.
