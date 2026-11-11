# Changelog

## v2026-11-11 — imagen distribuible

Release [`v2026-11-11`](https://codeberg.org/atrapavientos/storymaker/releases/tag/v2026-11-11),
con la imagen de tarjeta y su checksum SHA256. Probada en una Raspberry Pi 3
con el Voice HAT y en una Zero 2W con la placa del proyecto.

### Firmware

- **El Voice HAT se reconoce solo** por su EEPROM en el primer arranque: se
  aplica su placa y la caja se reinicia una vez, así que el altavoz del HAT
  suena desde el principio.
- **El aviso del primer arranque suena con la voz de Elvira** también sin
  internet (clips de `data/voz/`). En modo punto de acceso no hay red y antes
  salía siempre con espeak.
- **Contraseña WiFi errónea en el portal cautivo:** la caja repite por voz el
  aviso del punto de acceso (sin tique ni e-ink).
- **Rescate con el botón al arrancar en el Voice HAT:** lo hace ya
  `storymaker-wifi.sh` para las dos placas. Antes lo intentaba el servicio, que
  no tiene permiso para cambiar de red, y nunca funcionó.
- Imagen: la limpieza devuelve `config.txt` y `asound.conf` a la placa del
  proyecto aunque la Pi de origen lleve el Voice HAT.

### Documentación

- Manuales: el rescate con el botón se mantiene desde el encendido hasta el
  parpadeo rápido (no «tres segundos»); el Voice HAT añade un reinicio al
  primer arranque y viene marcado en el asistente.
- `docs/hardware.md`: detección del HAT, rescate AP y aviso tras una contraseña
  errónea.

### Contenido del repositorio

- **Caja impresa en 3D** (`envolvente/`, modelo 00): siete versiones, una por
  combinación de salidas (e-ink, impresora y altavoz), y un juego de
  accesorios común: tapa inferior, tornillos y tuercas, patas para la placa
  base y el powerbank, llave de patas, marco del e-ink, rejillas para
  altavoz de 40 y 78 mm y soporte de Pi Zero. En STL y como proyecto de Bambu
  Studio (3MF) con una placa por versión, con parámetros de impresión
  orientativos. Diseñada en Tinkercad.
- La caja impresa en 3D pasa a ser el modelo de base; madera y acrílico se
  renumeran como 01 y 02 (`01 Madera/`, `02 Acrílico/`).

---

## v2026-11-07 — imagen distribuible (retirada)

Sustituía a `v2026-10-03`, que dejaba mudas las cajas con altavoz (edge-tts
7.2.8, rechazado por Microsoft). Checksum `19ba8a48…de7c`. **Retirada el
2026-11-11** al publicarse `v2026-11-11`: aquí solo se mantiene la release más
reciente.

### Firmware

- La voz vuelve a sonar: edge-tts 7.3.1, espeak por `plug:dmixed` cuando no hay
  red, y paso a espeak en 2 s si no se llega al servidor de voz. `deploy.sh`
  actualiza edge-tts en cada despliegue.
- El panel de control muestra cada premisa generada a toda página mientras está
  visible, venga del botón físico o del web.
- Soporte del **Voice HAT de Google (kit AIY V1) con Raspberry Pi 3**, elegible
  en el asistente (`storymaker-perfil.sh` cambia overlay y `asound.conf`). Solo
  con altavoz, la caja dicta el AP o su IP con avisos pregrabados.
- Tras una contraseña WiFi errónea, el punto de acceso de configuración vuelve.
- Perfil de serie `1eso` renombrado `juvenil`, con migración automática en las
  cajas actualizadas.
- Guardar el hardware en el portal ya no imprime dos QR: solo un tique de
  prueba al activar la impresora o cambiar su baudrate.
- Tipografías Lora e Inter servidas por la propia caja (`firmware/static/fuentes/`,
  OFL 1.1), sin Google Fonts.
- Contraseña del dispositivo: mínimo 6 caracteres.
- Imagen: las dos rutas de limpieza dejan las salidas apagadas, y la imagen
  lleva los perfiles del repositorio, no los de la Pi usada para capturarla.

### Documentación

- `docs/hardware.md`: Voice HAT, diagnóstico de «la caja no suena» y QR204.
- `docs/sistema.md`: ficheros del cambio de placa y su funcionamiento.
- Manuales: la premisa en pantalla, el bloque «Placa» del asistente y el mínimo
  de la contraseña.

### Contenido del repositorio

- **Firmware completo**, trasplantado desde el repositorio de desarrollo:
  código Python, módulos de hardware, portal web, perfiles de ejemplo y
  scripts de instalación y de creación de imagen.
- **Manual de despliegue e instalación** (`docs/manuales/despliegue.md`): las
  dos rutas de instalación, actualización de dispositivos y generación de la
  imagen distribuible.
- **Manual de usuario** (`docs/manuales/usuario.md`): botón, LED, panel de
  control, perfiles, importación de premisas y dudas frecuentes.
- Referencia técnica: `docs/hardware.md`, `docs/sistema.md`,
  `docs/decisiones.md`.
- **Artes gráficas** (`artes-graficas/`), del IES Pilar Lorengar: troqueles de
  la caja de cartón y seis modelos (Alicia, Arcade, Steampunk, Historia
  interminable, Jules Verne y Zootropo), con fuentes `.ai`, PDF para imprimir
  y fotos de los prototipos.
- **Envolvente** (`envolvente/`), del IES Virgen del Pilar: cajas de madera
  y acrílico para corte láser (DXF e IGES); la de acrílico, con sus bisagras,
  esquineras y marcos para impresión 3D (STL, IGES y fuentes de Inventor).
  Modelos y vídeos del montaje. Las siete versiones de la caja impresa en 3D
  llegarán aparte.
- **Placa base v3** (`hardware/`): esquema eléctrico y croquis de montaje
  (PNG y SVG), Gerber listos para fabricar, diseño editable en Fritzing,
  fotos de la placa real, renders, trazado de pistas a escala 1:1 y tabla de
  conectores con su GPIO. El BOM llegará aparte.
- **Impresora QR204 TTL+USB** probada como alternativa a la QR701: funciona
  sin cambios en el firmware, conectada por TTL a 9600 bps.

### Notas del repositorio

- Estructura inicial del repositorio: esqueleto de carpetas, licencias y
  READMEs.

---

## v2026-10-03 — imagen distribuible (retirada)

Primera release publicada desde este repositorio, con la imagen de tarjeta y su
checksum SHA256 (`90a1be92…98f7`). La imagen se generó el 3 de octubre desde el
repositorio de desarrollo, con el firmware de este árbol idéntico byte a byte.

**Retirada el 2026-11-07**, al publicarse `v2026-11-07`: su edge-tts (7.2.8) ya
no funciona y las cajas con altavoz se quedaban mudas. Aquí solo se mantiene
la release más reciente.

Desde el 2026-10-05, **Codeberg y este repositorio son el único sitio de
descarga**: el repositorio de desarrollo pasó a privado.
