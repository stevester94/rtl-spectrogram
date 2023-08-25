import numpy as np

cdef class Fast_Cython_v2_PhaseLockedLoop:

    cdef double lastSinOut

    cdef double fs
    cdef double f_multiplier

    # LF State
    cdef double K_p
    cdef double K_i
    cdef double lf_integrator

    # NCO State
    cdef double K_0
    cdef double nco_f
    cdef double nco_theta
    cdef double nco_theta_multi
    cdef double nco_phaseEstimate


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

    def proc( self, double in_, ):
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
        if self.nco_theta_multi > 2*np.pi:
            self.nco_theta_multi -= 2*np.pi

        cosOut = np.cos( self.nco_theta_multi  )
        sinOut = -np.sin( self.nco_theta  )

        self.lastSinOut = sinOut
        return cosOut, sinOut, e_D, e_F
