import queue
import sounddevice
import numpy as np

class AudioBuffer:
    def __init__(self, blocksize=100 ) -> None:
        self.blocksize = blocksize
        self.q = queue.Queue(maxsize=100000)
        self.os = sounddevice.OutputStream( blocksize=self.blocksize, channels=1, samplerate=44100, callback=lambda outdata,frames,time,status: self._callback( outdata, frames, time, status ) )
        self.buffer = np.array( [], dtype=np.float32 )
    
    def __del__( self ):
        if not self.os.stopped:
            self.os.stop()
    
    def put( self, block:np.ndarray ):
        block = np.array( block, dtype=np.float32 )

        self.buffer = np.concatenate( [self.buffer, block] )
        
        if len(self.buffer) < self.blocksize: # Block too small, stick it in remainder and wait
            return
    
        while len(self.buffer) >= self.blocksize: # Block is too big, shove rest in remainder and proceed
            chunk = self.buffer[:self.blocksize]
            self.buffer = self.buffer[self.blocksize:]
            self.q.put( chunk )

        if not self.os.active:
            self.os.start()

    def _callback( self, outdata, frames, time, status ):
        block = self.q.get()
        block = block.reshape( [self.blocksize, 1] )
        outdata[:] = block