#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import math

from psdAndSpectrogram import PsdAndSpectrogram, RealPsdAndSpectrogram
from fmDemodulator import FmDemodulator
from utils import AudioBuffer

from scipy import signal
from scipy.signal import butter, lfilter, freqz

from pll import PLL

from multiprocessing import Queue, Process

def apply_filter(b,a,x):
    y = lfilter(b, a, x)
    return y

fullscale = math.sqrt(2**8 + 2**8)

# we use this in order to take full advantage of multiprocessing. Pushes buffers of audio and RF at adjustable rates
class FmSource:
    def __init__( self, rfQ, audioQ, ) -> None:
        self.rfQ = rfQ
        self.audioQ = audioQ

        self.closeQ = Queue()

    def run( self ):
        self.p = Process( target=self._run )
        self.p.start()

    def stop( self ):
        self.closeQ.put( "STOP" )
        self.p.join()

    def _run( self ):
        sdr = RtlSdr()

        # configure device
        # sdr.sample_rate = 256000
        sdr.sample_rate = 256000*1
        sdr.center_freq = 104.7e6
        sdr.gain = 'auto'

        fmDemod = FmDemodulator( sampleRate=sdr.sample_rate, doResample=False, doFilter=False, filterCutoff=10000 )

        decimator = 0
        while True:
            # print( "LOOP" )
            samples = sdr.read_samples(nBins) # 8192 is necessary

            audio = fmDemod.demodulateSamples( samples )
            # pilot = apply_filter( b, a, audio )
            # stereoPilot = pll.advance( pilot )

            # stereoPilot = bsg.get( nBins )

            # if len(audio) == nBins:
            #     audio = audio + stereoPilot

            self.audioQ.put( audio )
            self.rfQ.put( samples )


            try:
                self.closeQ.get_nowait()
                break
            except:
                pass
        sdr.close()




nBins = 2**10


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

audio = None
samples = None

def get_samples_and_plot(_):
    global rfDisp
    global fmDemod
    global audioDisp
    global plotDecimator

    global rfQ
    global audioQ

    global audio
    global samples

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
        sdr.center_freq = new_freq_Hz

# cli = Thread(target=get_center_freq)
# cli.start()




rfQ = Queue( maxsize=1000 )
audioQ = Queue( maxsize=1000 )
fms = FmSource( audioQ=audioQ, rfQ=rfQ )
fms.run()

def loop():
    global audio
    global samples
    # audioBuffer = AudioBuffer()

    while True:
        audio = audioQ.get()
        samples = rfQ.get()

        # audioBuffer.put( audio )

        

looper = Thread(target=loop)
looper.start()



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


ani = FuncAnimation(fig, get_samples_and_plot, interval=1)
plt.show()
fms.stop()