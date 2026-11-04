# Envolvente

Archivos para fabricar la caja de la máquina, en tres variantes:

- **Madera**, de corte láser.
- **Acrílico**, de corte láser, con bisagras y esquineras impresas en 3D.
- **Impresa en 3D**, en siete versiones: una por cada combinación de salidas
  (pantalla e-ink, impresora térmica y altavoz), para que la caja lleve justo
  los huecos de lo que vayas a montar.

Las cajas de madera y acrílico son obra del alumnado y el profesorado del
**IES Virgen del Pilar** (Zaragoza). Las dos son un cubo de 160 mm con tapa
abatible; en la tapa van la ventana de la pantalla e-ink y el hueco del botón,
y en un lateral, dos orificios más.

| Variante | Qué hace falta para fabricarla |
|---|---|
| Madera | Cortadora láser y tablero |
| Acrílico | Cortadora láser, plancha de metacrilato e impresora 3D |
| Impresa en 3D | Impresora 3D |

Los troqueles de la **caja de cartón** no están aquí: van con sus diseños
gráficos en [`artes-graficas/`](../artes-graficas/README.md).

---

## Muestrario

Modelos de cada versión. Pulsa una imagen para verla a tamaño completo.

| Madera | Acrílico |
|:-:|:-:|
| [<img src="../docs/galeria/envolvente-01-madera.jpg" width="240" alt="Caja cúbica de tablero claro con uniones de dedos, tapa con ventana rectangular y agujero redondo, y dos discos de bisagra en el borde trasero">](03%20im%C3%A1genes/00%20Madera/ensamblaje.jpg) | [<img src="../docs/galeria/envolvente-02-acrilico.jpg" width="240" alt="Caja cúbica gris de paneles lisos encajados en ranuras, con la misma tapa de ventana rectangular y agujero redondo">](03%20im%C3%A1genes/01%20Acr%C3%ADlico/ensamblaje.jpg) |

Las siete versiones de la **caja impresa en 3D** se añadirán aquí cuando se
publiquen.

---

## Estructura

| Carpeta | Contenido |
|---|---|
| `01 fuentes/` | Ficheros editables del programa de CAD en que se diseñaron |
| `02 producción/` | Lo que va a la máquina: `dxf/` para cortar con láser, `stl/` para imprimir, y `iges/` con el modelo 3D de cada pieza |
| `03 imágenes/` | Modelos de cada pieza y del conjunto, y vídeos del montaje y del corte |

Dentro de cada una hay una subcarpeta por modelo, con el mismo número en las
tres. Cada pieza se llama igual en todas: `tapa.dxf`, `tapa.iges` y
`tapa.jpg` son la misma pieza.

---

## Modelos

| | Modelo | Fabricación | Estado |
|---|---|---|---|
| 00 | **Madera** | Corte láser en tablero de 2,6 mm, con uniones de dedos. La tapa gira sobre dos discos | ✅ |
| 01 | **Acrílico** | Paneles de corte láser en metacrilato de 3,2 mm, que se montan con bisagras y esquineras impresas en 3D | ✅ |
| 02 | **Impresa en 3D** | Impresión 3D, en siete versiones según las salidas | ⏳ Próximamente |

---

## Piezas

Medidas en milímetros, sacadas de los propios ficheros.

### 00 · Madera

| Pieza | Medidas | Cantidad | Notas |
|---|---|:-:|---|
| `suelo` | 160 × 160 | 1 | |
| `lado_a` | 160 × 160 | 1 | |
| `lado_a2` | 160 × 157,4 | 1 | |
| `lado_b` | 160 × 177,6 | 1 | Con la oreja y el eje de la bisagra (Ø 15) |
| `lado_b2` | 160 × 177,6 | 1 | Como `lado_b`, más dos orificios: Ø 12 y 19 × 13 |
| `tapa` | 161 × 162,4 | 1 | Ventana de la pantalla de 104 × 57 y hueco del botón de Ø 30 |
| `bisagra` | Ø 14,9 | 2 | Disco sobre el que gira la tapa |

### 01 · Acrílico

Paneles, para cortar con láser (`dxf/`):

| Pieza | Medidas | Cantidad | Notas |
|---|---|:-:|---|
| `base` | 160 × 160 | 1 | |
| `frontal_trasera` | 160 × 160 | 2 | Una para cada cara |
| `lateral` | 160 × 169 | 1 | Con la oreja de la bisagra y dos orificios: Ø 12 y rectangular |
| `lateral_2` | 160 × 169 | 1 | Con la oreja de la bisagra |
| `tapa` | 160 × 165 | 1 | Ventana de la pantalla de 104 × 57 y hueco del botón de Ø 30 |

Bisagras, esquineras y marcos, para imprimir en 3D (`stl/`). Las bisagras y
las esquineras son las que sujetan los paneles entre sí: sin ellas la caja no
se monta.

| Pieza | Medidas | Notas |
|---|---|---|
| `bisagra_tapa` | 78 × 14,5 × 8 | Bisagra de la tapa |
| `bisagra_tope` | 100 × 29 × 11 | Bisagra con tope. Montaje en `montaje_bisagra.jpg` |
| `esquinera_tope` | 24 × 20 × 20 | Esquinera con tope |
| `esquinera_tope_izq` | 24 × 20 × 20 | Variante izquierda |
| `esquinera_tope_dch` | 24 × 20 × 20 | Variante derecha |
| `marco_1` | 117 × 69 × 4 | Marco de la ventana de la pantalla |
| `marco_2` | Ø 23 × 4 | Aro |
| `marco_3` | 25 × 19 × 4 | Marco del orificio rectangular |
| `marco_4` | Ø 17 × 4 | Aro del orificio de Ø 12 |
| `placa` | — | Solo fuente, sin exportar a STL |

Los marcos también sirven para la caja de madera: su ventana y sus orificios
miden lo mismo.

---

## Cortar y montar

**Corte láser.** Los DXF están en milímetros, con todos los contornos en una
sola capa. Están dibujados para el espesor que indica la tabla de modelos: si
tu tablero o tu plancha miden otra cosa, las uniones no encajarán. Los
ficheros no indican compensación de *kerf* (el ancho de material que se
lleva el láser al cortar, unas décimas de milímetro), así que conviene cortar primero
una pieza pequeña y probar el encaje antes de lanzar el juego completo.

**Impresión 3D.** Los STL están en milímetros. No se acompañan de parámetros
de impresión.

En `03 imágenes/` hay vídeos del ensamblaje de las cajas de madera y
acrílico, pieza a pieza, y uno de la de madera cortándose.

---

## Editar los diseños

- Los **paneles de madera y acrílico** se diseñaron en Autodesk Fusion. Sus
  ficheros nativos no se han publicado; para modificar una pieza, importa su
  `.iges` o edita directamente el `.dxf`.
- Las **piezas impresas del acrílico** se diseñaron en Autodesk Inventor
  2025: sus fuentes son los `.ipt` de `01 fuentes/01 Acrílico/`.

Los `.iges` se abren en cualquier programa de CAD, también en programas
libres como **FreeCAD**, y los `.dxf` en **LibreCAD**, **Inkscape** o el
programa de la cortadora.

---

## Licencia

Este directorio se publica bajo la
**CERN Open Hardware Licence v2 — Strongly Reciprocal**
([`CERN-OHL-S-2.0`](LICENSE)), la misma que el resto del hardware del
proyecto. Puedes fabricar, modificar y distribuir estos diseños, también con
fines comerciales, siempre que publiques las fuentes de lo que derives bajo la
misma licencia y conserves los avisos de autoría.

Atribución sugerida:

> Diseño de las cajas de madera y acrílico: alumnado y profesorado del
> IES Virgen del Pilar, para
> *La asombrosa máquina de generar historias* (Asociación Atrapavientos).
> CERN-OHL-S-2.0.
