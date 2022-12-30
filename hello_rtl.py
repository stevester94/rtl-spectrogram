#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
from scipy.fft import fft, fftfreq, fftshift
import numpy as np



sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 104.7e6
sdr.gain = 'auto'


def get_samples_and_plot(_):
    # use matplotlib to estimate and plot the PSD
    ax.cla()
    n_samples = 1024*256
    samples = sdr.read_samples(n_samples)

    duration_secs = len(samples) / sdr.sample_rate

    N = len(samples)
    T = 1/sdr.sample_rate

    yf = fft(samples)
    xf = fftfreq(N, T) # Convenience function, Returns the frequency bin center freqs
    xf = fftshift(xf) # Convenience function, swaps the bins so that they can be directly plotted (Recall FFT output is kinda wonky pre-shift)
    yplot = fftshift(yf) # Have to shift the actual fft values too
    yplot = 1.0/N * np.abs(yplot) # Normalize the magnitude of FFT

    # Fs and Fc are divided by 1e6 to make the legends nicer, since they are both divided by the same factor this doesn't mess any math up
    # NFFT splits samples into 1024 "segments", idk what this really means though
    # ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    
    ax.plot(xf+sdr.center_freq, yplot)
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Relative power (dB)')

def get_center_freq():
    global sdr

    while True:
        new_freq_MHz = float(input("Enter frequency in MHz: "))
        new_freq_Hz = new_freq_MHz * 1e6
        sdr.center_freq = new_freq_Hz

cli = Thread(target=get_center_freq)
cli.start()

fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
ax = plt.subplot(111)
ani = FuncAnimation(fig, get_samples_and_plot, interval=1)
plt.show()

sdr.close()