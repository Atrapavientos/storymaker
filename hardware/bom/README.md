# Lista de materiales

Todas las versiones de la máquina usan la misma PCB. Lo que cambia es qué se monta en ella y qué se conecta. La lista completa está en [`bom.csv`](bom.csv), organizada por bloques.

> Borrador: lo marcado como **PENDIENTE** está sin confirmar. Los precios y los proveedores están por completar.

## Cómo hacer tu lista de compra

### 1. Elige las salidas

Compra siempre el bloque `BASE` y añade los de las salidas que quieras:

| Versión | Bloques |
|---|---|
| Solo impresora | `IMP` |
| Solo altavoz | `AUD` |
| Solo pantalla | `PAN` |
| Impresora + altavoz | `IMP` + `AUD` |
| Impresora + pantalla | `IMP` + `PAN` |
| Altavoz + pantalla | `AUD` + `PAN` |
| Impresora + altavoz + pantalla | `IMP` + `AUD` + `PAN` |

### 2. Elige la alimentación

| Bloque | Alimentación | Con impresora | Sin impresora | Corriente mínima |
|---|---|---|---|---|
| `ALIM-CARG` | Cargador USB de 5 V | Sí | Sí | 2 A; 2,5 A con impresora |
| `ALIM-PB` | Powerbank de dos celdas 18650 | Sí | Sí | 2 A; 2,5 A con impresora |
| `ALIM-LIPO` | MH-CD42 + LiPo | **No** | Sí | Cargador de 2 A |

Una sola celda no cubre los picos de consumo de la impresora.

### 3. Suma los bloques

Junta las filas de los bloques elegidos en `bom.csv`. El bloque `OPC` es opcional.

## Configurar la alimentación

| En la PCB | Cargador USB o powerbank | MH-CD42 + LiPo |
|---|---|---|
| Jumper J1 | `SÓLO USB` | `BAT+CARG.` |
| Módulo `CARGADOR` | No se monta | Se monta |
| Borne `BAT/USB` | Cable USB externo o salida del powerbank | Batería |
| Borne `USB` | Vacío | Toma USB externa de carga |
| Borne `INT` | Interruptor | Interruptor |

```text
BAT/USB + ── INT ── J1 ─┬─ BAT+CARG. ── BAT del módulo ── salida del módulo ──┐
                        │                                                     ├── 5 V
                        └─ SÓLO USB ──────────────────────────────────────────┘

USB + ── VIN del módulo
```

### Avisos

- **No inviertas la polaridad.** La PCB no tiene fusible ni diodo de protección, y `BAT/USB` llega al raíl de 5 V que alimenta la Pi cuando J1 está en `SÓLO USB`.
- **Comprueba J1 antes de dar corriente.**
  - Con J1 en `BAT+CARG.`, los 5 V de un cargador entrarían por la entrada de batería del módulo y podrían dañarlo.
  - Con J1 en `SÓLO USB`, la LiPo quedaría conectada directamente al raíl de 5 V, sin pasar por el módulo.
- **No montes el MH-CD42 si J1 va en `SÓLO USB`.** Su salida está siempre unida al raíl de 5 V.
- **Para cargar la LiPo, el interruptor debe estar cerrado.** `INT` está entre la batería y el módulo; si está abierto, la batería queda desconectada.
- **Arranque con MH-CD42:** PENDIENTE: puente necesario para que arranque con el interruptor.

## Conexiones de la PCB

| Conector | Serigrafía | Señal |
|---|---|---|
| `PULS` | `P1` / `P2` | GND / GPIO5 |
| `LED` | `GND` / `Led+` | GND / GPIO23 |
| `PRINTER` | `VIN` / `GND` / `Tx` | 5 V / GND / GPIO14 |
| `AUDIO` | `VIN` / `GND` | 5 V / GND |
| `AUDIO` | `DIN` / `BCLK` / `LRC` | GPIO21 / GPIO18 / GPIO19 |
| `E-INK LCD` | `3,3V` / `GND` | 3,3 V / GND |
| `E-INK LCD` | `SDA` / `SCL` / `CS` | GPIO10 / GPIO11 / GPIO8 |
| `E-INK LCD` | `D/C` / `RES` / `BUSY` | GPIO25 / GPIO17 / GPIO24 |

Numeración BCM. La impresora solo recibe datos: GPIO15 (RX) no está conectado en la PCB.

Los dos pads junto al módulo de audio dan acceso a sus pines `SD_MODE` y `GAIN`, y no van conectados a la Pi. El conector `INTERFAZ GPIO's RASPBERRY PI` repite estas señales en una sola fila.

## Cómo leer `bom.csv`

| Columna | Significado |
|---|---|
| `ref_pcb` | Dónde va en la PCB, según su serigrafía o su nombre en el diseño |
| `cantidad` | Unidades por máquina |
| `sustitucion` | `exacto`: usa esa pieza. `equivalente`: vale otra con las mismas características. `genérico`: cualquiera que cumpla la especificación |
| `estado` | `probado`: usado en una máquina. `pendiente`: faltan datos o confirmar el modelo |
| `pack_min` | Unidades mínimas de compra |
| `precio_unit_eur` | Precio orientativo por unidad, con punto decimal |

Los enlaces y los precios son orientativos. Si un enlace deja de funcionar, busca por la descripción y la especificación.
