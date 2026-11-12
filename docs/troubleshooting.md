# Trampas encontradas en el desarrollo

Puntos críticos detectados al desarrollar el firmware, documentados para no repetirlos. Los problemas de uso están en los manuales.

- **Driver e-ink:** usar la secuencia de init oficial **WeAct SSD1683**, nunca la de
  Waveshare/SSD1619. Son incompatibles aunque el hardware parezca similar.

- **SPI fragmentado a 4000 bytes** para evitar `OverflowError` al transferir buffers
  de imagen completos al display.

- **GPIO:** solo `RPi.GPIO` con polling. Nunca `lgpio` ni `gpiozero`; presentan
  incompatibilidades en Bookworm que impiden el arranque limpio del servicio.

- **TTS:** Piper descartado — el runtime ONNX agota los 512 MB de RAM del Pi Zero 2W
  y provoca resets. Solución: edge-tts (online) con espeak como fallback offline.

- **Alimentación:** condensador 1000 µF low-ESR (105 °C, 10 V) en los pines de
  alimentación resuelve resets en picos de corriente; complementar con cerámicas
  100 nF–10 µF cerca del Pi.

- **Perfil AP WiFi:** crear el perfil con `nmcli` sin parámetros `wifi-security`
  (no usar `802-11-wireless-security`); de lo contrario NetworkManager rechaza el modo AP.

- **`storymaker-wifi.sh`:** usar `set -uo pipefail` (sin `-e`) y aislar los `grep`
  con `|| true` para evitar que una búsqueda vacía aborte el script.

- **Portal cautivo (timing):** el flag `/run/storymaker-ap-mode` debe crearse antes
  de que systemd evalúe `ConditionPathExists` en las unidades dependientes.
  El orden de arranque importa; revisar `After=` y `Requires=` en los `.service`.

- **Concurrencia JSON:** las escrituras a `config.json` deben ir protegidas con lock
  de threading y escritura atómica (escribir a `.tmp` y renombrar) para evitar
  corrupción si el proceso muere a mitad.

- **Pulsación larga del botón:** usar un flag `_largo_procesado` para que el callback
  de pulsación corta no se dispare al soltar después de una pulsación larga.
