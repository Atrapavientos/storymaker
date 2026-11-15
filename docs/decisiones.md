# Decisiones técnicas

- GPIO con `RPi.GPIO` + polling software (sin lgpio, sin gpiozero, sin edge detection)
- SPI fragmentado a 4000 bytes para evitar `OverflowError`
- `eink.py` usa secuencia de inicialización SSD1683 WeAct oficial (no Waveshare)
- Audio TTS: `edge-tts` genera MP3 → `mpg123` reproduce
- `config_manager.py` usa lock + escritura atómica para evitar corrupción JSON concurrente
- Animación e-ink: `pluma.png` pre-renderizada al arrancar; se muestra mientras genera
- Portal web: slider volumen con debounce 400ms; restart servicio via `subprocess.Popen` con `start_new_session=True`
- `journald`: Storage=auto (volátil) — no saturar SD en producción
- Contraseña SSH por dispositivo: el asistente de primer arranque la exige y la
  aplica con el ayudante privilegiado `storymaker-setpass`
  - El problema que resuelve: la imagen distribuible es pública, así que la
    contraseña que lleve dentro es una credencial compartida por todas las
    unidades. Y con `NOPASSWD: ALL`, entrar por SSH era ser root directo: con
    eso se leen los `psk=` en claro de `/etc/NetworkManager/system-connections/`,
    o sea la clave WiFi de la red donde esté el aparato
  - Se eligió pedirla en `/setup` en vez de generarla y mostrarla en la e-ink,
    para que sea memorizable; el coste es que sobre el AP abierto viaja en claro
  - La contraseña va por *stdin* al ayudante, nunca como argumento (`ps`), el
    usuario está fijado dentro del script (no vale `sudo chpasswd` a secas) y la
    validación se repite en el script por ser la frontera de privilegio
  - `limpiar_*.sh` abortan si falta el ayudante o su línea de sudoers: una imagen
    sin ellos y sin `010_pi-nopasswd` dejaría el dispositivo inservible, porque
    el asistente no podría cumplir un requisito que es obligatorio
- Importación de premisas (`importador.py`): flujo de tres pantallas
  (formulario → revisión → confirmación) porque el usuario final no es técnico;
  nada se escribe hasta confirmar
  - Decodifica UTF-8/BOM y reintenta CP1252 y Latin-1: los .txt llegan de Word
    y del Bloc de notas de Windows
  - Deduplica sin distinguir mayúsculas ni espacios múltiples, pero **no** toca
    la puntuación: el `Generador` ya recorta la final al cargar
  - Copia `<tipo>.txt.bak` antes de escribir → botón «Deshacer» de un nivel
  - Las categorías que el usuario deja vacías no se tocan, ni en modo reemplazar
  - Avisa si una categoría quedaría a cero: el `Generador` lanza `ValueError`
    con una lista vacía y `main.py` se quedaría con el perfil anterior en silencio
  - Al importar sobre el perfil activo se recarga el `Generador` reutilizando
    `_callback_cambiar_perfil`; eso reinicia el contador de combinaciones y el
    portal lo avisa
  - Revisión pendiente en memoria (token + sesión, 15 min), no en campos ocultos:
    menos RAM y menos tráfico en la Pi Zero
  - `MAX_CONTENT_LENGTH` 3 MB; 5000 líneas y 300 caracteres por línea
- Actualizaciones menores desde el portal, sin regrabar la tarjeta
  (`modules/actualizador.py`, desde la `v1.0`). Antes, cualquier arreglo
  obligaba a grabar la imagen nueva en cada máquina y se perdían sus perfiles
  - **Versionado:** `firmware/VERSION`. El tercer número llega por
    actualización; cambiar el primero o el segundo es imagen nueva
  - **Qué cabe:** solo el firmware de `proyecto/`. Nunca `data/config.json` ni
    `data/perfiles/`, y tampoco ficheros de sistema ni paquetes, que el servicio
    no puede escribir sin root
  - **Firma Ed25519 verificada con `openssl`**, que ya trae Raspberry Pi OS: sin
    dependencias nuevas. Sin firma, el PIN de fábrica bastaría para meter código
    en la máquina a través del portal
  - **Dos caminos, un solo aplicador:** subir el fichero desde el panel (sin
    internet) o buscar en `actualizacion.json`, en la raíz del repositorio. La
    máquina mira una vez al día, pero **nunca instala sin que alguien pulse el
    botón**: no se actualiza en mitad de un taller
  - **Los paquetes cuelgan de la release de la imagen vigente:** aquí solo se
    mantiene la última release, y una release propia para la `v1.0.1` borraría
    la imagen `v1.0`
  - **La vuelta atrás vive fuera del firmware.** Un código actualizado no puede
    vigilarse a sí mismo: si viene roto, no llega a ejecutarse. El guardián
    `storymaker-arranque` es de root, no lo toca ninguna actualización y se
    ejecuta antes de cada arranque del servicio. `main.py` confirma la versión
    cuando el portal lleva 45 s en marcha; si no se confirma en 3 arranques, o
    la copia se cortó a medias, restaura la anterior
  - Antes de tocar nada se comprueban la firma, las rutas (sin `..`, sin
    enlaces, sin datos de la máquina), la versión y la sintaxis de todos los
    `.py`. La copia es fichero a fichero con `os.replace`, y `VERSION` va la
    última
  - Descartado: actualización de imagen completa en dos particiones (RAUC,
    Mender, SWUpdate). Obliga a reparticionar, pesa para la Zero 2W y, en el
    caso de Mender, necesita un servidor aparte

## Estructura interna de `firmware/`

Qué hace cada módulo y cada script, en [`../firmware/README.md`](../firmware/README.md).
