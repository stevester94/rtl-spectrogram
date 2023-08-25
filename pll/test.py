#! /usr/bin/env python3

import sys, os
from typing import List, Tuple

from Orig_PLL import PhaseLockedLoop as Cyth_PhaseLockedLoop
from Fast_PLL import Fast_PhaseLockedLoop as Cyth_Fast_PhaseLockedLoop

from src.Orig_PLL import PhaseLockedLoop
from src.Fast_PLL import Fast_PhaseLockedLoop
from Fast_Cython_PLL import Fast_Cython_v2_PhaseLockedLoop

import numpy as np

import time

K = 1
duration_secs = 10 / K
in_f_Hz   = 10*K
fs = 256000

def speed_test_a_PLL( pll, n_iterations ) -> Tuple[ List[float], int ]:
    t = np.linspace(0,duration_secs, int(duration_secs*fs))
    in_sig    = np.cos( 2*np.pi * in_f_Hz*1.25 * t + 0 )

    times = []
    for _ in range(n_iterations):
        start = time.time()
        for idx in range(len(in_sig)):
            pll.proc( in_sig[idx] )
        end = time.time()

        times.append( end-start )
    
    totalTime_secs = sum( times )
    totalSamples = len(in_sig) * n_iterations
    avgSampsPerSecond = totalSamples/ totalTime_secs

    return times, len(in_sig), avgSampsPerSecond




K_p = 0.2667/10
K_i = 0.0178*100
K_0 = 1
in_f_Hz =  9900 
cyth_pll = Cyth_PhaseLockedLoop( K_i, K_p, K_0, in_f_Hz, fs )
cyth_fast_pll = Cyth_Fast_PhaseLockedLoop( K_i, K_p, K_0, in_f_Hz, fs )
pll = PhaseLockedLoop( K_i, K_p, K_0, in_f_Hz, fs )
fast_pll = Fast_PhaseLockedLoop( K_i, K_p, K_0, in_f_Hz, fs )

fast_pll_v2 = Fast_Cython_v2_PhaseLockedLoop( K_i, K_p, K_0, in_f_Hz, fs )

_, _, avg_sps = speed_test_a_PLL( fast_pll_v2, 5 )
print( "Fast PLL v2 avg Kilo samples per second:", avg_sps/1000.0 )

_, _, avg_sps = speed_test_a_PLL( cyth_pll, 5 )
print( "Original PLL Cythonized avg Kilo samples per second:", avg_sps/1000.0 )

_, _, avg_sps = speed_test_a_PLL( cyth_fast_pll, 5 )
print( "Fast PLL Cythonized avg Kilo samples per second:", avg_sps/1000.0 )

_, _, avg_sps = speed_test_a_PLL( pll, 5 )
print( "Original PLL avg Kilo samples per second:", avg_sps/1000.0 )

_, _, avg_sps = speed_test_a_PLL( fast_pll, 5 )
print( "Fast PLL avg Kilo samples per second:", avg_sps/1000.0 )