# Hardware

Placa base de la máquina: un *hat* para Raspberry Pi Zero 2W que reúne en un
solo circuito la Pi, el amplificador de audio, el cargador de batería y los
conectores de la pantalla, la impresora, el botón y el LED. Con ella no hay
que soldar cables a la Pi: cada periférico va a su conector, rotulado en la
serigrafía.

La versión publicada es la **v3**: 80 × 70 mm, dos caras y solo componentes
de agujero pasante, que se sueldan a mano.

---

## Muestrario

Pulsa una imagen para verla a tamaño completo.

| Montada | Placa y módulos |
|:-:|:-:|
| [<img src="../docs/galeria/hardware-01-montada.jpg" width="240" alt="Foto de la placa montada: la Raspberry Pi Zero 2W encima, el amplificador y el cargador insertados en sus zócalos, y las bornas verdes de tornillo">](pcb/imagenes/v3-foto-montada.jpg) | [<img src="../docs/galeria/hardware-02-piezas.jpg" width="240" alt="Foto de la placa con los conectores ya soldados, junto al amplificador, el cargador y la Raspberry Pi sueltos">](pcb/imagenes/v3-foto-piezas.jpg) |
| **Cara (render)** | **Dorso (render)** |
| [<img src="../docs/galeria/hardware-03-pcb-cara.jpg" width="240" alt="Render de la cara de la placa, con los conectores rotulados: audio, cargador, interruptor, entradas de alimentación, impresora, pantalla e-ink, botón, LED y la doble fila de pines de la Raspberry Pi">](pcb/imagenes/v3-cara.png) | [<img src="../docs/galeria/hardware-04-pcb-dorso.jpg" width="240" alt="Render del dorso de la placa, con los logotipos de los centros participantes, el nombre de la máquina y la dirección del repositorio">](pcb/imagenes/v3-dorso.png) |

Hay también una [vista 3D](pcb/imagenes/v3-3d.png) y el trazado de pistas de
cada cara en SVG, a escala 1:1: impreso al 100 %, sirve para comprobar el
tamaño y los taladros antes de encargarla
([cara](pcb/imagenes/v3-layout-cara.svg), [dorso](pcb/imagenes/v3-layout-dorso.svg)).

---

## Esquema

En [SVG](esquemas/v3-esquema.svg), para ampliarlo sin pixelar o imprimirlo.

[![Esquema eléctrico de la placa v3: la Raspberry Pi Zero 2W en el centro, con la pantalla e-ink, la impresora y el botón a la izquierda, el amplificador y las entradas de alimentación a la derecha, y el cargador y el puente J1 abajo](esquemas/v3-esquema.png)](esquemas/v3-esquema.png)

El mismo circuito en vista de montaje, con los módulos dibujados como son y
cada cable de un color según su función (en [SVG](esquemas/v3-croquis.svg)):

[![Croquis de montaje de la placa v3, con los módulos y la Raspberry Pi dibujados y los cables coloreados](esquemas/v3-croquis.png)](esquemas/v3-croquis.png)

> **C1 es de 1000 µF**, como dice la serigrafía. En el esquema y en el
> fichero de Fritzing figura como 1 µF: es el valor por defecto de la pieza.
> Va en la línea de 5 V, así que vale cualquier electrolítico de 10 V o más.

---

## Estructura

| Carpeta | Contenido |
|---|---|
| `esquemas/` | Esquema eléctrico y croquis de montaje, en PNG y SVG |
| `pcb/gerber/` | Lo que se manda a fabricar: el `.zip` con los Gerber y el fichero de taladros |
| `pcb/fritzing/` | El diseño editable, para abrirlo y modificarlo en Fritzing |
| `pcb/imagenes/` | Fotos de la placa real, renders de las dos caras, vista 3D y trazado de pistas en SVG |
| [`bom/`](bom/) | Lista de materiales por bloques, según las salidas y la alimentación *(borrador)* |

Los ficheros llevan la versión de la placa en el nombre (`v3`).

---

## Conectores

Los nombres son los de la serigrafía. GPIO en numeración BCM; entre
paréntesis, el pin físico de la Pi.

| Conector | Se conecta a | Pines |
|---|---|---|
| `E-INK LCD` | Pantalla e-ink WeAct de 4,2" | `Vcc 3,3V` (1) · `GND` · `RES` GPIO 17 (11) · `BUSY` GPIO 24 (18) · `D/C` GPIO 25 (22) · `SDA` GPIO 10 (19) · `CS` GPIO 8 (24) · `SCL` GPIO 11 (23) |
| `PRINTER` | Impresora térmica | `Tx` GPIO 14 (8), al RX de la impresora · `VIN` 5 V · `GND` |
| `AUDIO` | Amplificador MAX98357A (Adafruit 3006) | `VIN` 5 V · `GND` · `DIN` GPIO 21 (40) · `BCLK` GPIO 18 (12) · `LRC` GPIO 19 (35) |
| `PULS` | Botón | `P1` · `P2`: GPIO 5 (29) y GND, en cualquier orden |
| `LED` | LED de estado | `GND` · `Led+` GPIO 23 (16) |
| `CARGADOR` | Módulo cargador y elevador de batería de litio, 2 A / 5 V | `VOUT` · `GND` · `BAT` · `GND` · `GND` · `VIN` |
| `BAT/USB` | Alimentación principal: la batería o una fuente USB de 5 V, según `J1` | `+` · `−` |
| `USB` | Entrada de carga de la batería | `+` · `−` |
| `INT` | Interruptor de encendido | `S1` · `S2` |
| `J1` | Puente de selección del modo de alimentación | ver abajo |
| `INTERFAZ GPIO's RASPBERRY PI` | Todas las señales anteriores, más 5 V y GND, para medir o ampliar | `5V` · GPIO 14, 17, 18, 23, 24, 10, 25, 8, 11, 5, 19, 21 · `GND` |

La impresora solo recibe: la placa no cablea su TX de vuelta a la Pi. En el
amplificador, `SD` y `GAIN` quedan sin conectar, que es su configuración por
defecto, y salen a dos pads del dorso por si alguien quiere cambiarla.

### Alimentación y el puente J1

La alimentación entra por `BAT/USB`, pasa por el interruptor `INT` y llega a
`J1`, que decide adónde va:

| Posición de `J1` | Serigrafía | `BAT/USB` | `CARGADOR` | `USB` | Cómo funciona |
|---|---|---|---|---|---|
| Arriba | `BAT+CARG.` | La **batería** LiPo de una celda | Módulo MH-CD42 montado | Toma de carga | La batería va al cargador, que la eleva a 5 V para todo el circuito. Por `USB` se carga |
| Abajo | `SÓLO USB` | Una **fuente USB de 5 V** o la salida de un powerbank | Vacío | Vacío | Los 5 V van directos al circuito |

Qué comprar para cada opción, en la [lista de materiales](bom/).

> **Pon `J1` antes de conectar nada.**
>
> - Con el puente arriba, `BAT/USB` va al pin de batería del cargador: una
>   fuente de 5 V ahí puede dañarlo.
> - Con el puente abajo, una LiPo quedaría conectada directamente a los 5 V,
>   sin pasar por el cargador.

- **Respeta la polaridad.** La placa no tiene fusible ni diodo de protección:
  con `J1` abajo, `BAT/USB` llega directo al raíl de 5 V que alimenta la Pi.
- **Con `J1` abajo, no montes el cargador.** Su salida está siempre unida al
  raíl de 5 V.
- **Para cargar la LiPo, el interruptor tiene que estar cerrado.** `INT` está
  entre la batería y el cargador; abierto, la batería queda desconectada.

---

## Fabricar la placa

El `.zip` de [`pcb/gerber/`](pcb/gerber/) se sube tal cual a cualquier
servicio de fabricación de PCB (JLCPCB, PCBWay, Aisler…), sin descomprimirlo.
El servicio detecta solo el tamaño y las capas. Lo demás se puede dejar con
los valores habituales:

| Opción | Valor |
|---|---|
| Capas | 2 |
| Medidas | 80 × 70 mm |
| Grosor | 1,6 mm |
| Taladros | Los más pequeños, 0,4 mm (vías) |
| Color de la máscara | El que quieras; los renders son azules |
| Acabado | HASL, el más común |

El `.zip` incluye también un fichero de colocación (`_pnp.xy`) que genera
Fritzing. No hace falta: todos los componentes son de agujero pasante y la
placa se encarga sin montaje.

Antes de pedirla, conviene repasar la vista previa que muestra el propio
servicio al subir el `.zip`: deben verse las dos caras como en el muestrario.

---

## La Raspberry Pi va encima

La Pi se pincha **encima** de la placa, con sus componentes hacia arriba, como
en la foto de la placa montada. Para eso, el conector de 40 pines tiene que ir
soldado **por debajo** de la Pi, al revés de lo habitual.

> **Compra una Raspberry Pi Zero 2W sin pines (no la «WH»).** La Zero 2 WH
> viene con el conector ya soldado por arriba y no sirve: dada la vuelta para
> pincharla, los pines quedan invertidos.

---

## Editar el diseño

La placa está diseñada en **Fritzing** 1.0.8. El fichero
[`storymaker_pcb_v3.fzz`](pcb/fritzing/storymaker_pcb_v3.fzz) lleva dentro
las piezas que no vienen con el programa (el amplificador y el cargador), así
que se abre sin instalar nada más.

Fritzing es software libre. En Linux está en los repositorios de muchas
distribuciones y en Flathub; en su web oficial, la descarga de los binarios
pide una aportación.

Para volver a fabricar después de un cambio: *File → Export → for
Production → Extended Gerber*, y comprimir en un `.zip` los ficheros que
genera.

> La serigrafía de la cara dice «Storymaker board **V2.0**», en la esquina
> derecha. Es una errata: esta es la v3.

---

## Licencia

Este directorio se publica bajo la
**CERN Open Hardware Licence v2 — Strongly Reciprocal**
([`CERN-OHL-S-2.0`](LICENSE)). Puedes fabricar, modificar y distribuir la
placa, también con fines comerciales, siempre que publiques las fuentes de lo
que derives bajo la misma licencia y conserves los avisos de autoría.

Los **logotipos** de la serigrafía (Atrapavientos, IES Pablo Serrano,
IES Virgen del Pilar, IES Pilar Lorengar y CIFPA) pertenecen a sus
titulares y no entran en esa licencia. Si derivas tu propia placa, puedes
quitarlos.

Las piezas de Fritzing de terceros que van dentro del `.fzz` conservan su
autoría; ver [`CREDITS.md`](../CREDITS.md).
