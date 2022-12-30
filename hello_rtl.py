#! /usr/bin/env python3

from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread



sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 104.7e6
sdr.gain = 'auto'


def get_samples_and_plot(_):
    # use matplotlib to estimate and plot the PSD
    ax.cla()
    samples = sdr.read_samples(256*1024)
    ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    # ax.xlabel('Frequency (MHz)')
    # ax.ylabel('Relative power (dB)')

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