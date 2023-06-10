#! /usr/bin/env python3

import argparse
import asyncio
import logging
import math
import struct
import json
import fractions
import time

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import AudioFrame
import numpy as np
from utils import UltraSigGen

# Create a class for an audio track
class AudioStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.time = 0
        self.audioGen = UltraSigGen( 10e3, 44.1e3 )
        self.samplerate = 44100
        self.samples = 10000 # Num to get each buffer


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
        data *= 32000
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

    # async def recv(self):
    #     frameLen = 44.1e3*0.01 # 10ms frames

    #     samps = self.audioGen.get( frameLen )
    #     samps *= 5000
    #     samps = samps.astype(np.int16)
    #     # samps = samps.reshape([1,-1])

    #     await asyncio.sleep(0.01)
    #     frame = AudioFrame(format='s16', layout='mono')
    #     frame.samples = len(samps)
    #     frame.layout = 1

    #     # frame = AudioFrame.from_ndarray( samps, layout="mono", format="s16" )
    #     frame.sample_rate = 44.1e3

    #     np.copyto(frame.planes[0].to_ndarray(), samps)



    #     # frame.time_base = fractions.Fraction(1, 44.1e3)

    #     return frame


# Create a signaling server using aiohttp
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Create a peer connection
    pc = RTCPeerConnection()

    # Add the audio track to the peer connection
    pc.addTrack(AudioStreamTrack())

    async def send_answer():
        # Create the session description
        recv = json.loads( await ws.receive_str() )
        logging.debug( f"SMACK: Got receive_str={recv} in send_answer")
        description = RTCSessionDescription(sdp=recv["sdp"], type="offer")

        logging.debug( f"SMACK: setRemoteDescription")
        await pc.setRemoteDescription(description)

        # Generate the answer
        logging.debug( f"SMACK: createAnswer")
        ans = await pc.createAnswer()

        logging.debug( f"SMACK: Answer: {ans}")

        logging.debug( f"SMACK: Set local description")
        await pc.setLocalDescription( ans )

        # Send the answer
        logging.debug( f"SMACK: sending answer (or something): {pc.localDescription.sdp}")
        payload = {
            "type": pc.localDescription.type,
            "sdp": pc.localDescription.sdp
        }
        payload = json.dumps( payload )
        await ws.send_str( payload )

    # Handle signaling messages
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            if msg.data == "offer":
                logging.debug( "Got str 'offer' on websocket. Doing send_answer()")
                await send_answer()
            elif msg.data == "close":
                await ws.close()
        elif msg.type == web.WSMsgType.ERROR:
            logging.error('Websocket connection closed with exception %s' % ws.exception())

    return ws


# class fugck():
#     def __init__(self):
#         self.audioGen = UltraSigGen( 10e3, 44.1e3 )

#     def recv(self):
#         frameLen = 44.1e3*0.01 # 10ms frames

#         samps = self.audioGen.get( frameLen )
#         samps *= 5000
#         samps = samps.astype(np.int16)
#         samps = samps.reshape([1,-1])
        

#         return AudioFrame.from_ndarray( samps, layout="mono" )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC audio stream backend")
    parser.add_argument("--port", type=int, default=8080, help="Port for the signaling server")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Create the signaling server
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)

    # Start the signaling server
    web.run_app(app, port=args.port)
