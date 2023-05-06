#! /usr/bin/env python3
# PLL in an SDR

# Import the necessary packages and modules
import matplotlib.pyplot as plt
import numpy as np


class PhaseDetector:
    def __init__(self) -> None:
        pass

    def proc( self, sigIn, sigOut ):
        return sigIn * sigOut


class LoopFilter:
    def __init__( self, K_i, K_p ) -> None:
        self.K_i = K_i
        self.K_p = K_p
        self.integrator = 0
    
    def proc( self, e_D ):
        self.integrator += K_i * e_D

        return self.K_p * e_D + self.integrator

class NumericallyControlledOscillator:
    def __init__( self, K_0 ) -> None:
        self.prevPhaseEstimate = 0
        self.K_0 = K_0

    def proc( self, e_F ):
        prev = self.prevPhaseEstimate
        new = prev + self.K_0 * e_F
        self.prevPhaseEstimate = new

        return prev
    

class PhaseLockedLoop:
    def __init__( self, K_i, K_p, K_0, pll_f ) -> None:
        self.pd = PhaseDetector()
        self.lf = LoopFilter( K_i, K_p )
        self.nco = NumericallyControlledOscillator( K_0 )

        self.last_sin_out = 0
        self.last_phase_estimate = 0
        self.pll_f = pll_f


    """
    The original code for this seemed pretty interested in delaying the output by one sample (or something along those lines)
    I took that all out and it appears to still work fine
    """
    def proc( self, in_, n ):
        _e_D = self.pd.proc( in_, self.last_sin_out )

        #loop filter
        _e_F = self.lf.proc( _e_D )

        _phase_estimate = self.nco.proc( _e_F )        

        # These were originally n+1
        _sin_out = -np.sin(2*np.pi*self.pll_f*(n) + _phase_estimate)
        _cos_out = np.cos(2*np.pi*self.pll_f*(n) + _phase_estimate)

        self.last_sin_out = _sin_out

        return _cos_out, _sin_out, _e_D


k = 1
N = 15
K_p = 0.2667
K_i = 0.0178
K_0 = 1

t = np.arange( 199, dtype=int )
input_signal = np.cos(2*np.pi*(k/N)*t +  np.pi)
input_signal += np.random.normal(0, 0.1, size=len(t)) # Noise

e_D = [] #phase-error output
cos_out = [0]



pll = PhaseLockedLoop( K_i, K_p, K_0, k/N )
for n in range(199):
    _cos_out, _sin_out, _e_D = pll.proc( input_signal[n], n )

    cos_out.append( _cos_out )
    e_D.append( _e_D )



# Create a Figure
fig = plt.figure()

# Set up Axes
ax1 = fig.add_subplot(211)
ax1.plot(cos_out, label='PLL Output')
plt.grid()
ax1.plot(input_signal, label='Input Signal')
plt.legend()
ax1.set_title('Waveforms')

# Show the plot
#plt.show()

ax2 = fig.add_subplot(212)
ax2.plot( e_D )
plt.grid()
ax2.set_title('Filtered Error')
plt.show()