# Hoja de ruta del repositorio

Qué hay publicado, qué falta y en qué orden toca hacerlo. Este fichero es el
índice de trabajo del repositorio público: cuando algo se completa, se marca
aquí.

El desarrollo del firmware no se planifica aquí, sino en el repositorio de
desarrollo. Esto es sólo **qué le falta a la publicación**.

---

## Estado por carpeta

| Carpeta | Estado | Qué falta |
|---|---|---|
| `firmware/` | ✅ Publicado | — |
| `docs/` | 🟡 Parcial | Capturas, manual de montaje físico |
| `hardware/` | ⬜ Vacío | BOM, esquemas, PCB |
| `envolvente/` | ⬜ Externo | Lo define el centro de CAD |
| `artes-graficas/` | ⬜ Externo | Lo define el centro responsable |
| *Releases* | ⬜ Sin publicar | La imagen distribuible todavía no cuelga de este repositorio |

---

## 1. Documentación

### Hecho

- [x] **Manual de despliegue e instalación** — [`docs/manuales/despliegue.md`](docs/manuales/despliegue.md).
      Cubre las dos rutas (imagen publicada y desde cero), la actualización de
      un dispositivo y la creación de imágenes.
- [x] **Manual de usuario** — [`docs/manuales/usuario.md`](docs/manuales/usuario.md).
      Botón, LED, panel de control, perfiles, importación y resolución de dudas.
- [x] Referencia técnica: `hardware.md`, `sistema.md`, `decisiones.md`,
      `troubleshooting.md`.

### Siguiente

- [ ] **Las capturas de los dos manuales.** Veintiséis en total, con su
      descripción y su nombre de fichero ya decididos en
      [`docs/galeria/README.md`](docs/galeria/README.md). Es lo que más falta
      hace: sin ellas los manuales se siguen, pero cuestan el doble.
- [ ] **Manual de montaje físico.** Cableado paso a paso, montaje en la caja y
      comprobaciones antes de dar corriente. Depende de que haya una caja
      definitiva y de las fotos del proceso.
- [ ] **Guía rápida de una página**, imprimible, para dejar junto al aparato en
      el aula. Encender, generar, apagar, qué significa cada parpadeo del LED.

---

## 2. Hardware

- [ ] **BOM** (`hardware/bom/`) — lista de materiales por versión, con
      referencias y precio aproximado. Es lo primero que pide quien quiere
      replicarlo.
- [ ] **Esquemas eléctricos** (`hardware/esquemas/`) — el cableado está
      descrito en tablas en los manuales, pero hace falta el esquema dibujado.
- [ ] **PCB** (`hardware/pcb/kicad/` y `hardware/pcb/jlcpcb/`) — fuentes de
      KiCad y paquete de fabricación.
- [ ] Decidir dónde encaja el **STL del logo** que hay en el repositorio de
      desarrollo: ¿`hardware/`, `envolvente/` o `artes-graficas/`?

---

## 3. Material de terceros

Ni se inventa ni se rellena desde aquí: lo aportan los centros responsables.
Lo que sí toca es **pedirlo y acordar la licencia**.

- [ ] `envolvente/` — archivos de caja. Formato esperado: fuente + exportado
      (STEP y STL para impresión 3D; SVG o DXF para corte láser), anotando
      grosor de material y *kerf*.
- [ ] `artes-graficas/` — vinilos e ilustraciones, con sus créditos.
- [ ] Licencia de ambas carpetas, a definir por quien las aporte.

---

## 4. Publicación

- [ ] **Mover las releases a este repositorio.** La imagen distribuible se
      publica todavía desde el repositorio de desarrollo. Su sitio es éste, que
      es el que se enseña.
- [ ] **Confirmar los créditos.** [`CREDITS.md`](CREDITS.md) lleva una nota de
      pendiente y un `[centro]` sin rellenar en el apartado de artes gráficas.
- [ ] **Visto bueno formal de Atrapavientos** al esquema de licencias, como
      titular del proyecto. Es condición previa a anunciar el repositorio.
- [ ] **Decidir si el repositorio tiene espejo.** El de desarrollo lo tiene en
      GitHub; éste no. Un espejo ayuda a que lo encuentre quien busque allí.
- [ ] Rellenar el [`CHANGELOG.md`](CHANGELOG.md) con la primera versión
      publicable.

---

## 5. Pendiente de decidir

- **Idioma.** Todo está en castellano. Una traducción al inglés multiplicaría
  el alcance, pero también el trabajo de mantener dos versiones de cada
  manual. Conviene decidirlo antes de que los manuales crezcan más.
- **Dónde se responden las dudas.** Si el repositorio se anuncia, llegarán.
  ¿Incidencias de Codeberg, correo de la asociación, ninguna de las dos?
