#! /usr/bin/env python3

import time
import numpy as np

import sounddevice as sd

from utils import signalGenerator

fs = 44100
sg = signalGenerator()



# bufferLen = 44100
# start = time.time()
# while time.time() - start < 10.0:
#     # print( "Gen" )
#     x = [next(sg) for _ in range(bufferLen)]
#     # print( "Play" )
#     sd.play(x, fs, blocking=True)


def callback(outdata, frames, time, status):
    if status:
        print(status)
    ar = np.array( [next(sg) for _ in range(len(outdata))] )
    ar = ar.reshape( [len(ar), 1] )
    outdata[:] = ar


os = sd.OutputStream(channels=1, samplerate=fs, callback=callback)
os.start()


while True:
    time.sleep(10)