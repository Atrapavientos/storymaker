# Galería

Imágenes que acompañan a la documentación: capturas de pantalla, fotos del
dispositivo y del montaje.

Licencia: **CC BY-SA 4.0** (ver [`../LICENSE`](../LICENSE)).

## Convención de nombres

```
<documento>-<NN>-<descripción-corta>.png
```

- `<documento>` — `despliegue`, `usuario`, `montaje`...
- `<NN>` — dos dígitos, en el orden en que aparecen en el texto
- Sin acentos, sin espacios, sin mayúsculas

Las capturas de pantalla en `.png`; las fotos, en `.jpg`.

Los manuales ya referencian estos nombres. En cuanto el fichero existe en esta
carpeta, basta con sustituir el bloque `> **📷 Captura pendiente — ...**` del
manual por:

```markdown
![Texto alternativo descriptivo](../galeria/nombre-del-fichero.png)
```

El texto alternativo no es decorativo: lo lee quien usa un lector de pantalla.
Describe **qué se ve**, no "captura de pantalla".

## Pendientes

Marca la casilla según las vayas haciendo.

### Manual de despliegue

- [ ] `despliegue-00-dispositivo.png` — El dispositivo terminado y encendido, de frente, con una premisa en la e-ink. Portada del manual
- [ ] `despliegue-01-cableado.png` — Cenital del cableado, con los tres periféricos conectados y la serigrafía legible
- [ ] `despliegue-02-release.png` — Página de la release en Codeberg con los dos adjuntos y la versión visible
- [ ] `despliegue-03-imager.png` — Raspberry Pi Imager con modelo, imagen personalizada y tarjeta seleccionados
- [ ] `despliegue-04-imager-no-personalizar.png` — El diálogo de personalización, señalando que la respuesta es *no*
- [ ] `despliegue-05-eink-bienvenida.png` — E-ink en el primer arranque, con el QR y la URL
- [ ] `despliegue-06-tique-bienvenida.png` — Tique de bienvenida impreso
- [ ] `despliegue-07-wifi-ap.png` — Lista de redes del móvil con `StoryMaker-Setup`
- [ ] `despliegue-08-captivo-redes.png` — Portal cautivo: lista de redes y campo de contraseña, en móvil
- [ ] `despliegue-09-captivo-exito.png` — Portal cautivo: pantalla de éxito con la URL del panel
- [ ] `despliegue-10-login.png` — Pantalla de acceso en el primer arranque, con el aviso del PIN inicial
- [ ] `despliegue-11-asistente.png` — Asistente de configuración inicial completo (o `-11a` hardware y `-11b` credenciales)
- [ ] `despliegue-12-panel.png` — Panel principal ya configurado
- [ ] `despliegue-13-prepare-sd.png` — Terminal con el resumen de `prepare_sd.sh` **(tapar el SSID si es una red real)**
- [ ] `despliegue-14-setup-final.png` — Comprobaciones finales de `setup_sd.sh`, todas en verde

### Manual de usuario

- [ ] `usuario-01-boton-led.png` — Frontal con el botón y el LED fijo encendido
- [ ] `usuario-02-eink-premisa.png` — E-ink con una premisa completa, sin reflejos
- [ ] `usuario-03-tique.png` — Tique impreso con una premisa
- [ ] `usuario-04-panel.png` — Panel principal en ordenador, con un perfil abierto
- [ ] `usuario-05-panel-movil.png` — El mismo panel en móvil
- [ ] `usuario-06-perfiles.png` — Barra lateral de perfiles junto al selector de perfil activo
- [ ] `usuario-07-editar.png` — Lista de detonantes con el campo de añadir y el botón de borrar
- [ ] `usuario-08-importar-1.png` — Primer paso del asistente de importación
- [ ] `usuario-09-importar-revision.png` — Pantalla de revisión del importador, con el recuento
- [ ] `usuario-10-hardware.png` — Pantalla ⚙ Hardware con los interruptores y el PIN
- [ ] `usuario-11-captivo.png` — Selección de red WiFi en el móvil

## Antes de subir una captura

Las capturas de un dispositivo real llevan dentro cosas que no quieres
publicar. Repasa:

- **Nombres de redes WiFi** reales, sobre todo las del centro o las de casa
- **Direcciones IP** de la red interna
- **El PIN y la contraseña** que hayas puesto, si se ven escritos
- **Códigos QR**: contienen la URL, que puede llevar una IP privada
- Nombres de usuario, rutas personales y pestañas abiertas del navegador

Lo más limpio es hacer las capturas sobre un dispositivo recién instalado y una
red creada para la ocasión.
