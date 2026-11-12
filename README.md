# La asombrosa máquina de generar historias

<!-- PENDIENTE imagen portada-00-taller.jpg: la máquina en uso en un taller,
     con gente alrededor o tiques pegados en cuadernos. Cuando exista,
     sustituye a la foto de abajo, que pasa a la tira. -->
<img src="docs/galeria/despliegue-00-dispositivo.jpg" width="560" alt="La máquina terminada: una caja cúbica turquesa con un pulsador y la rejilla del altavoz arriba, y en el frontal una pantalla de tinta electrónica mostrando el arranque de una historia">

**Pulsas un botón y la máquina te da el arranque de una historia. Tú tienes
que continuarla.**

Es un aparato para talleres de escritura y fomento de la lectura. Lo ha hecho
la asociación Atrapavientos con alumnado y profesorado de FP de tres
institutos de Zaragoza, y en este repositorio está todo lo necesario para
construir una: el programa, la placa, las cajas y los manuales.

> **¿Has llegado aquí escaneando un QR?** Es el de la máquina, el que sale al
> apagarla o en el tique de despedida. Estás en el sitio correcto.

| | | | |
|:-:|:-:|:-:|:-:|
| <img src="docs/galeria/artes-02-arcade.jpg" width="180" alt="Caja de cartón decorada como una máquina recreativa"> | <img src="docs/galeria/usuario-03-tique.jpg" width="180" alt="Tique recién impreso con una premisa"> | <img src="docs/galeria/usuario-02-eink-premisa.jpg" width="180" alt="Pantalla de tinta electrónica con una premisa"> | <img src="docs/galeria/usuario-05-panel-movil.png" width="100" alt="Panel de control de la máquina en un móvil"> |
| Una caja cualquiera... | ...que imprime historias | o las muestra en pantalla | y se maneja desde el móvil |

<!-- PENDIENTE imagen portada-01-familia.jpg: las cajas juntas (cartón,
     impresa en 3D, madera y acrílico, las que se tengan a mano). Iría aquí,
     bajo la tira, o sustituyendo la primera foto de la tira. -->

---

## ¿Qué quieres hacer?

### Ya tengo una máquina y quiero usarla en clase

Enchúfala, espera a que el LED se quede fijo y pulsa el botón. Todo lo demás,
cambiar las frases, preparar un perfil para cada grupo o apagarla bien, está
en el **[manual de usuario](docs/manuales/usuario.md)**. No hace falta saber
nada de informática.

### Quiero construir una

En este orden:

1. **Decide qué salidas quieres.** Pantalla de tinta electrónica, impresora de
   tiques y altavoz. Las tres son opcionales e independientes; con una basta.
2. **Compra el material.** La [lista de materiales](hardware/bom/README.md)
   va por bloques, según las salidas y la alimentación que elijas. Está en
   borrador, pero ya sirve para hacer la compra.
3. **Encarga la placa y suéldala.** Los ficheros de fabricación y las
   instrucciones están en [`hardware/`](hardware/README.md). Todo es de
   agujero pasante, para soldar a mano.
4. **Fabrica la caja.** [Impresa en 3D, de madera o de
   acrílico](envolvente/README.md), o [de cartón con uno de los seis
   diseños](artes-graficas/README.md).
5. **Graba la tarjeta y configura la máquina.** El [manual de
   despliegue](docs/manuales/despliegue.md), Ruta A, lo hace en unos veinte
   minutos sin tocar una terminal.

<!-- PENDIENTE: coste orientativo de una máquina completa y de la mínima,
     cuando el BOM tenga precios. Iría aquí, en una frase. -->

### Quiero entender cómo funciona o modificarla

- El programa: [`firmware/`](firmware/README.md), en Python, y [por qué está
  hecho así](docs/decisiones.md).
- La placa: [editar el diseño](hardware/README.md#editar-el-diseño) en
  Fritzing.
- Instalar desde el código, actualizar una máquina o generar una imagen
  nueva: [manual de despliegue](docs/manuales/despliegue.md), Ruta B, y
  [`docs/desarrollo.md`](docs/desarrollo.md).

---

## Cómo es por dentro

Una Raspberry Pi Zero 2W sobre una placa propia que reúne las conexiones de
la pantalla, la impresora, el altavoz, el botón y la batería. El programa
combina tres listas de frases (cómo empieza, quién es el protagonista, qué le
pasa) y manda el resultado a las salidas que tengas. Las listas se editan
desde el móvil, sin internet.

También funciona, solo con voz, en una Raspberry Pi 3 con el Voice HAT de
Google (kit AIY V1), sin placa ni soldaduras.

> **Estado:** firmware, documentación, placa, artes gráficas y envolventes
> publicados; lista de materiales en borrador.

---

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `docs/` | Manuales, referencia técnica y galería de imágenes |
| `firmware/` | Código Python que corre en el dispositivo, y los scripts de instalación |
| `hardware/` | Placa base: esquema, Gerber para fabricarla, diseño editable en Fritzing y lista de materiales |
| `envolvente/` | Caja impresa en 3D en siete versiones, con sus accesorios, y cajas de madera y acrílico para corte láser (IES Virgen del Pilar) |
| `artes-graficas/` | Diseños de la caja de cartón: troqueles, fuentes de Illustrator, PDF para imprimir y fotos de prototipos (IES Pilar Lorengar) |

## Descargas

La imagen de tarjeta lista para grabar se publica en la sección **Releases**,
con su checksum SHA256. No va dentro del repositorio: pesa cerca de 1 GB.

## Licencias

Código → GPLv3 · hardware → CERN-OHL-S v2 · documentación y arte →
CC BY-SA 4.0. Detalle en [`README.licensing.md`](README.licensing.md).

## Créditos

Ver [`CREDITS.md`](CREDITS.md).

## Dudas y contacto

- **Incidencias** de este repositorio, para errores y propuestas que puedan
  servir a más gente.
- **Correo:** profektor@tuta.com, para lo demás.
