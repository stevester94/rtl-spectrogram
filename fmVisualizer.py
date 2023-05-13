#! /usr/bin/env python3

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import math

from psdAndSpectrogram import PsdAndSpectrogram, RealPsdAndSpectrogram
from fmDemodulator import FmDemodulator

from scipy import signal
from scipy.signal import butter, lfilter, freqz

from pll import PLL
from rtlsdr import RtlSdr

from multiprocessing import Queue, Process
import asyncio

import json

def apply_filter(b,a,x):
    y = lfilter(b, a, x)
    return y

fullscale = math.sqrt(2**8 + 2**8)

# we use this in order to take full advantage of multiprocessing. Pushes buffers of audio and RF at adjustable rates
class FmSource:
    def __init__( self, rfQ, audioQ, ) -> None:
        self.rfQ = rfQ
        self.audioQ = audioQ

        self.commandQ = Queue()

    def run( self ):
        self.p = Process( target=self._run )
        self.p.start()

    def stop( self ):
        print( "FmSource stopping" )
        self.commandQ.put( {"command": "stop" } )
        print( "FmSource joining" )
        self.p.join()

    def tune( self, freq_Hz:float ):
        self.commandQ.put( {"command": "tune", "freq_Hz": freq_Hz} )

    async def _loop( self ):
        from audioBuffer import AudioBuffer
        audioBuffer = AudioBuffer()


        # configure device
        sdr = RtlSdr()
        sdr.sample_rate = 256000
        sdr.sample_rate = 256000*1
        sdr.center_freq = 104.7e6
        sdr.gain = 'auto'

        # Configure Demod
        fmDemod = FmDemodulator( sampleRate=sdr.sample_rate, doResample=True, doFilter=False, filterCutoff=10000 )

        decimator = 0
        async for samps in sdr.stream( nBins ):
            audio = fmDemod.demodulateSamples( samps )
            audioBuffer.put( audio )

            decimator += 1
            if decimator % 10 == 0:
                self.audioQ.put( audio )
                self.rfQ.put( samps )
                decimator = 0
            
            try:
                v = self.commandQ.get_nowait()
                if v["command"] == "stop":
                    print( "Internal close" )
                    self.rfQ.close()
                    self.audioQ.close()
                    return 
                    sdr.close()
                    print( "Internal close done" )
                
                elif v["command"] == "tune":
                    sdr.center_freq = v["freq_Hz"]


            except:
                pass


    def _run( self ):
        loop = asyncio.get_event_loop()
        loop.run_until_complete( self._loop() )



nBins = 2**15


# while True:
#     samples = sdr.read_samples(nBins) # 8192 is necessary
#     audio = fmDemod.demodulateSamples( samples )
#     audioBuffer.put( audio )


fs = 256000
sample_rate = fs
center_freq = 104.7e6

# # Pilot tone filtering
# f0 = 19e3  # Frequency to be removed from signal (Hz)
# Q = 30.0  # Quality factor
# # Design notch filter
# # b, a = signal.iirnotch(f0, Q, fs) # Notch filter
# b, a = signal.iirpeak(f0, Q, fs) # Notch pass

# pll = PLL( sdr.sample_rate )

# from utils import BetterSigGen
# bsg = BetterSigGen( 38e3, sdr.sample_rate )

def get_samples_and_plot(_):
    global rfQ
    global audioQ



    audio = audioQ.get()
    samples = rfQ.get()

    if samples is not None:
        rfDisp.centerFreq = center_freq
        rfDisp.process( samples )

    if audio is not None:
        audioDisp.process( audio )

def get_center_freq():
    global sdr

    while True:
        new_freq_MHz = float(input("Enter frequency in MHz: "))
        new_freq_Hz = new_freq_MHz * 1e6
        fms.tune( new_freq_Hz )

cli = Thread(target=get_center_freq)
cli.start()




rfQ = Queue( maxsize=0 )
audioQ = Queue( maxsize=0 )
fms = FmSource( audioQ=audioQ, rfQ=rfQ )
fms.run()


def audioLoop():
    from audioBuffer import AudioBuffer
    audioBuffer = AudioBuffer()

    while True:
        block = audioQ.get()

        audioBuffer.put( block )


fig, axes = plt.subplots( nrows=2, ncols=2, sharex=False, figsize=(20,8), facecolor='#DEDEDE' )
fig.suptitle( "FM Visualizer" )

rfPsdAx = axes[0,0]
rfSpectrogramAx = axes[1,0]
rfPsdAx.set_title( "RF PSD" )
rfSpectrogramAx.set_title( "RF Spectrogram" )

audioPsdAx = axes[0,1]
audioSpectrogramAx = axes[1,1]
audioPsdAx.set_title( "Audio PSD" )
audioSpectrogramAx.set_title( "Audio Spectrogram" )

rfDisp = PsdAndSpectrogram( rfPsdAx, rfSpectrogramAx, sample_rate, center_freq, fullscale, nBins )
audioDisp = RealPsdAndSpectrogram( audioPsdAx, audioSpectrogramAx, sampleRate=sample_rate, centerFreq=0, fullscale=1, nBins=705 )


ani = FuncAnimation(fig, get_samples_and_plot, interval=1 )
plt.show()
fms.stop()