#! /usr/bin/env python3

import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import time
import numpy as np
import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from av import VideoFrame
from av import AudioFrame
import fractions    

from utils import UltraSigGen

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()

# Create a class for an audio track
class AudioStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.time = 0
        self.audioGen = UltraSigGen( 10e3, 44.1e3 )
        self.samplerate = 44100
        self.samples = 1000 # Num to get each buffer


    async def recv(self):

        # Handle timestamps properly
        if hasattr(self, "_timestamp"):
            self._timestamp += self.samples
            wait = self._start + (self._timestamp / self.samplerate) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0

        # create empty data by default
        # data = np.zeros(self.samples).astype(np.int16)
        data = self.audioGen.get( self.samples )
        data *= 1000
        data = data.astype( np.int16 )

        # Only get speaker data if we have some in the buffer
        # <sig gen here>

        # To convert to a mono audio frame, we need the array to be an array of single-value arrays for each sample (annoying)
        data = data.reshape(data.shape[0], -1).T
        # Create audio frame
        frame = AudioFrame.from_ndarray(data, format='s16', layout='mono')

        # Update time stuff
        frame.pts = self._timestamp
        frame.sample_rate = self.samplerate
        frame.time_base = fractions.Fraction(1, self.samplerate)

        # Return
        return frame
    



async def debug():
    ROOT = os.path.dirname(__file__)
    player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))

    track = player.audio

    f = track.recv()
    print( await f )

    f = track.recv()
    print( await f )

asyncio.run( debug() )