#! /usr/bin/env python3
# PLL in an SDR

# Import the necessary packages and modules
import matplotlib.pyplot as plt
import numpy as np

from cython_impl.pll import PhaseLockedLoop

if __name__ == "__main__":
    k = 1
    N = 15
    K_p = 0.2667
    K_i = 0.0178
    K_0 = 1

    t = np.arange( 199, dtype=int )
    input_signal = np.cos(2*np.pi*(k/N)*t + np.random.normal(0, 0.1, size=len(t)) + np.pi) # Sprinkle in phase noise
    input_signal +=  np.random.normal(0, 0.1, size=len(t)) # AWGN

    #mode = "time"
    mode = "plot"


    if mode == "plot":
        e_D = [] #phase-error output
        cos_out = [0]



        pll = PhaseLockedLoop( K_i, K_p, K_0, k/N )
        for n in range(199):
            _cos_out, _sin_out, _e_D = pll.proc( input_signal[n] )

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
    
    elif mode == "time":
        import timeit


        L = 10000
        iters = 2
        total = L*len(input_signal)
        def thing():
            pll = PhaseLockedLoop( K_i, K_p, K_0, k/N )
            for _ in range(L):
                for x in input_signal:
                    _cos_out, _sin_out, _e_D = pll.proc( x )
                    # cos_out.append( _cos_out )
                    # e_D.append( _e_D )

        avg_seconds = timeit.timeit( thing, number=iters )/iters
        avg_samps_per_second = total/avg_seconds

        print( "avg seconds:", avg_seconds, "avg_samps_per_second", avg_samps_per_second )
