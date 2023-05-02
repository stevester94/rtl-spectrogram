#!/usr/bin/env python3
# FM demodulator based on I/Q (quadrature) samples

# import struct, math, random, sys, numpy, filters, time
import math
import random
import numpy as np

from utils import signalGenerator

class PLL:
    def __init__( self, sampleRate ) -> None:
        self.pll = math.pi - random.random() * 2 * math.pi
        self.last_pilot = 0.0
        self.tau = 2 * math.pi
        self.STEREO_CARRIER = 38000 # Hz
        self.sampleRate = sampleRate
        self.tau = 2 * math.pi
        self.deviation_avg = math.pi - random.random() * 2 * math.pi
        self.last_deviation_avg = self.deviation_avg

    def advance( self, detected_pilot ):
        out = np.arange( len(detected_pilot), dtype=np.float32 )

        CHEAT = True

        if CHEAT:
            if not hasattr(self, "siggen1"):
                print( "Init cheater siggens" )
                self.siggen1 = signalGenerator( 38e3, self.sampleRate )
                self.siggen2 = signalGenerator( 10e3, self.sampleRate )
            for i in range(len(out)):
                out[i] = next(self.siggen1)
                # out[i] += next(self.siggen2)
            
            return out
        else:
            for n in range(len(detected_pilot)):
                self.pll = (self.pll + self.tau * self.STEREO_CARRIER / self.sampleRate) % self.tau

                out[n] = self.pll
                ############ Carrier PLL #################

                # Detect pilot zero-crossing
                cur_pilot = detected_pilot[n]
                zero_crossed = (cur_pilot * self.last_pilot) <= 0
                self.last_pilot = cur_pilot
                if not zero_crossed:
                    continue

                # When pilot is at 90º or 270º, carrier should be around 180º
                # t=0    => cos(t) = 1,  cos(2t) = 1
                # t=π/2  => cos(t) = 0,  cos(2t) = -1
                # t=π    => cos(t) = -1, cos(2t) = 1
                # t=-π/2 => cos(t) = 0,  cos(2t) = -1
                ideal = math.pi
                deviation = self.pll - ideal
                if deviation > math.pi:
                    # 350º => -10º
                    deviation -= self.tau
                self.deviation_avg = 0.99 * self.deviation_avg + 0.01 * deviation
                rotation = self.deviation_avg - self.last_deviation_avg
                self.last_deviation_avg = self.deviation_avg

                if abs(self.deviation_avg) > math.pi / 8:
                    # big phase deviation, reset PLL
                    # print("Resetting PLL", file=sys.stderr)
                    self.pll = ideal
                    self.pll = (self.pll + self.tau * self.STEREO_CARRIER / self.sampleRate) % self.tau
                    self.deviation_avg = 0.0
                    self.last_deviation_avg = 0.0

                # Translate rotation to frequency deviation e.g.
                # cos(tau + 3.6º) = cos(1.01 * tau)
                # cos(tau - 9º) = cos(tau * 0.975)
                            #
                # Overcorrect by 5% to (try to) sync phase,
                            # otherwise only the frequency would be synced.

                self.STEREO_CARRIER /= (1 + (rotation * 1.05) / self.tau)

            
            return np.cos(out)


'''
optimized = "-o" in sys.argv
debug_mode = "-d" in sys.argv
disable_pll = "--disable-pll" in sys.argv
if disable_pll:
    optimized = False

if optimized:
    import fastfm # Cython

MAX_DEVIATION = 200000.0 # Hz
INPUT_RATE = 256000
OUTPUT_RATE = 32000

if debug_mode:
    OUTPUT_RATE=256000

DECIMATION = INPUT_RATE / OUTPUT_RATE
assert DECIMATION == math.floor(DECIMATION)

FM_BANDWIDTH = 15000 # Hz
STEREO_CARRIER = 38000 # Hz
DEVIATION_X_SIGNAL = 0.999 / (math.pi * MAX_DEVIATION / (INPUT_RATE / 2))

pll = math.pi - random.random() * 2 * math.pi
last_pilot = 0.0
deviation_avg = math.pi - random.random() * 2 * math.pi
last_deviation_avg = deviation_avg
tau = 2 * math.pi

# Downsample mono audio
decimate1 = filters.decimator(DECIMATION)

# Deemph + Low-pass filter for mono (L+R) audio
lo = filters.deemphasis(INPUT_RATE, 75, FM_BANDWIDTH, 120)

# Downsample jstereo audio
decimate2 = filters.decimator(DECIMATION)

# Deemph + Low-pass filter for joint-stereo demodulated audio (L-R)
lo_r = filters.deemphasis(INPUT_RATE, 75, FM_BANDWIDTH, 120)

# Band-pass filter for stereo (L-R) modulated audio
hi = filters.band_pass(INPUT_RATE,
    STEREO_CARRIER - FM_BANDWIDTH, STEREO_CARRIER + FM_BANDWIDTH, 120)

# Filter to extract pilot signal
pilot = filters.band_pass(INPUT_RATE,
    STEREO_CARRIER / 2 - 100, STEREO_CARRIER / 2 + 100, 120)

last_angle = 0.0
remaining_data = b''

while True:
    # Ingest 0.1s worth of data
    data = sys.stdin.buffer.read((INPUT_RATE * 2) // 10)
    if not data:
        break
    data = remaining_data + data

    if len(data) < 4:
        remaining_data = data
        continue

    # Save one sample to next batch, and the odd byte if exists
    if len(data) % 2 == 1:
        print("Odd byte, that's odd", file=sys.stderr)
        remaining_data = data[-3:]
        data = data[:-1]
    else:
        remaining_data = data[-2:]

    samples = len(data) // 2

    # Find angle (phase) of I/Q pairs
    iqdata = numpy.frombuffer(data, dtype=numpy.uint8)
    iqdata = iqdata - 127.5
    iqdata = iqdata / 128.0
    iqdata = iqdata.view(complex)

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

    # At this point, output_raw contains two audio signals:
    # L+R (mono-compatible) and L-R (joint-stereo) modulated in AM-SC,
    # carrier 38kHz
    
    # Downsample and low-pass L+R (mono) signal
    output_mono = lo.feed(output_raw)
    output_mono = decimate1.feed(output_mono)

    # Filter pilot tone
    detected_pilot = pilot.feed(output_raw)

    # Separate ultrasonic L-R signal by high-pass filtering
    output_jstereo_mod = hi.feed(output_raw)

    # Demodulate L-R, which is AM-SC with 53kHz carrier

    if optimized:
        output_jstereo, pll, STEREO_CARRIER, \
        last_pilot, deviation_avg, last_deviation_avg = \
            fastfm.demod_stereo(output_jstereo_mod,
                        pll,
                        STEREO_CARRIER,
                        INPUT_RATE,
                        detected_pilot,
                        last_pilot,
                        deviation_avg,
                        last_deviation_avg)
    else:
        output_jstereo = []

        for n in range(0, len(output_jstereo_mod)):
            # Advance carrier
            pll = (pll + tau * STEREO_CARRIER / INPUT_RATE) % tau

            # Standard demodulation
            output_jstereo.append(math.cos(pll) * output_jstereo_mod[n])

            if disable_pll:
                continue
    
            ############ Carrier PLL #################

            # Detect pilot zero-crossing
            cur_pilot = detected_pilot[n]
            zero_crossed = (cur_pilot * last_pilot) <= 0
            last_pilot = cur_pilot
            if not zero_crossed:
                continue
    
            # When pilot is at 90º or 270º, carrier should be around 180º
            # t=0    => cos(t) = 1,  cos(2t) = 1
            # t=π/2  => cos(t) = 0,  cos(2t) = -1
            # t=π    => cos(t) = -1, cos(2t) = 1
            # t=-π/2 => cos(t) = 0,  cos(2t) = -1
            ideal = math.pi
            deviation = pll - ideal
            if deviation > math.pi:
                # 350º => -10º
                deviation -= tau
            deviation_avg = 0.99 * deviation_avg + 0.01 * deviation
            rotation = deviation_avg - last_deviation_avg
            last_deviation_avg = deviation_avg
    
            if abs(deviation_avg) > math.pi / 8:
                # big phase deviation, reset PLL
                # print("Resetting PLL", file=sys.stderr)
                pll = ideal
                pll = (pll + tau * STEREO_CARRIER / INPUT_RATE) % tau
                deviation_avg = 0.0
                last_deviation_avg = 0.0

            # Translate rotation to frequency deviation e.g.
            # cos(tau + 3.6º) = cos(1.01 * tau)
            # cos(tau - 9º) = cos(tau * 0.975)
                        #
            # Overcorrect by 5% to (try to) sync phase,
                        # otherwise only the frequency would be synced.

            STEREO_CARRIER /= (1 + (rotation * 1.05) / tau)

    
    # Downsample, Low-pass/deemphasis demodulated L-R
    output_jstereo = lo_r.feed(output_jstereo)
    output_jstereo = decimate2.feed(output_jstereo)

    assert len(output_jstereo) == len(output_mono)

    # Scale to 16-bit and divide by 2 for channel sum
    output_mono = numpy.multiply(output_mono, 32767 / 2.0)
    output_jstereo = numpy.multiply(output_jstereo, 32767 / 2.0)

    # Output stereo by adding or subtracting joint-stereo to mono
    output_left = output_mono + output_jstereo
    output_right = output_mono - output_jstereo

    if not debug_mode:
        # Interleave L and R samples using NumPy trickery
        output = numpy.empty(len(output_mono) * 2, dtype=output_mono.dtype)
        output[0::2] = output_left
        output[1::2] = output_right
        output = output.astype(int)
    else:
        output = numpy.empty(len(output_mono) * 3, dtype=output_mono.dtype)
        output[0::3] = output_mono
        output[1::3] = output_jstereo
        output[2::3] = numpy.multiply(detected_pilot, 32767)
        output = output.astype(int)

    sys.stdout.buffer.write(struct.pack('<%dh' % len(output), *output))


'''