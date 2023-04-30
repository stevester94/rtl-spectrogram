import math
import numpy as np
from scipy.signal import resample, decimate
from scipy.signal import butter, lfilter, freqz

from utils import signalGenerator
# My Method
def build_butter_filter(cutoff, fs, order=24):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_filter(b,a,x):
    y = lfilter(b, a, x)
    return y


class FmDemodulator:
    def __init__(self, maxDeviation=200000, sampleRate=256000, doFilter=True, doResample=True, filterCutoff=44100 ) -> None:
        self.sampleRate = sampleRate
        self.deviationXSignal = 0.99 / (math.pi * maxDeviation / (self.sampleRate / 2))
        self.remaining_data = None
        self.doFilter = doFilter
        self.doResample = doResample
        # His Method
        # lo_pass = filters.low_pass(INPUT_RATE, INPUT_RATE, 48)

        self.b,self.a = build_butter_filter(filterCutoff, self.sampleRate)

        self.sigGen = signalGenerator()

    def demodulateSamples( self, iqdata ):
        # iqdata = iqdata - 127.5
        # iqdata = iqdata / 128.0

        # We are dropping a single sample between buffers
        if self.remaining_data is not None:
            iqdata = np.concatenate( [self.remaining_data, iqdata] )
        self.remaining_data = iqdata[-1:]


        angles = np.angle(iqdata)

        # Determine phase rotation between samples
        # (Output one element less, that's we always save last sample
        # in remaining_data)
        rotations = np.ediff1d(angles)

        # Wrap rotations >= +/-180º
        rotations = (rotations + np.pi) % (2 * np.pi) - np.pi

        # Convert rotations to baseband signal 
        output_raw = np.multiply(rotations, self.deviationXSignal)
        output_raw = np.clip(output_raw, -0.999, +0.999)

        """
        Attempt to downsample to 44100Hz.

        Still studders but its actually not horrible
        """
        if self.doFilter:
            output_raw = apply_filter(self.b, self.a, output_raw)

        if self.doResample:
            output_raw = resample(output_raw, int(len(output_raw) * 44100/self.sampleRate))



        # return [ next(self.sigGen) for _ in range(len(iqdata))]

        return output_raw    