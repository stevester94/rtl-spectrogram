#!/usr/bin/env python3
# FM demodulator based on I/Q (quadrature) samples
# https://epxx.co/artigos/pythonfm_en.html

import struct, numpy, sys, math
from scipy.signal import resample, decimate
import sounddevice as sd
from scipy.signal import butter, lfilter, freqz
from rtlsdr import *
from fm_demodulator import FM_Demodulator

INPUT_RATE = 256000

def build_butter_filter(cutoff, fs, order=24):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_filter(b,a,x):
    y = lfilter(b, a, x)
    return y

b,a = build_butter_filter(22000, INPUT_RATE)


# configure device
sdr = RtlSdr()
sdr.sample_rate = INPUT_RATE
sdr.center_freq = 104.7e6
sdr.gain = 'auto'

# Configure Demodulator
demod = FM_Demodulator(INPUT_RATE)

holdover = None
while True:
    iqdata = sdr.read_samples(INPUT_RATE*2)

    output_raw = demod.work(iqdata)

    """
    Various methods of processing the audio signal. Note that all of these suffer
    decent amounts of studdering that do not appear to be a consequence of CPU.

    I think it's something to do with number of samples read in at a time
    """


    """
    No filtering, just slam the audio signal to the sound card at rate
    """
    # sd.play(output_raw, INPUT_RATE, blocking=False)

    """
    Filter the signal, based on the butter filter taps generated above
    But still send to sound card at rate.
    """
    output_raw = apply_filter(b, a, output_raw)
    sd.play(output_raw, INPUT_RATE, blocking=False)

    """
    Attempt to downsample to 44100Hz.

    Significant gaps on studder
    """
    # output_raw = apply_filter(b, a, output_raw)
    # output_raw = resample(output_raw, int(len(output_raw) * 44100/INPUT_RATE))
    # sd.play(output_raw, 44100, blocking=False)