#! /usr/bin/env python3

import time
import numpy as np

import sounddevice as sd

from utils import UltraSigGen

fs = 44100
sg = UltraSigGen( frequency=10000, sampleRate=44100 )

from queue import Queue



os = sd.OutputStream(channels=1, samplerate=fs)


bufferLen = 44100
start = time.time()


from utils import AudioBuffer

ab = AudioBuffer()

# block = [ next(sg) for _ in range(int(1/10000*44100)) ]
block = []

for _ in range(10):
    block.extend( sg.get( 44100 ) )
while time.time() - start < 10.0:
    # block = sg.get( 44100 )
    ab.put( block )