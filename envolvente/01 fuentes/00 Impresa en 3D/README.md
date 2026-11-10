# Fuentes de la caja impresa en 3D

La caja impresa en 3D y sus accesorios se diseñaron en **Tinkercad**, un
programa de CAD que funciona en el navegador y guarda los diseños en la nube.

Tinkercad no tiene un formato de archivo propio que se pueda descargar: solo
exporta mallas (STL, OBJ) y contornos (SVG). Por eso aquí no hay fichero nativo,
y la forma editable del diseño son los propios STL de
[`02 producción/00 Impresa en 3D/stl/`](../../02%20producci%C3%B3n/00%20Impresa%20en%203D/stl/).

## Modificar una pieza

- **En Tinkercad.** Crea un diseño nuevo, pulsa *Importar* y elige el STL. Entra
  como una sola pieza sólida, a la que puedes sumar formas o restarle huecos
  como a cualquier otra. El límite de importación es de 25 MB; el mayor de
  estos ficheros, `accesorios.stl`, pesa unos 14 MB.
- **En FreeCAD.** Abre el STL con el banco de trabajo *Mesh* y conviértelo en
  sólido con *Part › Crear forma desde malla* y *Part › Convertir a sólido*.
  A partir de ahí admite operaciones booleanas con otras piezas.
- **En cualquier otro programa** que lea STL (Blender, Fusion, OnShape…),
  importándolo como malla.

Los STL están en milímetros.

## Licencia

Este diseño se publica bajo la
**CERN Open Hardware Licence v2 — Strongly Reciprocal**
([`CERN-OHL-S-2.0`](../../LICENSE)), como el resto de la envolvente. Si
publicas una versión modificada, hazlo bajo la misma licencia y conserva los
avisos de autoría.
