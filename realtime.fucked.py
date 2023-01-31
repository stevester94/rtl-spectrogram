#!/usr/bin/env python3
# FM demodulator based on I/Q (quadrature) samples

import struct, numpy, sys, math
from rtlsdr import *
from scipy.signal import resample_poly, firwin, bilinear, lfilter, decimate
import sounddevice as sd


MAX_DEVIATION = 200000 # Hz
INPUT_RATE = 256000
DEVIATION_X_SIGNAL = 0.99 / (math.pi * MAX_DEVIATION / (INPUT_RATE / 2))

remaining_data = b''

# configure device
sdr = RtlSdr()
sdr.sample_rate = INPUT_RATE
sdr.center_freq = 104.7e6
sdr.gain = 'auto'

while True:
    iqdata = sdr.read_samples(8192)
	iqdata = iqdata - 127.5
	iqdata = iqdata / 128.0
    angles = numpy.angle(iqdata)

    # Determine phase rotation between samples
    # (Output one element less, that's we always save last sample
    # in remaining_data)
    rotations = numpy.ediff1d(angles)

    # Wrap rotations >= +/-180º
    rotations = (rotations + numpy.pi) % (2 * numpy.pi) - numpy.pi

    # Convert rotations to baseband signal 
    output_raw = numpy.multiply(rotations, DEVIATION_X_SIGNAL)
    output_raw = numpy.clip(output_raw, -0.999, +0.999)

    # Scale to signed 16-bit int
    output_raw = numpy.multiply(output_raw, 32767)
    output_raw = output_raw.astype(int)
    # output_raw = decimate(output_raw, int(sdr.sample_rate/32000))

    # sd.play(output_raw, 32000, blocking=False)

    # Missing: low-pass filter and deemphasis filter
    # (result may be noisy)

    # Output as raw 16-bit, 1 channel audio
    bits = struct.pack(('<%dh' % len(output_raw)), *output_raw)

    sys.stdout.buffer.write(bits)