import numpy as np

class Fast_PhaseLockedLoop:
    def __init__( self, K_i, K_p, K_0, pll_f, fs, f_multiplier=1 ) -> None:
        self.lastSinOut = 0

        self.fs = fs
        self.f_multiplier = f_multiplier

        # LF State
        self.K_p = K_p
        self.K_i = K_i
        self.lf_integrator = 0

        # NCO State
        self.K_0 = K_0
        self.nco_f = pll_f
        self.nco_theta = 0
        self.nco_theta_multi = 0
        self.nco_phaseEstimate = 0

    def proc( self, in_, ):
        # Phase Detector
        e_D = in_ * self.lastSinOut

        # Loop Filter
        self.lf_integrator += self.K_i * e_D / self.fs
        e_F = self.K_p*e_D + self.lf_integrator

        # NCO
        self.nco_theta += 2*np.pi*self.nco_f/self.fs + self.K_0 * e_F
        self.nco_theta_multi += self.f_multiplier * (2*np.pi*self.nco_f/self.fs + self.K_0 * e_F)
        if self.nco_theta > 2*np.pi:
            self.nco_theta -= 2*np.pi

        cosOut = np.cos( self.nco_theta_multi  )
        sinOut = -np.sin( self.nco_theta  )

        self.lastSinOut = sinOut
        return cosOut, sinOut, e_D, e_F
