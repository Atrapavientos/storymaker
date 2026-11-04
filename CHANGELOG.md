# Changelog

## v2026-10-03 — imagen distribuible

Primera release publicada desde este repositorio:
[`v2026-10-03`](https://codeberg.org/atrapavientos/storymaker/releases/tag/v2026-10-03),
con la imagen de tarjeta y su checksum SHA256.

La imagen se generó el 3 de octubre desde el repositorio de desarrollo. El
firmware de este árbol es idéntico byte a byte al que lleva dentro, de modo que
el tag corresponde de verdad a lo que se descarga.

Qué trae la imagen, en las [notas de la
release](https://codeberg.org/atrapavientos/storymaker/releases/tag/v2026-10-03).

Desde el 2026-10-05, **Codeberg y este repositorio son el único sitio de
descarga**: el repositorio de desarrollo pasó a privado.

---

## Sin publicar (contenido del repositorio)

### Añadido

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
  la caja de cartón y cinco modelos (Alicia, Arcade, Historia interminable,
  Jules Verne y Zootropo), con fuentes `.ai`, PDF para imprimir y fotos de los
  prototipos. Steampunk llegará aparte.
- **Envolvente** (`envolvente/`), del IES Virgen del Pilar: cajas de madera
  y acrílico para corte láser (DXF e IGES); la de acrílico, con sus bisagras,
  esquineras y marcos para impresión 3D (STL, IGES y fuentes de Inventor).
  Modelos y vídeos del montaje. Las siete versiones de la caja impresa en 3D
  llegarán aparte.

### Notas

- Estructura inicial del repositorio: esqueleto de carpetas, licencias y
  READMEs.
