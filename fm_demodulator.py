import numpy as np


class FM_Demodulator:
    def __init__(self, input_rate_sps, max_deviation_Hz=200000) -> None:
        self.holdover = None
        self.DEVIATION_X_SIGNAL = 0.99 / (np.pi * max_deviation_Hz / (input_rate_sps / 2))
        pass

    def work(self, X):
        if self.holdover is not None:
            X = np.concatenate([self.holdover, X])
        self.holdover = X[-1:]

        # Not sure what the point of this is
        # X = X - 127.5
        # X = X / 128.0
        angles = np.angle(X)

        # Determine phase rotation between samples
        # (Output one element less, that's we always save last sample
        # in remaining_data)
        rotations = np.ediff1d(angles)

        # Wrap rotations >= +/-180º
        rotations = (rotations + np.pi) % (2 * np.pi) - np.pi

        # Convert rotations to baseband signal 
        output_raw = np.multiply(rotations, self.DEVIATION_X_SIGNAL)
        output_raw = np.clip(output_raw, -0.999, +0.999)

        return output_raw