import numpy as np

def signalGenerator( frequency=10000, sample_rate=44100 ):
    amplitude = 0.999  # We are floats, idk if/how this matters
    duration = 10 # Duration doesn't matter for frontend

    while True:
        t = np.linspace(0,duration, int(duration*sample_rate))
        X = amplitude * np.sin(2*np.pi*frequency*t)
        X = X.tolist()

        for x in X:
            yield x


class BetterSigGen:
    def __init__( self, frequency, sampleRate, phase_rads=0 ) -> None:

        duration = (1/frequency) * 10
        self.amplitude = 0.999
        self.frequency = frequency

        self.t = np.linspace(0,duration, int(duration*sampleRate))
        self.orig = self.amplitude * np.sin(2*np.pi*self.frequency*self.t + phase_rads)
        self._gen()

    def _gen( self ):
        self.x = self.orig
    
    def get( self, n ):
        out = np.array( [], dtype=np.float32 )

        while len(out) != n:
            grab = min( len(self.x), n - len(out) )
            out = np.concatenate( [out, self.x[:grab]])
            self.x = self.x[:grab]

            if len(self.x) == 0:
                self._gen()
        return out
    

class UltraSigGen:
    def __init__( self, frequency, sampleRate, phase_rads=0 ) -> None:

        self.theta = phase_rads
        self.amplitude = 0.999
        self.frequency = frequency
        self.sampleRate = sampleRate

        self.last_n = -1
        self.last_t = None
    def get( self, n )->np.ndarray:
        # We can cache the t vector and reuse if n stays the same (~50% speed increase!)
        if n != self.last_n:
            t = np.arange( n ) * (1/self.sampleRate)
            self.last_n = n
            self.last_t = t
        else:
            t = self.last_t
        out = self.amplitude * np.sin( 2*np.pi*self.frequency*t + self.theta )
        self.theta += 2*np.pi*self.frequency*n/self.sampleRate

        return out
    
    def setFrequency_Hz( self, frequency_Hz:float ) -> None:
        self.frequency = frequency_Hz

    def getFrequency_Hz( self ) -> float:
        return self.frequency 



if __name__ == "__main__":
    sg = BetterSigGen( 1, 100, np.pi/4 )

    out = []
    for _ in range(10):
        out.extend( sg.get(100) )
    
    import  matplotlib.pyplot as plt

    plt.plot( out )
    plt.show()