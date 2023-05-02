#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import math

from psdAndSpectrogram import PsdAndSpectrogram, RealPsdAndSpectrogram
from fmDemodulator import FmDemodulator
from utils import AudioBuffer
sdr = RtlSdr()

# configure device
# sdr.sample_rate = 256000
sdr.sample_rate = 256000*1
sdr.center_freq = 104.7e6
sdr.gain = 'auto'

fullscale = math.sqrt(2**8 + 2**8)

fmDemod = FmDemodulator( sampleRate=sdr.sample_rate, doResample=False, doFilter=True, filterCutoff=60000 )
audioBuffer = AudioBuffer()
nBins = 81920


# while True:
#     samples = sdr.read_samples(nBins) # 8192 is necessary
#     audio = fmDemod.demodulateSamples( samples )
#     audioBuffer.put( audio )

def get_samples_and_plot(_):
    global rfDisp
    global fmDemod
    global audioDisp
    global plotDecimator

    
    samples = sdr.read_samples(nBins) # 8192 is necessary

    audio = fmDemod.demodulateSamples( samples )
    # audioBuffer.put( audio )
    
    # sd.play(audio, 44100, blocking=False) # Too slow?

    rfDisp.centerFreq = sdr.center_freq
    rfDisp.process( samples )

    audioDisp.process( audio )
    # audioPsdAx.cla()
    # audioPsdAx.plot( audio )
    # print( audio )
    # print( len(audio) )

def get_center_freq():
    global sdr

    while True:
        new_freq_MHz = float(input("Enter frequency in MHz: "))
        new_freq_Hz = new_freq_MHz * 1e6
        sdr.center_freq = new_freq_Hz

cli = Thread(target=get_center_freq)
cli.start()



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

rfDisp = PsdAndSpectrogram( rfPsdAx, rfSpectrogramAx, sdr.sample_rate, sdr.center_freq, fullscale, nBins )
audioDisp = RealPsdAndSpectrogram( audioPsdAx, audioSpectrogramAx, sampleRate=sdr.sample_rate, centerFreq=0, fullscale=1, nBins=nBins//2 )


ani = FuncAnimation(fig, get_samples_and_plot, interval=1)
plt.show()

sdr.close()