# StoryMaker — Repositorio de publicación

**La asombrosa máquina de generar historias** — recursos abiertos para que cualquiera
pueda replicar el dispositivo (código, hardware, envolventes, artes gráficas, manuales).

Este repo **NO es un sandbox de desarrollo**: es el repositorio de **publicación curada**.
El desarrollo activo vive en `storymaker_dev`. Aquí solo entra material revisado y saneado.

## Reglas de oro
- **Nada se commitea sin sanear.** Cero secretos: claves SSH, contraseñas, tokens, PSK de
  WiFi, logs, rutas personales o datos de la asociación. Ante la duda, no subir.
- El material se **cura desde `storymaker_dev`**; no se desarrolla aquí.
- Las imágenes de SD **no van en git**: se publican como **Release asset** con checksum SHA256.
- No inventar contenido para `envolvente/` ni `artes-graficas/`: son de centros externos.
- Mantener este `CLAUDE.md` corto. El detalle va en `docs/`.

## Licencias (una por tipo de material)
- Código → **GPLv3** → `/LICENSE`
- Hardware (PCB, esquemas) → **CERN-OHL-S v2** → `/hardware/LICENSE`
- Docs, manuales → **CC BY-SA 4.0** → `/docs/LICENSE`
- Artes gráficas → **CC BY-SA 4.0**, salvo elementos de terceros → `/artes-graficas/LICENSE`

Resumen en `/README.licensing.md`. **Pendiente: OK formal de Atrapavientos** antes de publicar.

## Estructura
`hardware/` · `firmware/` · `envolvente/` · `artes-graficas/` · `docs/`
(`envolvente/` y `artes-graficas/` las definen centros externos.)

`firmware/`, `docs/` y `artes-graficas/` tienen contenido real (en artes falta el
modelo Steampunk). `envolvente/` es un placeholder y `hardware/` sigue vacío.

Lo que llega de los centros se sanea antes de entrar: rutas de usuario en el
XMP de PDF y `.ai`, EXIF y GPS en las fotos, nombres en Unicode NFC.

## Referencia
- `hoja-de-ruta.md` — qué falta por publicar y en qué orden
- `docs/README.md` — índice de la documentación
- `docs/troubleshooting.md` — errores conocidos / qué evitar

## Nombre
Público: *La asombrosa máquina de generar historias*. Codename técnico interno: **StoryMaker**.
