#! /usr/bin/env python3

import time
import numpy as np

import sounddevice as sd

from utils import signalGenerator

fs = 44100
sg = signalGenerator( frequency=10000, sample_rate=44100 )

from queue import Queue



os = sd.OutputStream(channels=1, samplerate=fs)


bufferLen = 44100
start = time.time()

# while time.time() - start < 10.0:
#     # print( "Gen" )
#     x = np.array( [next(sg) for _ in range(bufferLen)] )
#     x = x.astype( np.float32 )
#     if not os.active:
#         os.start()
#     os.write( x )


# q = Queue( maxsize=10000 )

# def callback(outdata, frames, time, status):
#     if status:
#         print(status)

#     ar = np.array( [q.get() for _ in range(len(outdata))] )
#     ar = ar.reshape( [len(ar), 1] )
#     outdata[:] = ar

# start = time.time()
# os = sd.OutputStream(channels=1, samplerate=fs, blocksize=100, callback=callback)
# os.start()


# while time.time() - start < 10.0:
#     q.put( next(sg) )


from utils import AudioBuffer

ab = AudioBuffer()

block = [ next(sg) for _ in range(int(1/10000*44100)) ]
while time.time() - start < 10.0:
    ab.put( block )