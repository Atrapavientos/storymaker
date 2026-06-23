# ARRANQUE — Construir el esqueleto del repositorio público

> **Tarea para Claude Code.** Objetivo: dejar este repositorio con su estructura completa,
> sus licencias y sus READMEs, navegable y listo para ir poblando.
>
> **Alcance de esta tarea:** SOLO el esqueleto + placeholders. **No** migrar todavía código
> ni contenido real (eso vendrá en tareas posteriores).

## Reglas de ejecución
1. No inventes contenido para `envolvente/` ni `artes-graficas/`: son material de centros
   externos. Crea solo su `README.md` placeholder.
2. Crea un fichero vacío `.gitkeep` en cada carpeta que quede sin archivos, para que git la versione.
3. Las licencias deben ser el **texto oficial íntegro**, descargado de su fuente canónica.
   Nunca un resumen ni texto reconstruido de memoria.
4. **No hagas `git commit` ni `git push`.** Al terminar, muestra el árbol y déjalo para revisión manual.

---

## 1. Descargar las licencias (texto íntegro y oficial)

| Destino | Licencia | SPDX | Fuente |
|---|---|---|---|
| `/LICENSE` | GNU GPL v3 | `GPL-3.0-or-later` | https://www.gnu.org/licenses/gpl-3.0.txt |
| `/hardware/LICENSE` | CERN-OHL-S v2 | `CERN-OHL-S-2.0` | Sitio oficial del CERN (ohwr.org) o spdx.org/licenses/CERN-OHL-S-2.0 |
| `/docs/LICENSE` | CC BY-SA 4.0 | `CC-BY-SA-4.0` | https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt |

Para CERN-OHL-S v2, verifica que descargas la **versión 2 "Strongly Reciprocal" íntegra**.
Si alguna descarga falla, crea el fichero con el texto `PENDIENTE: pegar texto oficial de <licencia> (SPDX: <id>)` y avísame al final.

---

## 2. Estructura de carpetas a crear

```
.
├── README.md
├── LICENSE
├── README.licensing.md
├── CREDITS.md
├── CHANGELOG.md
├── .gitignore
├── hardware/
│   ├── LICENSE
│   ├── README.md
│   ├── bom/.gitkeep
│   ├── pcb/
│   │   ├── kicad/.gitkeep
│   │   └── jlcpcb/.gitkeep
│   └── esquemas/.gitkeep
├── firmware/
│   └── README.md
├── envolvente/
│   └── README.md
├── artes-graficas/
│   └── README.md
└── docs/
    ├── LICENSE
    ├── README.md
    ├── troubleshooting.md
    ├── manuales/.gitkeep
    └── galeria/.gitkeep
```

---

## 3. Contenido de cada fichero

### `/README.md`
Portada del proyecto. Incluye, en este orden:
- Título: **La asombrosa máquina de generar historias**
- Una línea de qué es: dispositivo educativo de hardware y software libre, basado en Raspberry
  Pi Zero 2W, que genera premisas narrativas aleatorias (detonante + protagonista + conflicto)
  para talleres de fomento de la lectura, con salida por pantalla e-ink, impresora térmica y audio.
- **Estado:** en preparación. Repositorio de publicación curada; el desarrollo vive aparte.
- **Estructura:** breve descripción de cada carpeta de primer nivel.
- **Licencias:** remitir a `README.licensing.md` (código GPLv3, hardware CERN-OHL-S v2, docs/arte CC BY-SA 4.0).
- **Créditos:** remitir a `CREDITS.md`.
- Nota: el codename técnico interno es *StoryMaker*.

### `/README.licensing.md`
Tabla clara "qué carpeta → qué licencia" + una frase explicando que cada dominio tiene su
licencia copyleft propia. Incluye una nota: "Combinación pendiente de OK formal de Atrapavientos
(titular del proyecto)". `envolvente/` y `artes-graficas/` → "licencia a definir por el centro responsable".

### `/CREDITS.md`
Créditos del proyecto. Incluye (confirmar wording exacto con Héctor antes de publicar):
- **Creado por:** Asociación Atrapavientos (Zaragoza).
- **Proyecto de innovación en FP**, Gobierno de Aragón — Departamento de Educación, Cultura y Deporte.
- **Centros de FP participantes:** IES Pablo Serrano, IES Virgen del Pilar, IES Pilar Lorengar.
- **Con la colaboración de:** CIFPA (Centro de Innovación para la FP de Aragón) e IDEA FP.
- Sección **"Artes gráficas"**: placeholder — "Vinilos y decoraciones creados por la comunidad
  docente de [centro]. Pendiente de atribución y licencia definitivas."

### `/CHANGELOG.md`
Mínimo: encabezado y una entrada "Sin publicar — estructura inicial del repositorio".

### `/.gitignore`
Python (`__pycache__/`, `*.pyc`), logs (`*.log`), sistema (`.DS_Store`, `Thumbs.db`),
imágenes de SD (`*.img`, `*.img.xz`) para evitar que acaben en git por error.

### `/hardware/README.md`
Índice de la carpeta hardware. Explica que contendrá: BOM por versión (`bom/`), fuentes KiCad
y paquete listo para JLCPCB (`pcb/`), y esquemas eléctricos (`esquemas/`). Marca con `(pendiente)`
lo que aún no está. Indica que el hardware se licencia bajo CERN-OHL-S v2.

### `/firmware/README.md`
Placeholder: "El firmware se curará y trasplantará desde el repositorio de desarrollo
`storymaker_dev` (carpeta `firmware/`) una vez saneado. Código bajo GPLv3."

### `/envolvente/README.md`
Placeholder de terceros: "Archivos de las distintas versiones de caja (3D, madera/metacrilato
a láser, cartón a láser/CNC). Estructura y licencia a definir por el centro de CAD/diseño
responsable. Formato esperado: fuente + export (STEP+STL para 3D; SVG/DXF para corte láser),
anotando grosor de material y kerf."

### `/artes-graficas/README.md`
Placeholder de terceros: "Vinilos, decoraciones e ilustraciones imprimibles para las distintas
versiones de caja, creados por una comunidad docente. Estructura, créditos y licencia propia a
definir por el centro responsable."

### `/docs/README.md`
Índice de docs: manuales de montaje (físico, software, puesta en marcha), galería de fotos y
troubleshooting. Indica que la documentación se licencia bajo CC BY-SA 4.0.

### `/docs/troubleshooting.md`
Título "Errores conocidos / qué evitar". Incluye, en prosa con viñetas, exactamente estos puntos:
- **Driver e-ink:** usar la secuencia de init oficial **WeAct SSD1683**, nunca la de Waveshare/SSD1619.
- **SPI fragmentado a 4000 bytes** para evitar `OverflowError`.
- **GPIO:** solo `RPi.GPIO` con polling. Nunca `lgpio` ni `gpiozero` (incompatibilidades en Bookworm).
- **TTS:** Piper descartado — el runtime ONNX agota los 512 MB de RAM del Pi Zero 2W y provoca
  resets. Solución: edge-tts (online) con espeak como fallback offline.
- **Alimentación:** condensador 1000 µF low-ESR (105 °C, 10 V) en los pines de alimentación
  resuelve resets en picos de corriente; complementar con cerámicas 100 nF–10 µF cerca del Pi.
- **Perfil AP WiFi:** crear con `nmcli` sin parámetros `wifi-security`.
- **`storymaker-wifi.sh`:** usar `set -uo pipefail` (sin `-e`) y aislar los `grep` con `|| true`.
- **Portal cautivo (timing):** el flag `/run/storymaker-ap-mode` debe crearse antes de evaluar
  `ConditionPathExists`. El orden de arranque importa.
- **Concurrencia JSON:** escrituras a `config.json` con lock de threading + escritura atómica.
- **Pulsación larga del botón:** flag `_largo_procesado` para que no se dispare el callback corto al soltar.

---

## 4. Al terminar
- Ejecuta `git status` y muestra el árbol resultante.
- Reporta si alguna licencia no se pudo descargar.
- **No commitees.** Lo reviso y commiteo a mano (esta primera vez, para aprender el flujo).
