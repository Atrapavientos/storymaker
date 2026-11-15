# Lista de materiales

Todas las versiones de la máquina usan la misma PCB. Lo que cambia es qué se monta en ella y qué se conecta. La lista completa está en [`bom.csv`](bom.csv), organizada por bloques.

> Faltan los precios y los proveedores.

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
| `ALIM-PB` | Powerbank de dos celdas 18650 | Sí | Sí | 2 A; recomendado más de 2,5 A, sobre todo con impresora |
| `ALIM-LIPO` | MH-CD42 + LiPo | **No** | Sí | Cargador de 2 A |

Una sola celda no cubre los picos de consumo de la impresora.

### 3. Suma los bloques

Junta las filas de los bloques elegidos en `bom.csv`. El bloque `OPC` es opcional.

## Configurar la alimentación

Antes de dar corriente, coloca el puente `J1` según la alimentación elegida:
`SÓLO USB` con cargador USB o powerbank, `BAT+CARG.` con MH-CD42 + LiPo. Qué va
en cada borne, cómo funciona cada posición y los avisos de polaridad, en
[Alimentación y el puente J1](../README.md#alimentaci%C3%B3n-y-el-puente-j1).
A qué va cada conector de la PCB, en [Conectores](../README.md#conectores).

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
