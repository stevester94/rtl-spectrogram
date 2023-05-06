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

k = 1
N = 15
K_p = 0.2667
K_i = 0.0178
K_0 = 1

t = np.arange( 99, dtype=int )
input_signal = np.cos(2*np.pi*(k/N)*t + np.pi)

integrator_out = 0
phase_estimate = np.zeros(100)
e_D = [] #phase-error output
e_F = [] #loop filter output
sin_out = np.zeros(100)
cos_out = np.ones(100)

pd = PhaseDetector()
lf = LoopFilter( K_i, K_p )
nco = NumericallyControlledOscillator( K_0 )

for n in range(99):
    # phase detector
    try:
        e_D.append( pd.proc( input_signal[n], sin_out[n] ) )
    except IndexError:
        e_D.append(0)


    #loop filter
    e_F.append( lf.proc( e_D[n] ))

    phase_estimate[n+1] = nco.proc( e_F[n] )

    sin_out[n+1] = -np.sin(2*np.pi*(k/N)*(n+1) + phase_estimate[n])
    cos_out[n+1] = np.cos(2*np.pi*(k/N)*(n+1) + phase_estimate[n])



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