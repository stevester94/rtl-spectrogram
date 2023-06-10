#! /usr/bin/env python3
# https://github.com/aiortc/aiortc/issues/571
import os
import sys

import asyncio
from aiohttp import web
import mimetypes
import math
import struct
import logging
import numpy as np

from fmTuner import FmTuner

HTML_DIR = os.path.join( os.getcwd(), "html" )

fmSource = FmTuner()

async def handle(request):
    path = request.path
    absPath = os.path.abspath( HTML_DIR + path )
    if os.path.isdir(absPath):
        absPath = os.path.abspath(os.path.join(absPath, "index.html"))

    try:
        with open(absPath, 'rb') as f:
            content = f.read()
        content_type, _ = mimetypes.guess_type(absPath)
        if content_type == 'text/html':
            headers = {'Content-Type': 'text/html'}
            headers['Content-Type'] += '; charset=utf-8'
        return web.Response(body=content, headers=headers)
    except FileNotFoundError:
        return web.Response(status=404)

async def audio_generator():
    frequency = 10000  # 10 KHz
    sample_rate = 44100  # CD-quality audio
    amplitude = 0.999  # We are floats, idk if/how this matters
    duration = 10 # Duration doesn't matter for frontend


    while True:
        t = np.linspace(0,duration, int(duration*sample_rate))
        x = amplitude * np.sin(2*np.pi*frequency*t)
        x = x.tolist()
        # data = struct.pack('<' + 'f' * len(x), *x)
        # data = x
        yield x
        await asyncio.sleep(duration)

async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for audio_data in fmSource.asyncAudioGenerator():
    # async for audio_data in audio_generator():
        data = struct.pack('<' + 'f' * len(audio_data), *audio_data)
        await ws.send_bytes(data)
    
    return ws

app = web.Application()
app.add_routes([
    web.get('/noise', wshandle),
    web.get('/{tail:.*}', handle),
])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, port=int(sys.argv[1]) )