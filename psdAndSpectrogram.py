import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, fftshift, rfft, rfftfreq
import numpy as np

from scipy.signal import resample

class PsdAndSpectrogram:
    def __init__(self, psdAx, spectrogramAx, sampleRate, centerFreq, fullscale, nBins, realSignal=False ) -> None:
        self.psdAx = psdAx
        self.spectrogramAx = spectrogramAx
        self.A = np.zeros((100, nBins))
        self.colorbar = None
        self.sampleRate = sampleRate
        self.centerFreq = centerFreq
        self.fullscale = fullscale
        self.nBins = nBins
        self.realSignal = realSignal

    def process( self, samples ):
        self.psdAx.cla()
        self.spectrogramAx.cla()

        N = len(samples)
        T = 1/self.sampleRate

        yf = fft(samples)

        # yf = resample( yf, self.nBins )
        xf = fftfreq(self.nBins, T) # Convenience function, Returns the frequency bin center freqs

        xf = fftshift(xf) # Convenience function, swaps the bins so that they can be directly plotted (Recall FFT output is kinda wonky pre-shift)
        yplot = fftshift(yf) # Have to shift the actual fft values too
        yplot = 1.0/N * np.abs(yplot) # Normalize the magnitude of FFT

        # Put in terms of dBFS
        yplot = 10*np.log10(yplot/self.fullscale)

        self.A = np.roll(self.A, 1, axis = 0)
        self.A[0] = yplot
        # i += 1
        # A = np.roll(A, 1)s

        # A = np.concatenate([yplot, A[:, -1]])

        # Fs and Fc are divided by 1e6 to make the legends nicer, since they are both divided by the same factor this doesn't mess any math up
        # NFFT splits samples into 1024 "segments", idk what this really means though
        # ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
        

        x_axis = (self.centerFreq - self.sampleRate/2, self.centerFreq + self.sampleRate/2)
        self.psdAx.plot(xf+self.centerFreq, yplot)
        self.psdAx.set_xlabel('Frequency (MHz)')
        self.psdAx.set_ylabel('dBFS')
        self.psdAx.set_ylim(-70, 0)
        self.psdAx.set_xlim(x_axis[0], x_axis[1])

        y_axis = (100, 0)
        pos = self.spectrogramAx.imshow(self.A, cmap='hot', interpolation='none',  aspect='auto', extent=[x_axis[0], x_axis[1], y_axis[0], y_axis[1]],
            vmin=-70, vmax=0)
        self.spectrogramAx.set_xlabel('Frequency (MHz)')
        self.spectrogramAx.set_ylabel('Time')
        if self.colorbar is None:
            # colorbar = fig.colorbar(pos, ax=spectrogramAx)
            pass

"""
Doesn'd do anything with resampling to match nBins
"""
class RealPsdAndSpectrogram:
    def __init__(self, psdAx, spectrogramAx, sampleRate, centerFreq, fullscale, nBins ) -> None:
        self.psdAx = psdAx
        self.spectrogramAx = spectrogramAx
        self.A = None
        self.colorbar = None
        self.sampleRate = sampleRate
        self.centerFreq = centerFreq
        self.fullscale = fullscale
        self.nBins = nBins

    def process( self, samples ):


        self.psdAx.cla()
        self.spectrogramAx.cla()

        N = len(samples)
        T = 1/self.sampleRate

        yf = rfft(samples)

        # yf = resample( yf, self.nBins )
        xf = rfftfreq(len(samples), T) # Convenience function, Returns the frequency bin center freqs

        # print( len(samples), len(xf), len(yf) )
        # return

        # print( "nbins", self.nBins, "len(labels)", len(xf), "len(bins)", len(yf), "len(samples)", len(samples) )
        # return

        # xf = fftshift(xf) # Convenience function, swaps the bins so that they can be directly plotted (Recall FFT output is kinda wonky pre-shift)
        # yplot = fftshift(yf) # Have to shift the actual fft values too
        yplot = 1.0/N * np.abs(yf) # Normalize the magnitude of FFT

        # Put in terms of dBFS
        yplot = 10*np.log10(yplot/self.fullscale)

        if self.A is None or self.A.shape[1] != len(xf):
            self.A = np.zeros((100, len(xf)))

        self.A = np.roll(self.A, 1, axis = 0)
        self.A[0] = yplot

        # Fs and Fc are divided by 1e6 to make the legends nicer, since they are both divided by the same factor this doesn't mess any math up
        # NFFT splits samples into 1024 "segments", idk what this really means though
        # ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
        

        x_axis = (0, self.centerFreq + self.sampleRate/2)
        self.psdAx.plot(xf+self.centerFreq, yplot)
        self.psdAx.set_xlabel('Frequency (MHz)')
        self.psdAx.set_ylabel('dBFS')
        self.psdAx.set_ylim(-70, 0)
        self.psdAx.set_xlim(x_axis[0], x_axis[1])

        y_axis = (100, 0)
        pos = self.spectrogramAx.imshow(self.A, cmap='hot', interpolation='none',  aspect='auto', extent=[x_axis[0], x_axis[1], y_axis[0], y_axis[1]],
            vmin=-70, vmax=0)
        self.spectrogramAx.set_xlabel('Frequency (MHz)')
        self.spectrogramAx.set_ylabel('Time')
        if self.colorbar is None:
            # colorbar = fig.colorbar(pos, ax=spectrogramAx)
            pass