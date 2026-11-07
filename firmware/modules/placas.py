"""
placas.py — Perfiles de placa: pines de botón y LED, y salidas posibles.

La placa se guarda en config.json ('placa') y estos pines mandan sobre
boton.pin_gpio y led.pin_gpio. Sin placa elegida no se toca ni el botón ni
el LED: GPIO23 es el LED en la PCB y el botón en el Voice HAT, y ponerlo en
alto como LED con el botón pulsado lo cortocircuitaría a masa.

GPIO16 (apagado del amplificador del Voice HAT) lo gestiona el driver del
overlay googlevoicehat-soundcard: el firmware no debe tocarlo nunca.

'keepalive' es el silencio continuo de modules/audio.py. Evita el chasquido del
MAX98357A de la PCB, que se apaga en cuanto se para el reloj I2S. En el Voice
HAT el driver ya gestiona el apagado del amplificador.
"""

PLACAS = {
    "storymaker_pcb": {"boton": 5,  "led": 23, "salidas": {"eink", "impresora", "audio"},
                       "keepalive": True},
    "voicehat_pi3":   {"boton": 23, "led": 25, "salidas": {"audio"},
                       "keepalive": False},
}


def placa_activa(config: dict):
    """Nombre de la placa, o None si no hay una elegida y válida.

    Una instalación con el setup completado y sin la clave 'placa' es anterior
    a los perfiles: se trata como la PCB del proyecto para no romperla.
    """
    if 'placa' in config:
        placa = config['placa']
        return placa if placa in PLACAS else None
    if config.get('setup_completado', False):
        return 'storymaker_pcb'
    return None


def filtrar_hardware(hw: dict, placa) -> dict:
    """Copia de la sección 'hardware' con desactivadas las salidas que la placa
    no tiene, aunque config.json las marque como activas, y con el keepalive
    de la placa en la del audio."""
    if placa is None:
        return hw
    filtrado = {}
    for salida, cfg in hw.items():
        cfg = dict(cfg)
        if salida not in PLACAS[placa]['salidas']:
            cfg['activada'] = False
        if salida == 'audio':
            cfg['keepalive'] = PLACAS[placa]['keepalive']
        filtrado[salida] = cfg
    return filtrado
