#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import math

from psdAndSpectrogram import PsdAndSpectrogram

sdr = RtlSdr()

# configure device
sdr.sample_rate = 3.2e6
sdr.center_freq = 104.7e6
sdr.gain = 'auto'

# A = np.zeros((100, 8192))

fullscale = math.sqrt(2**8 + 2**8)

# colorbar = None






def get_samples_and_plot(_):
    global disp
    n_samples = 8192
    samples = sdr.read_samples(n_samples)

    disp.centerFreq = sdr.center_freq
    disp.process( samples )






def get_center_freq():
    global sdr

    while True:
        new_freq_MHz = float(input("Enter frequency in MHz: "))
        new_freq_Hz = new_freq_MHz * 1e6
        sdr.center_freq = new_freq_Hz

cli = Thread(target=get_center_freq)
cli.start()

fig = plt.figure(figsize=(12,6), facecolor='#DEDEDE')
psdAx = plt.subplot(211)
spectrogramAx = plt.subplot(212)
disp = PsdAndSpectrogram( psdAx, spectrogramAx, sdr.sample_rate, sdr.center_freq, fullscale )


ani = FuncAnimation(fig, get_samples_and_plot, interval=1)
plt.show()

sdr.close()