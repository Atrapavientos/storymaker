# La asombrosa máquina de generar historias

Dispositivo educativo de hardware y software libre, basado en Raspberry Pi
Zero 2W, que genera premisas narrativas aleatorias
(detonante + protagonista + conflicto) para talleres de fomento de la lectura,
con salida por pantalla e-ink, impresora térmica y audio.

Pulsas un botón y sale el arranque de una historia que alguien tiene que
continuar.

> **¿Has llegado aquí escaneando un QR?** Es el de la máquina, el que sale al
> apagarla o en el tique de despedida. Estás en el sitio correcto: aquí está
> todo lo necesario para construir una.

> **Estado:** firmware y documentación publicados; hardware y envolventes en
> preparación. Ver la [hoja de ruta](hoja-de-ruta.md).
>
> Este es el repositorio de publicación curada; el desarrollo activo vive en un
> repositorio separado (`storymaker_dev`).

Codename técnico interno: *StoryMaker*.

---

## Por dónde empezar

| Si quieres... | Ve a |
|---|---|
| Montar y poner en marcha un dispositivo | [Manual de despliegue e instalación](docs/manuales/despliegue.md) |
| Usarlo en un taller | [Manual de usuario](docs/manuales/usuario.md) |
| Entender cómo está hecho el firmware | [`firmware/README.md`](firmware/README.md) y [`docs/decisiones.md`](docs/decisiones.md) |
| Replicar el hardware | [`docs/hardware.md`](docs/hardware.md) (los esquemas y el BOM están pendientes) |
| Echar una mano | [Hoja de ruta](hoja-de-ruta.md) |

---

## Estructura

| Carpeta | Contenido |
|---|---|
| `firmware/` | Código Python que corre en el dispositivo, y los scripts de instalación |
| `docs/` | Manuales, referencia técnica y galería de imágenes |
| `hardware/` | Esquemas eléctricos, PCB (KiCad + JLCPCB) y BOM por versión *(pendiente)* |
| `envolvente/` | Archivos de caja (3D, corte láser); los define un centro de diseño externo |
| `artes-graficas/` | Vinilos e ilustraciones para la caja; los define un centro externo |

---

## Descargas

La imagen de tarjeta lista para grabar se publica en la sección **Releases**,
con su checksum SHA256. No va dentro del repositorio: pesa cerca de 1 GB.

---

## Licencias

Ver [`README.licensing.md`](README.licensing.md) para el detalle completo.

Resumen: código → GPLv3 · hardware → CERN-OHL-S v2 · documentación y arte →
CC BY-SA 4.0.

---

## Créditos

Ver [`CREDITS.md`](CREDITS.md).
