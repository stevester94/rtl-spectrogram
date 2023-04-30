import numpy as np

def signalGenerator():
    frequency = 10000  # 10 KHz
    sample_rate = 44100  # CD-quality audio
    amplitude = 0.999  # We are floats, idk if/how this matters
    duration = 1.0/frequency # Duration doesn't matter for frontend

    while True:
        t = np.linspace(0,duration, int(duration*sample_rate))
        X = amplitude * np.sin(2*np.pi*frequency*t)
        X = X.tolist()

        for x in X:
            yield x