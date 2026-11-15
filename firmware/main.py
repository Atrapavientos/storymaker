#!/usr/bin/env python3
"""
main.py — Punto de entrada StoryMaker v3.

Flujo:
  1. Carga config.json
  2. Inicia portal web (hilo daemon)
  3. Si setup no completado → avisa y espera en portal
  4. Inicia generador + salidas de hardware
  5. Configura botón y entra en bucle de espera
"""

import os
import sys
import time
import signal
import subprocess
import traceback

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from modules.config_manager import cargar_config, guardar_config
from modules.generador      import Generador
from modules.boton          import Boton, detectar_boton_arranque, SimpleLED
from modules.salidas        import RouterSalidas
from modules.portal         import (Portal, reinicio_pendiente, leer_marca_reinicio,
                                    publicar_premisa)
from modules.placas         import PLACAS, placa_activa, filtrar_hardware, detectar_placa


generador = None
router    = None
boton     = None


def al_pulsar_corto():
    """Genera una frase y la envía a todas las salidas activas."""
    global generador, router, boton

    if not generador or not router:
        return

    if not generador.hay_frases_disponibles():
        config  = cargar_config()
        mensaje = config.get('mensaje_sin_frases',
                             'Se han agotado las combinaciones. Reinicia el dispositivo.')
        print(f"[Main] Frases agotadas.")
        # Parpadeo lento: aviso de que no quedan premisas
        if boton:
            boton.led.off()
            boton.parpadear(5, 0.4)
            boton.led.on()
        publicar_premisa(mensaje, tipo='aviso')
        router.enviar(mensaje)
        return

    # Parpadeo de confirmación mientras se genera/envía
    if boton:
        boton.led.off()
        boton.parpadear(2, 0.1)

    frase = generador.generar_frase()
    if frase is None:
        # Frases agotadas: otro hilo consumió la última entre la comprobación
        # anterior y este punto. Tratarlo igual que el caso de lista vacía.
        config  = cargar_config()
        mensaje = config.get('mensaje_sin_frases',
                             'Se han agotado las combinaciones. Reinicia el dispositivo.')
        print("[Main] Frases agotadas (detectado en generar_frase).")
        if boton:
            boton.led.off()
            boton.parpadear(5, 0.4)
            boton.led.on()
        publicar_premisa(mensaje, tipo='aviso')
        router.enviar(mensaje)
        return

    # Al portal primero: aparece en pantalla mientras la caja habla o imprime
    publicar_premisa(frase, perfil=cargar_config().get('perfil_activo', '').upper())
    resultados = router.enviar_con_animacion(frase)

    for salida, ok in resultados.items():
        icono = "✓" if ok else "✗"
        print(f"[Main] {icono} {salida}")

    # Volver a fijo: sistema listo para la siguiente pulsación
    if boton:
        boton.led.on()


def al_pulsar_largo():
    """Apagado seguro: muestra despedida y apaga."""
    print("[Main] → Pulsación larga: apagando...")
    if router:
        router.mostrar_despedida()
        router.cerrar()
    if boton:
        boton.shutdown_seguro()


def al_cambiar_perfil(nuevo_perfil):
    """Recarga el generador cuando el portal cambia el perfil activo."""
    global generador
    ruta_perfil = os.path.join(PROJECT_DIR, 'data', 'perfiles', nuevo_perfil)
    try:
        nuevo_generador = Generador(ruta_perfil)
        generador = nuevo_generador
        print(f"[Main] Perfil cambiado a '{nuevo_perfil}' — generador recargado.")
    except (FileNotFoundError, ValueError) as e:
        print(f"[Main] ERROR al cargar perfil '{nuevo_perfil}': {e}")


def cleanup(*args):
    print("[Main] Limpieza y salida.")
    if router:
        try: router.cerrar()
        except Exception: pass
    if boton:
        try: boton.limpiar()
        except Exception: pass
    sys.exit(0)


def _migrar_perfil_1eso():
    """El perfil de fábrica se llamaba `1eso` hasta la release de 2026-11. En las
    cajas ya montadas, deploy.sh no toca data/perfiles/ ni config.json, así que
    el cambio de nombre se hace aquí, una sola vez. Las premisas se conservan."""
    perfiles = os.path.join(PROJECT_DIR, 'data', 'perfiles')
    viejo, nuevo = os.path.join(perfiles, '1eso'), os.path.join(perfiles, 'juvenil')
    if not os.path.isdir(viejo):
        return
    if os.path.exists(nuevo):
        print("[Main] AVISO: existen los perfiles '1eso' y 'juvenil'; no se migra.")
        return
    try:
        os.rename(viejo, nuevo)
        config = cargar_config()
        if config.get('perfil_activo') == '1eso':
            config['perfil_activo'] = 'juvenil'
            guardar_config(config)
        print("[Main] Perfil '1eso' renombrado a 'juvenil'.")
    except OSError as e:
        print(f"[Main] AVISO: no se ha podido renombrar el perfil '1eso': {e}")


def _autodetectar_placa(config):
    """Primer arranque de una imagen recién grabada: la imagen sale preparada
    para la PCB, así que en una Pi 3 con el Voice HAT el altavoz no tendría
    driver y la caja no podría decir a qué red conectarse. Si el HAT se
    identifica por su EEPROM, se aplica su placa y se reinicia una vez.

    Solo actúa sin placa guardada y con el setup sin completar. La placa se
    guarda antes de reiniciar, así que no puede entrar en bucle."""
    if 'placa' in config or config.get('setup_completado', False):
        return
    placa = detectar_placa()
    if not placa:
        return
    print(f"[Main] Detectada la placa '{placa}' por la EEPROM del HAT. Aplicándola...")
    try:
        r = subprocess.run(['sudo', '-n', '/usr/local/bin/storymaker-perfil.sh', placa],
                           capture_output=True, text=True, timeout=30)
    except Exception as e:
        print(f"[Main] AVISO: no se ha podido aplicar la placa: {e}. Se elige en el portal.")
        return
    if r.returncode != 0:
        print(f"[Main] AVISO: storymaker-perfil.sh falló ({r.returncode}): "
              f"{(r.stderr or '').strip()}. Se elige en el portal.")
        return
    config['placa'] = placa
    guardar_config(config)
    print("[Main] Placa aplicada. Reiniciando la Pi para cargar su driver de audio...")
    subprocess.run(['sudo', '-n', '/usr/sbin/shutdown', '-r', 'now'], check=False)
    time.sleep(60)   # que el reinicio llegue antes de seguir arrancando
    sys.exit(0)


def main():
    global generador, router, boton

    print("=" * 50)
    print("  StoryMaker v3 — Arrancando...")
    print("=" * 50)

    # 1. Configuración
    _migrar_perfil_1eso()
    try:
        config = cargar_config()
        print(f"[Main] Perfil activo: '{config.get('perfil_activo', '?')}'")
    except FileNotFoundError as e:
        print(f"[Main] ERROR CRÍTICO: {e}")
        sys.exit(1)

    # 1.4 Placa reconocible por su EEPROM (Voice HAT) en el primer arranque
    _autodetectar_placa(config)

    # 1.5 Detección de botón al arranque → forzar AP
    # Sin placa elegida no se toca ni botón ni LED (ver modules/placas.py)
    placa = placa_activa(config)
    if placa:
        print(f"[Main] Placa: {placa}")
        pin_boton = PLACAS[placa]['boton']
        pin_led   = PLACAS[placa]['led']
        # El AP de rescate lo levanta storymaker-wifi.sh, como root, antes de
        # este servicio: desde aquí polkit no deja cambiar de red. Esto solo
        # da la señal del LED y avisa si el botón no se pulsó a tiempo.
        if detectar_boton_arranque(pin_boton, pin_led=pin_led):
            if os.path.exists('/run/storymaker-ap-mode'):
                # 3 parpadeos lentos: AP activo
                _led_boot = SimpleLED(pin_led)
                _led_boot.blink(on_time=0.4, off_time=0.4, n=3)
            else:
                print("[Main] Botón pulsado, pero el AP no está activo: hay que "
                      "mantenerlo desde el encendido, antes de que conecte la WiFi.")
    else:
        print("[Main] Placa sin elegir: botón y LED desactivados hasta configurarla.")

    # 2. Portal web (siempre, incluso antes del setup)
    portal = Portal(config)
    portal.iniciar()

    # 2.5 Actualizaciones: confirmar la versión recién instalada si el portal
    # aguanta en pie, y buscar versiones nuevas en segundo plano
    from modules import actualizador
    from modules.netinfo import get_wifi_mode as _modo_red_act
    print(f"[Main] Firmware v{actualizador.leer_version()}")
    actualizador.programar_confirmacion()
    actualizador.iniciar_comprobacion_periodica(cargar_config, _modo_red_act)

    # 3. Si el setup no está completo, esperamos a que se configure desde el portal
    if not config.get('setup_completado', False):
        print("[Main] Setup no completado. Accede al portal para configurar el hardware.")
        print(f"[Main] http://<ip-de-la-pi>:{config.get('portal', {}).get('puerto', 5000)}")
        print("[Main] Esperando en modo portal...")

        from modules.eink import PantallaEInk
        from modules.netinfo import get_wifi_mode, get_ip
        from modules.audio import Audio

        cfg_eink      = config.get('hardware', {}).get('eink', {})
        cfg_impresora = config.get('hardware', {}).get('impresora', {})
        cfg_audio     = dict(config.get('hardware', {}).get('audio', {}))
        cfg_audio['activada'] = True  # forzar activo para anuncio de setup
        if placa:
            cfg_audio['keepalive'] = PLACAS[placa]['keepalive']

        pantalla_setup  = None
        impresora_setup = None
        audio_setup     = None

        # Sin placa se prueba todo (primer arranque de la PCB); con placa,
        # solo lo que tiene. La e-ink usa GPIO25, el LED del Voice HAT.
        salidas_setup = PLACAS[placa]['salidas'] if placa else {'eink', 'impresora', 'audio'}

        if 'eink' in salidas_setup:
            try:
                pantalla_setup = PantallaEInk(cfg_eink)
            except Exception as e:
                print(f"[Main] E-ink no disponible en setup: {e}")

        if 'impresora' in salidas_setup:
            try:
                from modules.impresora import Impresora
                impresora_setup = Impresora(cfg_impresora)
            except Exception as e:
                print(f"[Main] Impresora no disponible en setup: {e}")

        try:
            audio_setup = Audio(cfg_audio)
        except Exception as e:
            print(f"[Main] Audio no disponible en setup: {e}")

        from modules import anuncio_red

        def _anunciar_setup(modo, ip):

            if pantalla_setup:
                try:
                    pantalla_setup.mostrar_bienvenida(modo=modo, ip=ip)
                except Exception as e:
                    print(f"[Main] E-ink setup error: {e}")

            # Con los clips grabados con la voz de Elvira (data/voz), como las
            # cajas solo con altavoz: en modo AP no hay internet y edge-tts no
            # puede sonar, así que el primer aviso salía siempre con espeak.
            # Si falta algún clip, anuncio_red lo dice con espeak.
            if audio_setup and modo in ('ap', 'client'):
                try:
                    anuncio_red._anunciar(audio_setup, (modo, ip))
                except Exception as e:
                    print(f"[Main] Audio anuncio error: {e}")

            if impresora_setup and modo in ('ap', 'client'):
                try:
                    # Se reutiliza la bienvenida en lugar de componer texto plano:
                    # así el primer arranque saca también el QR, igual que la
                    # e-ink, y la URL de cada modo se decide en un solo sitio.
                    impresora_setup.imprimir_bienvenida(modo=modo, ip=ip)
                except Exception as e:
                    print(f"[Main] Impresora setup error: {e}")

        # Esperar hasta 12 s a que NetworkManager levante la red
        for _ in range(6):
            if get_wifi_mode() != 'none':
                break
            time.sleep(2)

        # Capturar modo ANTES del anuncio para evitar race condition en _modo_red
        _modo_red = get_wifi_mode()
        _sesion_ap = anuncio_red._sesion_ap()
        _anunciar_setup(modo=_modo_red, ip=get_ip())

        signal.signal(signal.SIGINT,  cleanup)
        signal.signal(signal.SIGTERM, cleanup)
        while True:
            time.sleep(5)
            try:
                modo_actual = get_wifi_mode()
                sesion_actual = anuncio_red._sesion_ap()
                if modo_actual != _modo_red and modo_actual in ('client', 'ap'):
                    _modo_red, _sesion_ap = modo_actual, sesion_actual
                    _anunciar_setup(modo=_modo_red, ip=get_ip())
                elif modo_actual == 'ap' and sesion_actual != _sesion_ap:
                    # Contraseña WiFi errónea: el AP cae unos 5 s y el cautivo
                    # lo reactiva, demasiado rápido para verlo como cambio de
                    # modo. La marca /run/storymaker-ap-mode se renueva, y eso
                    # sí se ve. Solo se repite la voz: ni tique ni e-ink.
                    _sesion_ap = sesion_actual
                    print("[Main] El AP ha vuelto (¿contraseña WiFi errónea?): se repite el aviso.")
                    if audio_setup:
                        try:
                            anuncio_red._anunciar(audio_setup, ('ap', sesion_actual))
                        except Exception as e:
                            print(f"[Main] Audio anuncio error: {e}")

                config_nueva = cargar_config()
                # Con un cambio de placa, el portal reinicia la Pi entera
                if config_nueva.get('setup_completado', False) and not reinicio_pendiente():
                    print("[Main] Setup completado. Reiniciando servicio...")
                    # Usar systemctl en lugar de os.execv: evita que el FD del
                    # socket Flask quede heredado y cause conflicto de puerto.
                    subprocess.Popen(
                        ['sudo', 'systemctl', 'restart', 'historias.service'],
                        start_new_session=True
                    )
                    sys.exit(0)
            except Exception:
                pass

    # 4. Generador de frases
    ruta_perfil = os.path.join(PROJECT_DIR, 'data', 'perfiles', config['perfil_activo'])
    try:
        generador = Generador(ruta_perfil)
    except (FileNotFoundError, ValueError) as e:
        print(f"[Main] ERROR CRÍTICO: {e}")
        sys.exit(1)

    # 5. Router de salidas (e-ink / impresora / audio)
    router = RouterSalidas(filtrar_hardware(config.get('hardware', {}), placa))
    if not router.hay_salidas():
        print("[Main] AVISO: ninguna salida configurada. Ve al portal → ⚙ Hardware.")

    # Solo con altavoz, la caja dicta su dirección: no tiene dónde mostrarla
    if router.audio and not router.eink and not router.impresora:
        from modules import anuncio_red
        anuncio_red.iniciar(router.audio)

    # 6. Botón (pines según la placa; sin placa válida no se arma)
    if placa:
        boton = Boton({**config.get('boton', {}), 'pin_gpio': PLACAS[placa]['boton']},
                      {'pin_gpio': PLACAS[placa]['led']})
        boton.on_corto(al_pulsar_corto)
        boton.on_largo(al_pulsar_largo)
    else:
        print(f"[Main] AVISO: placa '{config.get('placa')}' no válida. Botón y LED desactivados.")

    # Registrar callbacks en el portal (botón virtual web + cambio de perfil)
    from modules.portal import (registrar_callback_generar,
                                 registrar_callback_despedida,
                                 registrar_callback_cambiar_perfil)
    registrar_callback_generar(al_pulsar_corto)
    registrar_callback_despedida(router.mostrar_despedida)
    registrar_callback_cambiar_perfil(al_cambiar_perfil)

    # LED encendido fijo = sistema listo para generar premisas
    if boton:
        boton.led.on()
    # Tras guardar el hardware en el portal no se imprime (ver portal.py)
    imprimir_bienvenida = leer_marca_reinicio()
    if not imprimir_bienvenida:
        print("[Main] Reinicio desde el portal: bienvenida sin ticket impreso.")
    router.mostrar_bienvenida(imprimir=imprimir_bienvenida)

    # 7. Señales del sistema
    signal.signal(signal.SIGINT,  cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("[Main] Sistema listo. Esperando pulsaciones...")

    # 8. Bucle principal (el trabajo real lo hace el hilo del botón)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"[Main] Excepción fatal: {e}")
        traceback.print_exc()
        # Código 1, no el 0 de cleanup(): systemd solo reinicia el servicio
        # tras un fallo, y el guardián de actualizaciones cuenta esos arranques
        # para revertir una versión rota.
        try:
            cleanup()
        except SystemExit:
            pass
        sys.exit(1)
