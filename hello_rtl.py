#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
from scipy.fft import fft, fftfreq, fftshift
import numpy as np
import math


sdr = RtlSdr()

# configure device
sdr.sample_rate = 3.2e6
sdr.center_freq = 104.7e6
sdr.gain = 'auto'

A = np.zeros((100, 8192))

fullscale = math.sqrt(2**8 + 2**8)

colorbar = None

def get_samples_and_plot(_):
    global A
    global colorbar

    psd_ax.cla()
    spectrogram_ax.cla()

    n_samples = 8192
    samples = sdr.read_samples(n_samples)

    N = len(samples)
    T = 1/sdr.sample_rate

    yf = fft(samples)
    xf = fftfreq(N, T) # Convenience function, Returns the frequency bin center freqs
    xf = fftshift(xf) # Convenience function, swaps the bins so that they can be directly plotted (Recall FFT output is kinda wonky pre-shift)
    yplot = fftshift(yf) # Have to shift the actual fft values too
    yplot = 1.0/N * np.abs(yplot) # Normalize the magnitude of FFT

    # Put in terms of dBFS
    yplot = 10*np.log10(yplot/fullscale)

    A = np.roll(A, 1, axis = 0)
    A[0] = yplot
    # i += 1
    # A = np.roll(A, 1)s

    # A = np.concatenate([yplot, A[:, -1]])

    # Fs and Fc are divided by 1e6 to make the legends nicer, since they are both divided by the same factor this doesn't mess any math up
    # NFFT splits samples into 1024 "segments", idk what this really means though
    # ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    

    x_axis = (sdr.center_freq - sdr.sample_rate/2, sdr.center_freq + sdr.sample_rate/2)
    psd_ax.plot(xf+sdr.center_freq, yplot)
    psd_ax.set_xlabel('Frequency (MHz)')
    psd_ax.set_ylabel('dBFS')
    psd_ax.set_ylim(-70, 0)
    psd_ax.set_xlim(x_axis[0], x_axis[1])

    y_axis = (100, 0)
    pos = spectrogram_ax.imshow(A, cmap='hot', interpolation='none',  aspect='auto', extent=[x_axis[0], x_axis[1], y_axis[0], y_axis[1]],
        vmin=-70, vmax=0)
    spectrogram_ax.set_xlabel('Frequency (MHz)')
    spectrogram_ax.set_ylabel('Time')
    if colorbar is None:
        # colorbar = fig.colorbar(pos, ax=spectrogram_ax)
        pass





def get_center_freq():
    global sdr

    while True:
        new_freq_MHz = float(input("Enter frequency in MHz: "))
        new_freq_Hz = new_freq_MHz * 1e6
        sdr.center_freq = new_freq_Hz

cli = Thread(target=get_center_freq)
cli.start()

fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
psd_ax = plt.subplot(211)
spectrogram_ax = plt.subplot(212)

ani = FuncAnimation(fig, get_samples_and_plot, interval=1)
plt.show()

sdr.close()