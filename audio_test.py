#! /usr/bin/env python3

import ossaudiodev
import numpy as np

import sounddevice as sd


duration_secs = 10
fs = 44100
f_Hz = 6e3
amplitude = 0.25
t = np.arange(fs*duration_secs)
x = amplitude*np.sin(t*f_Hz)

sd.play(x, fs, blocking=True)
