import numpy as np

cdef class BetterSigGen:
    cdef float theta
    cdef float frequency
    cdef float sampleRate

    def __init__( self, frequency, sampleRate, phase_rads=0 ) -> None:

        self.theta = phase_rads
        self.frequency = frequency
        self.sampleRate = sampleRate

    def get( self, int n ):
        # ret = np.zeros( n )

        cdef int i = 0

        while i < n:
            # ret[i] = np.sin( self.theta )
            # np.sin( self.theta )
            self.theta += 2*np.pi*self.frequency

            if self.theta > 2*np.pi:
                self.theta -= 2*np.pi
            
            i += 1

        # return ret