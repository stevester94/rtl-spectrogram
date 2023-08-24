import numpy as np

class PhaseDetector:
    def __init__(self) -> None:
        pass

    def proc( self, sigIn, sigOut ):
        return sigIn * sigOut

# Yes, this one is immediate in the original
class LoopFilter:
    def __init__( self, K_i, K_p, fs ) -> None:
        self.K_i = K_i
        self.K_p = K_p
        self.integrator = 0
        self.fs = fs
    
    def proc( self, e_D ):
        self.integrator += self.K_i * e_D / self.fs
        return self.K_p * e_D + self.integrator

    

class NumericallyControlledOscillator:
    def __init__( self, K_0, f, fs, f_multiplier=1 ) -> None:
        self.K_0 = K_0
        self.f = f
        self.fs = fs
        self.theta = 0
        self.theta_multi = 0
        self.phaseEstimate = 0
        self.f_multiplier = f_multiplier

    def proc( self, e_F ):
        self.theta += 2*np.pi*self.f/self.fs + self.K_0 * e_F
        self.theta_multi += self.f_multiplier*(2*np.pi*self.f/self.fs + self.K_0 * e_F)
        if self.theta > 2*np.pi:
            self.theta -= 2*np.pi
        if self.theta_multi > 2*np.pi:
            self.theta_multi -= 2*np.pi
        
        cosOut = np.cos( self.theta_multi  )
        sinOut = -np.sin( self.theta  )
        return cosOut, sinOut
    

class PhaseLockedLoop:
    def __init__( self, K_i, K_p, K_0, pll_f, fs, f_multiplier=1 ) -> None:
        self.pd = PhaseDetector()
        self.lf = LoopFilter( K_i, K_p, fs )
        self.nco = NumericallyControlledOscillator( K_0, pll_f, fs, f_multiplier )
        self.lastSinOut = 0
    def proc( self, in_, ):
        e_D = self.pd.proc( in_, self.lastSinOut )

        e_F = self.lf.proc( e_D )
        
        cosOut, sinOut  = self.nco.proc(e_F)
        self.lastSinOut = sinOut
        return cosOut, sinOut, e_D, e_F