#! /usr/bin/env python3

from timeit import timeit
from utils import BetterSigGen, UltraSigGen
import cyth.utils as cyth

L = 2000
N = 10000
I = 10

def do_bsg():
    bsg = BetterSigGen( 51e3, 256e3, 0 )
    for _ in range(N):
        bsg.get( L )

T = timeit( do_bsg, number=I )
total_samps = L*N*I
avg_secs = T/I
avg_samps_per_sec = L*N / avg_secs

print( f"BetterSigGen: TotalSecs={T:.2f}, AvgSecs={avg_secs:.2f}, AvgMSampsPerSeconds={avg_samps_per_sec/1e6:.2f}" )

def do_bsg():
    bsg = UltraSigGen( 51e3, 256e3, 0 )
    for _ in range(N):
        bsg.get( L )

T = timeit( do_bsg, number=I )
total_samps = L*N*I
avg_secs = T/I
avg_samps_per_sec = L*N / avg_secs

print( f"UltraSigGen: TotalSecs={T:.2f}, AvgSecs={avg_secs:.2f}, AvgMSampsPerSeconds={avg_samps_per_sec/1e6:.2f}" )