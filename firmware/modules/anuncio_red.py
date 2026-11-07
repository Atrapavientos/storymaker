"""
anuncio_red.py — Dicta por voz el estado de la red en las cajas solo con audio.

Sin e-ink ni impresora, la caja no tiene otra forma de decir su dirección. Un
hilo consulta netinfo cada 5 s y habla cuando el estado (modo + IP) cambia y
se mantiene dos lecturas seguidas, para no anunciar transitorios del arranque.
Hace falta vigilar, no anunciar una vez: la WiFi se puede dar desde el portal
cautivo sin reiniciar la Pi.

Habla con clips de Elvira grabados de antemano (data/voz, ver
deploy/generar_voz.py): en modo AP no hay internet para edge-tts. Si falta
algún clip o no se puede reproducir, lo dice con espeak.

Tras una contraseña errónea, el AP cae unos 5 s y el portal cautivo lo
reactiva: demasiado poco para verlo sondeando. Por eso el estado del AP
incluye la fecha de /run/storymaker-ap-mode, que se renueva con cada
activación: una sesión nueva de AP se anuncia aunque la salida fuera breve.
"""
import os
import threading
import time

from modules.netinfo import get_wifi_mode, get_ip

INTERVALO = 5
DIR_VOZ   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'voz')
MARCA_AP  = '/run/storymaker-ap-mode'
VELOCIDAD = 125

CIFRAS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]

# Para el fallback con espeak. Grafías fonéticas: se ajustan de oído
TEXTO_AP = "Sin red wifi. Conéctate a la red Estóri Méiker guion Setap."
TEXTO_CLIENTE = ("Conectada. Mi dirección es {ip}, dos puntos, cinco mil. "
                 "Repito: {ip}, dos puntos, cinco mil.")


def ip_a_texto(ip):
    octetos = (" ".join(CIFRAS[int(c)] for c in o) for o in ip.split("."))
    return ", punto, ".join(octetos)


def _sesion_ap():
    try:
        return os.stat(MARCA_AP).st_mtime
    except OSError:
        return None


def _leer_estado():
    modo = get_wifi_mode()
    if modo == 'client':
        return (modo, get_ip())
    if modo == 'ap':
        return (modo, _sesion_ap())
    return (modo, None)


def _texto(estado):
    modo, ip = estado
    if modo == 'ap':
        return TEXTO_AP
    if modo == 'client' and ip:
        return TEXTO_CLIENTE.format(ip=ip_a_texto(ip))
    return None  # sin red: nada que decir


def _clips(estado):
    """Lista de clips que dicen el estado, en el orden en que suenan."""
    modo, ip = estado
    if modo == 'ap':
        return ['ap']
    if modo == 'client' and ip:
        cifras = []
        for i, octeto in enumerate(ip.split('.')):
            if i:
                cifras.append('punto')
            cifras.extend(octeto)
        return ['conectada', *cifras, 'puerto', 'repito', *cifras, 'puerto']
    return []


def _anunciar(audio, estado):
    rutas = [os.path.join(DIR_VOZ, f'{c}.mp3') for c in _clips(estado)]
    if rutas and all(os.path.isfile(r) for r in rutas) and audio.reproducir(rutas):
        return
    texto = _texto(estado)
    if texto:
        audio.hablar_offline(texto, velocidad=VELOCIDAD)


def _vigilar(audio):
    anunciado = None
    candidato = None
    lecturas  = 0
    while True:
        try:
            estado = _leer_estado()
            if estado == candidato:
                lecturas += 1
            else:
                candidato, lecturas = estado, 1
            if lecturas == 2 and estado != anunciado:
                # Se recuerda también «sin red», para volver a anunciar el AP
                # si la caja regresa a él (p. ej. tras una contraseña errónea)
                anunciado = estado
                texto = _texto(estado)
                print(f"[Red] Estado estable: {estado}" + (" → anuncio" if texto else ""))
                if texto:
                    _anunciar(audio, estado)
        except Exception as e:
            print(f"[Red] Error vigilando la red: {e}")
        time.sleep(INTERVALO)


def iniciar(audio):
    threading.Thread(target=_vigilar, args=(audio,), daemon=True).start()
    print("[Red] Anuncio de la dirección por voz activo.")
