"""
actualizador.py — Actualizaciones menores del firmware sin regrabar la tarjeta.

Una actualización es un fichero `storymaker-actualizacion-X.Y.Z.tar` con dos
piezas: `contenido.tar.gz` (el firmware, como lo despliega deploy.sh) y
`contenido.tar.gz.sig`, su firma Ed25519. La firma se comprueba con `openssl`
contra `clave_actualizaciones.pem`, en la raíz del proyecto. Sin la clave
privada, que solo está en el PC de quien publica, no se puede fabricar un
paquete que la caja acepte.

Llega por dos caminos que terminan en `aplicar()`:
  • El portal lo sube a mano (sin internet en la caja).
  • `comprobar()` lee el manifiesto publicado en el repositorio canónico y,
    si hay una versión nueva, `instalar_disponible()` la descarga.

Reglas de versión: solo se instala una versión mayor que la actual y con los
mismos dos primeros números. Cambiar esos (v1.0 → v1.1) es una imagen nueva:
toca ficheros de sistema que esta vía no puede escribir.

Vuelta atrás: antes de copiar se guarda lo que se va a sobrescribir. Si la
versión nueva no llega a confirmarse (main.py llama a `confirmar()` cuando el
portal lleva un rato en marcha), el guardián del sistema
(/usr/local/bin/storymaker-arranque, ExecStartPre de historias.service)
restaura la anterior al tercer arranque fallido. El guardián no forma parte del
firmware a propósito: una actualización rota no puede estropearlo.

Nunca se tocan data/config.json ni data/perfiles/: las premisas y la
configuración de cada caja sobreviven a la actualización.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time
import urllib.error
import urllib.request

PROYECTO   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ESTADO_DIR = os.environ.get('STORYMAKER_ACTUALIZACION_DIR',
                            os.path.join(os.path.dirname(PROYECTO), '.storymaker-actualizacion'))
ESTADO     = os.path.join(ESTADO_DIR, 'estado.json')
ANTERIOR   = os.path.join(ESTADO_DIR, 'anterior')
CLAVE      = os.path.join(PROYECTO, 'clave_actualizaciones.pem')

# El repositorio canónico: el mismo al que apunta el QR de los aparatos
MANIFIESTO = 'https://codeberg.org/atrapavientos/storymaker/raw/branch/main/actualizacion.json'

MAX_PAQUETE   = 20 * 1024 * 1024    # descarga y fichero subido
MAX_CONTENIDO = 60 * 1024 * 1024    # suma descomprimida: contra bombas de compresión
INTENTOS_MAX  = 3                   # igual que en storymaker-arranque
SEGUNDOS_CONFIRMAR = 45

# Lo que pertenece a cada caja y nunca viaja en una actualización
_PROTEGIDOS = ('data/config.json',)
_PROTEGIDAS = ('data/perfiles/', 'venv/', 'deploy/', '.')

_lock_instalar = threading.Lock()
_lock_estado   = threading.Lock()
_ultima = {'fecha': None, 'ok': None, 'error': None,
           'disponible': None, 'imagen': None}


class ErrorActualizacion(Exception):
    """Mensaje pensado para mostrarse tal cual en el portal."""


# ------------------------------------------------------------------ #
# Versiones                                                           #
# ------------------------------------------------------------------ #
def leer_version(proyecto=PROYECTO):
    try:
        with open(os.path.join(proyecto, 'VERSION'), encoding='utf-8') as f:
            return f.read().strip() or '0.0'
    except OSError:
        return '0.0'


def tupla(version):
    """'1.0' → (1, 0, 0); '1.0.2' → (1, 0, 2). ValueError si no es válida."""
    partes = version.strip().lstrip('v').split('.')
    if not 2 <= len(partes) <= 3 or not all(p.isdigit() for p in partes):
        raise ValueError(f"versión no válida: {version!r}")
    numeros = [int(p) for p in partes]
    return tuple(numeros + [0] * (3 - len(numeros)))


def _compatibilidad(nueva, actual):
    """None si `nueva` se puede instalar sobre `actual`; si no, el motivo."""
    try:
        tn, ta = tupla(nueva), tupla(actual)
    except ValueError as e:
        return str(e)
    if tn[:2] != ta[:2]:
        if tn[:2] > ta[:2]:
            return (f"La versión {nueva} necesita una imagen nueva: no se instala desde "
                    f"aquí, hay que regrabar la tarjeta.")
        return f"La versión {nueva} es para otra imagen (esta caja tiene la {actual})."
    if tn <= ta:
        return f"Esta caja ya tiene la versión {actual}, igual o más reciente que la {nueva}."
    return None


# ------------------------------------------------------------------ #
# Estado persistente                                                  #
# ------------------------------------------------------------------ #
def leer_estado():
    try:
        with open(ESTADO, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _guardar_estado(estado):
    os.makedirs(ESTADO_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=ESTADO_DIR, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ESTADO)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def confirmar():
    """La versión recién instalada ha arrancado bien: el guardián ya no la revierte."""
    with _lock_estado:
        estado = leer_estado()
        if estado.get('fase') != 'pendiente':
            return
        estado['fase'] = 'ok'
        estado['confirmada'] = time.strftime('%Y-%m-%d %H:%M')
        estado.pop('intentos', None)
        _guardar_estado(estado)
    print(f"[Actualizador] Versión {estado.get('version_nueva')} confirmada.")


def programar_confirmacion():
    """main.py la llama al levantar el portal. Si el proceso cae antes, no se confirma."""
    if leer_estado().get('fase') == 'pendiente':
        t = threading.Timer(SEGUNDOS_CONFIRMAR, confirmar)
        t.daemon = True
        t.start()


# ------------------------------------------------------------------ #
# Verificación del paquete                                            #
# ------------------------------------------------------------------ #
def _verificar_firma(contenido, firma, clave=CLAVE):
    if not os.path.isfile(clave):
        raise ErrorActualizacion("Falta la clave pública de actualizaciones en la caja.")
    try:
        r = subprocess.run(['openssl', 'pkeyutl', '-verify', '-pubin', '-inkey', clave,
                            '-rawin', '-in', contenido, '-sigfile', firma],
                           capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        raise ErrorActualizacion("No se encuentra openssl en el sistema.")
    except subprocess.TimeoutExpired:
        raise ErrorActualizacion("La comprobación de la firma ha tardado demasiado.")
    if r.returncode != 0:
        raise ErrorActualizacion("La firma no es válida: este fichero no es una "
                                 "actualización oficial de StoryMaker, o está dañado.")


def _ruta_segura(nombre):
    """Normaliza la ruta de un miembro. None si hay que ignorarlo (directorios
    raíz); ErrorActualizacion si es peligrosa o toca datos de la caja."""
    n = nombre
    while n.startswith('./'):
        n = n[2:]
    n = n.rstrip('/')
    if not n or n == '.':
        return None
    partes = n.split('/')
    if n.startswith('/') or '..' in partes or '' in partes:
        raise ErrorActualizacion(f"El paquete contiene una ruta no permitida: {nombre}")
    if n in _PROTEGIDOS or any((n + '/').startswith(p) for p in _PROTEGIDAS):
        raise ErrorActualizacion(f"El paquete intenta escribir datos de la caja: {nombre}")
    return n


def _extraer(paquete, destino):
    """Comprueba el paquete y deja el firmware en `destino`. Devuelve
    (version, [rutas relativas de los ficheros])."""
    if os.path.getsize(paquete) > MAX_PAQUETE:
        raise ErrorActualizacion("El fichero es demasiado grande para ser una actualización.")
    trabajo = os.path.join(destino, '..', 'firma')
    os.makedirs(trabajo, exist_ok=True)
    contenido = os.path.join(trabajo, 'contenido.tar.gz')
    firma     = os.path.join(trabajo, 'contenido.tar.gz.sig')

    try:
        with tarfile.open(paquete, 'r:') as tf:
            miembros = {m.name.lstrip('./'): m for m in tf.getmembers()}
            if set(miembros) != {'contenido.tar.gz', 'contenido.tar.gz.sig'} \
                    or not all(m.isfile() for m in miembros.values()):
                raise ErrorActualizacion("Este fichero no es una actualización de StoryMaker.")
            for nombre, ruta in (('contenido.tar.gz', contenido),
                                 ('contenido.tar.gz.sig', firma)):
                with tf.extractfile(miembros[nombre]) as src, open(ruta, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
    except tarfile.TarError:
        raise ErrorActualizacion("Este fichero no es una actualización de StoryMaker.")

    # Nada del contenido se lee antes de comprobar la firma
    _verificar_firma(contenido, firma)

    ficheros, total = [], 0
    with tarfile.open(contenido, 'r:gz') as tf:
        for m in tf.getmembers():
            rel = _ruta_segura(m.name)
            if rel is None or m.isdir():
                continue
            if not m.isfile():
                raise ErrorActualizacion(f"El paquete contiene algo que no es un fichero: {m.name}")
            total += m.size
            if total > MAX_CONTENIDO:
                raise ErrorActualizacion("El contenido del paquete es demasiado grande.")
            ruta = os.path.join(destino, rel)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with tf.extractfile(m) as src, open(ruta, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            os.chmod(ruta, 0o755 if m.mode & 0o111 else 0o644)
            ficheros.append(rel)

    if 'VERSION' not in ficheros or 'main.py' not in ficheros:
        raise ErrorActualizacion("El paquete está incompleto (falta VERSION o main.py).")
    version = leer_version(destino)

    # Un error de sintaxis se detecta aquí, antes de tocar nada de la caja
    for rel in ficheros:
        if rel.endswith('.py'):
            try:
                with open(os.path.join(destino, rel), 'rb') as f:
                    compile(f.read(), rel, 'exec')
            except SyntaxError as e:
                raise ErrorActualizacion(f"La versión {version} tiene un error en {rel} "
                                         f"(línea {e.lineno}); no se instala.")
    return version, ficheros


# ------------------------------------------------------------------ #
# Aplicación                                                          #
# ------------------------------------------------------------------ #
def aplicar(paquete, reiniciar=True):
    """Verifica e instala un paquete. Devuelve la versión instalada; si algo no
    cuadra, lanza ErrorActualizacion sin haber tocado el firmware."""
    if not _lock_instalar.acquire(blocking=False):
        raise ErrorActualizacion("Ya hay una actualización en curso.")
    try:
        actual = leer_version()
        os.makedirs(ESTADO_DIR, exist_ok=True)
        # Dentro de /home, como el proyecto: os.replace es atómico en el mismo disco
        staging = os.path.join(ESTADO_DIR, 'nuevo')
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(os.path.join(ESTADO_DIR, 'firma'), ignore_errors=True)
        os.makedirs(staging)
        try:
            version, ficheros = _extraer(paquete, staging)
            motivo = _compatibilidad(version, actual)
            if motivo:
                raise ErrorActualizacion(motivo)

            # Copia de lo que se va a sobrescribir y lista de lo que no existía
            shutil.rmtree(ANTERIOR, ignore_errors=True)
            os.makedirs(ANTERIOR)
            nuevos = []
            for rel in ficheros:
                origen = os.path.join(PROYECTO, rel)
                if os.path.isfile(origen):
                    copia = os.path.join(ANTERIOR, rel)
                    os.makedirs(os.path.dirname(copia), exist_ok=True)
                    shutil.copy2(origen, copia)
                else:
                    nuevos.append(rel)

            estado = {'fase': 'aplicando', 'version_nueva': version,
                      'version_anterior': actual, 'nuevos': nuevos,
                      'fecha': time.strftime('%Y-%m-%d %H:%M'), 'intentos': 0}
            with _lock_estado:
                _guardar_estado(estado)
            # VERSION la última: si se corta la luz a medias, la caja no
            # anuncia una versión que no tiene, y el guardián ve «aplicando»
            for rel in sorted(ficheros, key=lambda r: r == 'VERSION'):
                destino = os.path.join(PROYECTO, rel)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                os.replace(os.path.join(staging, rel), destino)
            os.sync()
            estado['fase'] = 'pendiente'
            with _lock_estado:
                _guardar_estado(estado)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            shutil.rmtree(os.path.join(ESTADO_DIR, 'firma'), ignore_errors=True)

        print(f"[Actualizador] Instalada la versión {version} (antes {actual}).")
        if reiniciar:
            threading.Thread(target=_reiniciar_servicio, daemon=True).start()
        return version
    finally:
        _lock_instalar.release()


def _reiniciar_servicio():
    time.sleep(2)   # que la respuesta llegue antes al navegador
    subprocess.Popen(['sudo', '-n', '/usr/bin/systemctl', 'restart', 'historias.service'],
                     start_new_session=True)


# ------------------------------------------------------------------ #
# Comprobación contra el repositorio                                  #
# ------------------------------------------------------------------ #
def _descargar(url, maximo, timeout=20):
    peticion = urllib.request.Request(url, headers={
        'User-Agent': f'StoryMaker/{leer_version()}', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(peticion, timeout=timeout) as r:
        datos = r.read(maximo + 1)
    if len(datos) > maximo:
        raise ErrorActualizacion("La descarga es más grande de lo esperado.")
    return datos


def ultima_comprobacion():
    return dict(_ultima)


def comprobar():
    """Lee el manifiesto. Actualiza y devuelve el resultado de la última comprobación."""
    actual = leer_version()
    resultado = {'fecha': time.strftime('%Y-%m-%d %H:%M'), 'ok': False, 'error': None,
                 'disponible': None, 'imagen': None}
    try:
        manifiesto = json.loads(_descargar(MANIFIESTO, 64 * 1024))
        imagen = manifiesto.get('imagen') or {}
        if imagen.get('version'):
            try:
                if tupla(imagen['version'])[:2] > tupla(actual)[:2]:
                    resultado['imagen'] = {'version': imagen['version'],
                                           'url': imagen.get('url', '')}
            except ValueError:
                pass
        act = manifiesto.get('actualizacion') or {}
        if act.get('version') and act.get('url') and act.get('sha256') \
                and _compatibilidad(act['version'], actual) is None:
            resultado['disponible'] = {'version': act['version'], 'url': act['url'],
                                       'sha256': act['sha256'].lower(),
                                       'notas': act.get('notas', '')}
        resultado['ok'] = True
    except urllib.error.HTTPError as e:
        resultado['error'] = (f"El repositorio no tiene información de actualizaciones "
                              f"(HTTP {e.code}).")
    except (urllib.error.URLError, OSError) as e:
        resultado['error'] = ("No se ha podido contactar con el repositorio de StoryMaker "
                              "(sin internet, o el servidor no responde). Prueba en un rato.")
        print(f"[Actualizador] Comprobación fallida: {e}")
    except (ValueError, AttributeError, ErrorActualizacion) as e:
        resultado['error'] = "La información de actualizaciones publicada no se entiende."
        print(f"[Actualizador] Manifiesto ilegible: {e}")
    _ultima.update(resultado)
    if resultado['disponible']:
        print(f"[Actualizador] Disponible la versión {resultado['disponible']['version']}.")
    return dict(_ultima)


def instalar_disponible():
    """Descarga e instala lo que encontró la última comprobación."""
    disp = _ultima.get('disponible')
    if not disp:
        raise ErrorActualizacion("No hay ninguna actualización pendiente de instalar.")
    try:
        datos = _descargar(disp['url'], MAX_PAQUETE, timeout=60)
    except (urllib.error.URLError, OSError):
        raise ErrorActualizacion("No se ha podido descargar la actualización. "
                                 "Comprueba la conexión y vuelve a intentarlo.")
    if hashlib.sha256(datos).hexdigest() != disp['sha256']:
        raise ErrorActualizacion("La descarga no coincide con la publicada (huella "
                                 "distinta). Vuelve a intentarlo más tarde.")
    os.makedirs(ESTADO_DIR, exist_ok=True)
    ruta = os.path.join(ESTADO_DIR, 'descarga.tar')
    with open(ruta, 'wb') as f:
        f.write(datos)
    try:
        version = aplicar(ruta)
    finally:
        try:
            os.unlink(ruta)
        except OSError:
            pass
    _ultima['disponible'] = None
    return version


def iniciar_comprobacion_periodica(cargar_config, modo_red):
    """Hilo en segundo plano: primera comprobación al poco de arrancar y luego
    una vez al día. Solo con WiFi de cliente (en modo AP no hay internet).
    Desactivable desde el portal (`buscar_actualizaciones` en config.json)."""
    def _bucle():
        time.sleep(90)   # que la red y la hora (NTP) estén listas
        while True:
            espera = 30 * 60
            try:
                activo = cargar_config().get('buscar_actualizaciones', True)
                if activo and modo_red() == 'client':
                    if comprobar()['ok']:
                        espera = 24 * 3600
            except Exception as e:
                print(f"[Actualizador] Error en la comprobación periódica: {e}")
            time.sleep(espera)
    threading.Thread(target=_bucle, daemon=True, name='actualizador').start()
