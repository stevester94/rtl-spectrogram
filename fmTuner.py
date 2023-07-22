#!/usr/bin/env python3
# FM demodulator based on I/Q (quadrature) samples
# https://epxx.co/artigos/pythonfm_en.html

from rtlsdr import *
import asyncio
import numpy as np
from fmDemodulator import FmDemodulator

from collections import deque

from audioBuffer import AudioBuffer


SAVE_IQ = False
SAVE_IQ_N_SAMPS = 5 * 256000
SAVE_IQ_PATH = "saved_iq.complex128" # Numpy adds .npy to the path

LOAD_IQ = False
LOAD_IQ_PATH = "saved_iq.complex128.npy"

if SAVE_IQ:
    print( f"Will save {SAVE_IQ_N_SAMPS} samples to {SAVE_IQ_PATH}" )
    saved_iq = np.array( [], dtype=np.complex128 )

if LOAD_IQ:
    LOAD_IQ_IDX = 0
    loaded_iq = np.load( LOAD_IQ_PATH )

class FmTuner:
    def __init__(self, maxDeviation=200000, sampleRate=256000) -> None:
        self.sampleRate = sampleRate

        self.fmDemod = FmDemodulator( maxDeviation, sampleRate )
        
        # configure device
        self.sdr = RtlSdr()
        self.sdr.sample_rate = self.sampleRate
        self.sdr.center_freq = 95.1e6
        self.sdr.gain = 'auto'

        self.ab = AudioBuffer()
        # self.ab.start()

    def __del__(self):
        self.ab.stop()


    def getAudioSamples( self, N=None ):
        if N is None: N = self.sampleRate

        iqdata = self.sdr.read_samples( N )
        return self.fmDemod.demodulateSamples( iqdata )
    
    async def asyncAudioGenerator( self, N=2000 ):
        global saved_iq
        global SAVE_IQ
        global LOAD_IQ_IDX

        async for samps in self.sdr.stream( N ):
            if SAVE_IQ:
                saved_iq = np.concatenate( [saved_iq, samps] )

                if len(saved_iq) >= SAVE_IQ_N_SAMPS:
                    print( "Saving IQ to", SAVE_IQ_PATH )
                    np.save( SAVE_IQ_PATH, saved_iq )
                    SAVE_IQ = False
            if LOAD_IQ:
                old_samps = samps
                samps = loaded_iq[LOAD_IQ_IDX:LOAD_IQ_IDX+len(old_samps)]
                LOAD_IQ_IDX += len(old_samps)

            yield self.fmDemod.demodulateSamples( samps )

    async def run( self ):
        async for audio in self.asyncAudioGenerator():
            self.ab.put( audio )
            # sd.play(audio, 44100, blocking=False)



if __name__ == "__main__":
    fm = FmTuner()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fm.run())
