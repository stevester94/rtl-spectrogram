#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np


fig, axes = plt.subplots( nrows=2, ncols=2, sharex=False, figsize=(20,8), facecolor='#DEDEDE' )
fig.suptitle( "My PLL" )


# Differs from the math, no K_D?
def phaseErrorDetector( inSig, outSig ):
    return inSig * outSig

prevIntegral = 0
def loopFilter( K_P, K_j, e_D ):
    global prevIntegral

    proportional = K_P * e_D
    integrator =  prevIntegral + K_j*e_D
    prevIntegral = integrator

    return proportional + integrator

prevNCO = 0
prev_e_F = 0
def numericallyControlledOscillator( K_0, e_F ):
    global prevNCO
    global prev_e_F

    NCO = prevNCO + K_0 * prev_e_F

    prevNCO = NCO
    prev_e_F = e_F

    return NCO

K_P = 0.2667
K_0 = 1
K_j = 0.0178




t = np.linspace(0, 1, num=1000)
ref_signal = np.sin(2 * np.pi * 10 * t)

# Generate a noisy input signal, pi/4 rads out of phase
sigIn = np.cos(2 * np.pi * 10 * t + np.random.normal(0, 0.1, size=len(t))  + np.pi/4  )

list_phaseOut = [0]
list_sigOut = [0]
list_phaseErr = [0]
for i,x in enumerate(sigIn):
    e_D = phaseErrorDetector( x, list_sigOut[-1] )
    e_F = loopFilter( K_P, K_j, e_D )
    phaseOut = numericallyControlledOscillator( K_0, e_F )
    sigOut = -np.sin( 2*np.pi*10 + phaseOut )

    list_phaseOut.append( phaseOut )
    list_sigOut.append( sigOut )
    list_phaseErr.append( e_D )


ax_sigIn = axes[0,0]
ax_sigOut = axes[1,0]
ax_phaseError = axes[0,1]

ax_sigIn.set_title( "sigIn" )
ax_sigOut.set_title( "sigOut" )
ax_phaseError.set_title( "phaseError" )

ax_sigIn.plot( sigIn )
ax_sigOut.plot( list_sigOut )
ax_phaseError.plot( list_phaseErr )

plt.show()