#!/usr/bin/env python3
# FM demodulator based on I/Q (quadrature) samples
# https://epxx.co/artigos/pythonfm_en.html

import struct, numpy, sys, math
from scipy.signal import resample, decimate
import sounddevice as sd
from scipy.signal import butter, lfilter, freqz
from rtlsdr import *
import asyncio

from fmDemodulator import FmDemodulator

class FmTuner:
    def __init__(self, maxDeviation=200000, sampleRate=256000) -> None:
        self.sampleRate = sampleRate

        self.fmDemod = FmDemodulator( maxDeviation, sampleRate )
        
        # configure device
        self.sdr = RtlSdr()
        self.sdr.sample_rate = self.sampleRate
        self.sdr.center_freq = 104.7e6
        self.sdr.gain = 'auto'

    def getAudioSamples( self ):
        iqdata = self.sdr.read_samples(self.sampleRate)
        return self.fmDemod.demodulateSamples( iqdata )
    
    async def asyncAudioGenerator( self ):
        async for samps in self.sdr.stream( self.sampleRate ):
            yield self.fmDemod.demodulateSamples( samps )

    async def run( self ):
        async for audio in self.asyncAudioGenerator():
            sd.play(audio, 44100, blocking=False)



if __name__ == "__main__":
    fm = FmTuner()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fm.run())