#! /usr/bin/env python3

import argparse
import asyncio
import logging
import math
import json

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack


# Create a class for an audio track
class AudioStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()

    async def recv(self):
        # Sample rate of the audio stream (e.g., 48 kHz)
        sample_rate = 48000

        # Frequency of the audio tone (e.g., 440 Hz for A4)
        frequency = 440

        # Number of audio frames to generate
        frame_count = 480  # 10 milliseconds of audio frames

        # Duration of each audio frame in seconds
        frame_duration = 1 / sample_rate

        # Generate audio samples for the tone
        samples = []
        for _ in range(frame_count):
            t = self.time
            sample = int(32767 * math.sin(2 * math.pi * frequency * t))
            samples.extend(sample.to_bytes(2, "little"))
            self.time += frame_duration

        return bytes(samples)


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
        logging.debug( f"Got receive_str={recv} in send_answer")
        await pc.setRemoteDescription(RTCSessionDescription(sdp=recv, type="offer"))

        # Generate the answer
        logging.debug( f"createAnswer")
        ans = await pc.createAnswer()

        logging.debug( f"Answer: {ans}")

        logging.debug( f"Set local description")
        await pc.setLocalDescription( ans )

        # Send the answer
        logging.debug( f"sending answer (or something)")
        await ws.send_str(pc.localDescription.sdp)

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
