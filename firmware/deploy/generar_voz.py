#!/usr/bin/env python3
"""
generar_voz.py — Genera los avisos de red con la voz de Elvira (edge-tts).

Se ejecuta en el PC, no en la Pi, y deja los clips en firmware/data/voz/,
que viajan con el firmware y en la imagen. Hacen falta grabados de antemano:
en el primer arranque del Voice HAT la caja está en AP, sin internet, justo
cuando tiene que decir a qué red conectarse. modules/anuncio_red.py los
encadena; si falta alguno, cae a espeak.

Requisitos: edge-tts (pip) y ffmpeg con libmp3lame.
USO:
  python3 generar_voz.py
Regenerar cuando cambie un texto de CLIPS y hacer commit de data/voz/.
"""
import asyncio
import os
import subprocess
import sys
import tempfile

import edge_tts

VOZ = "es-ES-ElviraNeural"
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'voz')

# Nombre del clip → texto. Las cifras van sueltas para dictar la IP cifra a cifra.
CLIPS = {
    'ap':        "Sin red wifi. Conéctate a la red StoryMaker guion Setup.",
    'conectada': "Conectada. Mi dirección es",
    'punto':     "punto",
    'puerto':    "dos puntos, cinco mil.",
    'repito':    "Repito:",
    '0': "cero", '1': "uno", '2': "dos", '3': "tres", '4': "cuatro",
    '5': "cinco", '6': "seis", '7': "siete", '8': "ocho", '9': "nueve",
}

# Recorta el silencio que edge-tts deja al principio y al final, dejando un
# margen corto para que al encadenar clips las palabras no se atropellen.
RECORTE = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,"
           "areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,"
           "areverse")


async def generar(nombre, texto):
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        bruto = tmp.name
    try:
        await edge_tts.Communicate(texto, VOZ).save(bruto)
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-y', '-i', bruto, '-af', RECORTE,
             '-ac', '1', '-ar', '24000', '-c:a', 'libmp3lame', '-b:a', '48k',
             os.path.join(DESTINO, f'{nombre}.mp3')],
            check=True)
    finally:
        os.unlink(bruto)


async def main():
    os.makedirs(DESTINO, exist_ok=True)
    for nombre, texto in CLIPS.items():
        await generar(nombre, texto)
        print(f"  {nombre}.mp3  ← {texto}")
    print(f"{len(CLIPS)} clips en {os.path.abspath(DESTINO)}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
