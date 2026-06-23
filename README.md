# La asombrosa máquina de generar historias

Dispositivo educativo de hardware y software libre, basado en Raspberry Pi Zero 2W,
que genera premisas narrativas aleatorias (detonante + protagonista + conflicto)
para talleres de fomento de la lectura, con salida por pantalla e-ink, impresora
térmica y audio.

> **Estado:** en preparación. Este es el repositorio de publicación curada;
> el desarrollo activo vive en un repositorio separado (`storymaker_dev`).

Codename técnico interno: *StoryMaker*.

---

## Estructura

| Carpeta | Contenido |
|---|---|
| `hardware/` | Esquemas eléctricos, PCB (KiCad + JLCPCB) y BOM por versión |
| `firmware/` | Código Python que corre en el dispositivo |
| `envolvente/` | Archivos de caja (3D, corte láser); definidos por el centro de diseño externo |
| `artes-graficas/` | Vinilos e ilustraciones para la caja; definidos por el centro externo |
| `docs/` | Manuales de montaje, galería y troubleshooting |

---

## Licencias

Ver [`README.licensing.md`](README.licensing.md) para el detalle completo.

Resumen: código → GPLv3 · hardware → CERN-OHL-S v2 · documentación y arte → CC BY-SA 4.0.

---

## Créditos

Ver [`CREDITS.md`](CREDITS.md).
