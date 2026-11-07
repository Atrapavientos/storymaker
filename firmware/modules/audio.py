"""
audio.py — Salida de audio TTS con edge-tts (Microsoft Neural).
I2S MAX98357A:
  GPIO18 -> BCLK
  GPIO19 -> LRC (LRCLK)
  GPIO21 -> DIN
Voice HAT de Google: misma salida, la tarjeta la elige /etc/asound.conf.
edge-tts genera un .mp3 que se reproduce con mpg123 (plug:dmixed).
Requiere red. Sin red, cae a espeak-ng como fallback offline, por el mismo
dispositivo y con el mismo volumen.
"""
import subprocess
import tempfile
import os
import shutil
import socket
import asyncio
import threading
import time

VOZ_DEFAULT  = "es-ES-ElviraNeural"
MPG123_BIN   = "mpg123"
APLAY_BIN    = "aplay"
APLAY_DEVICE = "plug:dmixed"
EDGE_TTS_BIN = "/home/storymaker/proyecto/venv/bin/edge-tts"

# Un solo hablante a la vez, aunque haya varias instancias de Audio: así el
# anuncio de la IP no se solapa con una premisa.
_lock_voz = threading.Lock()

# Tras un fallo de edge-tts, las frases van directas a espeak durante este
# tiempo. Con la red caída, cada intento costaba hasta 15 s de silencio; así
# solo lo paga la primera frase, y la voz de espeak avisa de que algo falla.
PAUSA_EDGE = 120
_edge_caido_hasta = 0.0

# Antes de cada intento se comprueba en ≤2 s que se llega al servidor de voz.
# Sin red, o con una WiFi que no da salida a internet (habitual en centros),
# la primera frase ya no pierde los 15 s del timeout de edge-tts. Va en un hilo
# para que una resolución DNS colgada tampoco pase de ese límite.
HOST_EDGE = ("speech.platform.bing.com", 443)

def _hay_ruta_edge(limite=2.0):
    ok = []
    def _probar():
        try:
            socket.create_connection(HOST_EDGE, timeout=limite).close()
            ok.append(True)
        except OSError:
            pass
    hilo = threading.Thread(target=_probar, daemon=True)
    hilo.start()
    hilo.join(limite)
    return bool(ok)

class Audio:
    def __init__(self, config: dict):
        self.activada = config.get('activada', False)
        self.voz      = config.get('voz', VOZ_DEFAULT)
        self.volumen  = config.get('volumen', 90)
        # Lo decide la placa (modules/placas.py); sin dato, como en la PCB
        self.keepalive = config.get('keepalive', True)
        self._mpg123_ok = shutil.which(MPG123_BIN) is not None
        self._aplay_ok  = shutil.which(APLAY_BIN)  is not None
        self._espeak_ok = shutil.which('espeak-ng') is not None or shutil.which('espeak') is not None
        self._edge_ok   = os.path.isfile(EDGE_TTS_BIN)
        if self.activada:
            if self._edge_ok and self._mpg123_ok:
                print(f"[Audio] edge-tts listo. Voz: {self.voz}")
                if self._aplay_ok and self.keepalive:
                    self._iniciar_keepalive()
                elif not self.keepalive:
                    print("[Audio] Keep-alive desactivado para esta placa.")
            elif self._espeak_ok:
                print("[Audio] Sin red o edge-tts no disponible, usando espeak como fallback.")
            else:
                print("[Audio] AVISO: ningun motor TTS disponible.")

    def _iniciar_keepalive(self):
        """Mantiene el reloj I2S corriendo con silencio continuo.

        El MAX98357A entra en shutdown en cuanto BCLK se detiene (fin de
        mpg123). Al reactivarse produce un chasquido audible. Alimentar el
        dispositivo con /dev/zero (muestras nulas = silencio digital) mantiene
        el reloj I2S vivo indefinidamente.

        Requiere que pcm.dmixed sea 'type dmix' en /etc/asound.conf, para
        que aplay y mpg123 puedan usar el dispositivo simultáneamente.
        """
        def _loop():
            while True:
                try:
                    subprocess.run(
                        [APLAY_BIN, '-D', APLAY_DEVICE,
                         '-f', 'S16_LE', '-r', '44100', '-c', '2',
                         '/dev/zero'],
                        capture_output=True   # sin timeout: corre indefinidamente
                    )
                except Exception:
                    time.sleep(2)             # pausa breve si falla, luego reintenta
        threading.Thread(target=_loop, daemon=True).start()
        print("[Audio] Keep-alive MAX98357A activo — chasquido de arranque eliminado.")

    def hablar(self, texto: str):
        if not self.activada:
            return
        with _lock_voz:
            self._hablar(texto)

    def hablar_offline(self, texto: str, velocidad: int = 130):
        """Siempre con espeak: para avisos del sistema que deben sonar aunque no
        haya internet, como la dirección IP."""
        if not self.activada or not self._espeak_ok:
            return
        with _lock_voz:
            self._hablar_espeak(texto, velocidad)

    def reproducir(self, rutas: list) -> bool:
        """Reproduce seguidos varios clips .mp3 grabados (data/voz), con el
        volumen del slider. Devuelve False si no se ha podido."""
        if not self.activada or not self._mpg123_ok:
            return False
        with _lock_voz:
            self._leer_volumen()
            try:
                subprocess.run(
                    [MPG123_BIN, '-q', '-a', APLAY_DEVICE,
                     '-f', str(int(self.volumen / 100 * 32768)), *rutas],
                    capture_output=True, check=True, timeout=60)
                return True
            except Exception as e:
                print(f"[Audio] Error reproduciendo clips: {e}")
                return False

    def _hablar(self, texto: str):
        global _edge_caido_hasta
        if self._edge_ok and self._mpg123_ok and time.time() >= _edge_caido_hasta:
            if not _hay_ruta_edge():
                _edge_caido_hasta = time.time() + PAUSA_EDGE
                print(f"[Audio] Sin conexión con el servidor de edge-tts; "
                      f"espeak durante {PAUSA_EDGE} s...")
            else:
                try:
                    asyncio.run(self._hablar_edge(texto))
                    return
                except Exception as e:
                    _edge_caido_hasta = time.time() + PAUSA_EDGE
                    print(f"[Audio] edge-tts fallo ({str(e) or type(e).__name__}); "
                          f"espeak durante {PAUSA_EDGE} s...")
        if self._espeak_ok:
            self._hablar_espeak(texto)
        else:
            print("[Audio] Sin motor TTS disponible.")

    def _leer_volumen(self):
        """Relee el volumen de config.json: el slider del portal lo cambia en caliente."""
        import json
        try:
            with open('/home/storymaker/proyecto/data/config.json') as _f:
                self.volumen = json.load(_f).get('hardware', {}).get('audio', {}).get('volumen', self.volumen)
        except Exception:
            pass

    async def _hablar_edge(self, texto: str):
        import edge_tts
        self._leer_volumen()
        tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        tmp.close()
        mp3_path = tmp.name
        try:
            comunicar = edge_tts.Communicate(texto, self.voz)
            await asyncio.wait_for(comunicar.save(mp3_path), timeout=15.0)
            subprocess.run(
                [MPG123_BIN, '-a', APLAY_DEVICE, '-f', str(int(self.volumen / 100 * 32768)), mp3_path],
                capture_output=True,
                check=True,
                timeout=60
            )
            print("[Audio] Reproduccion completada.")
        except Exception as e:
            raise e
        finally:
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)

    def _hablar_espeak(self, texto: str, velocidad: int = 130):
        """espeak escribe el WAV en stdout y aplay lo saca por plug:dmixed, como
        mpg123: abrir la tarjeta directamente chocaría con el keepalive. El
        volumen es la amplitud de espeak, donde 100 es el nivel normal, igual
        que volumen=100 deja mpg123 sin escalar."""
        self._leer_volumen()
        espeak = None
        try:
            cmd = ['espeak-ng' if shutil.which('espeak-ng') else 'espeak',
                   '-v', 'es', '-s', str(velocidad), '-a', str(int(self.volumen)),
                   '--stdout', texto]
            espeak = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL)
            subprocess.run([APLAY_BIN, '-q', '-D', APLAY_DEVICE],
                           stdin=espeak.stdout, capture_output=True, timeout=30)
            espeak.stdout.close()
            espeak.wait(timeout=5)
            print("[Audio] espeak completado.")
        except Exception as e:
            if espeak:
                espeak.kill()
            print(f"[Audio] espeak error: {e}")

    def esta_disponible(self) -> bool:
        return (self._edge_ok and self._mpg123_ok) or self._espeak_ok
