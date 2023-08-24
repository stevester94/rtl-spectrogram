#! /usr/bin/env python3
# PLL in an SDR

# Import the necessary packages and modules
import matplotlib.pyplot as plt
import numpy as np

from Orig_PLL import PhaseLockedLoop
from Fast_PLL import Fast_PhaseLockedLoop

import timeit


L = 10000
iters = 2
total = L*len(input_signal)

def thing():
    pll = PhaseLockedLoop( K_i, K_p, K_0, k/N, 1 )
    for _ in range(L):
        for x in input_signal:
            pll.proc( x )

avg_seconds = timeit.timeit( thing, number=iters )/iters
avg_samps_per_second = total/avg_seconds

print( "avg seconds:", avg_seconds, "avg_samps_per_second", avg_samps_per_second )
