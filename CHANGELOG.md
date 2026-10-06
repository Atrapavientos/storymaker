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
- `docs/galeria/README.md` con la convención de nombres y la lista de capturas
  pendientes.
- `hoja-de-ruta.md`: estado del repositorio y orden de trabajo.

### Notas

- Los manuales llevan marcadas las capturas pendientes con bloques
  `📷 Captura pendiente`. Sustituirlos por la imagen al añadirla.
- Estructura inicial del repositorio: esqueleto de carpetas, licencias y
  READMEs.
