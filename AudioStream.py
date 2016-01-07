import wave
import numpy as np
from .Range import Range, RangeQueue


class AudioStream:
    def __init__(self):
        # this props are set at construction time and do not change
        self.nChannels = 0
        self.sampleRate = 0
        self.length = 0
        pass

    # subclass should override next methods
    def read(self, outBuffer, start=0, length=None, outRangeQueue=None):
        """
        write on outBuffer[start:start+length]
        return number of written frames
        """
        pass

    def seek(self, pos):
        pass

    def pos(self):
        pass


class AudioStream_WaveFile(AudioStream):
    """
    read signed integer wave files
    to get signed integer wave file use:

      ffmpeg -i inputFile -acodec pcm_s16le outputFile.wav
      afconvert inputFile -d LEI16 -o outputFile.wav
      avconv -i inputFile -acodec pcm_s16le outputFile.wav
      
    """
    def __init__(self, filename):
        super().__init__()
        self.wf = wave.open(filename, 'rb')  # returns a Wave_read object
        self.nChannels = self.wf.getnchannels()
        self.length = self.wf.getnframes()
        self.sampleRate = self.wf.getframerate()
        self.samplewidth = self.wf.getsampwidth()
        self.sampleType_numpy = self.getSampleType(self.samplewidth)
        self.normCoeff = np.iinfo(self.sampleType_numpy).max
        self._pos = 0

    def read(self, outBuffer, start=0, length=None, outRangeQueue=None):
        assert(outBuffer.shape[0] == self.nChannels)
        if(length is None):
            length = outBuffer.shape[1]
        assert(start + length <= outBuffer.shape[1])

        toRead = np.minimum(self.length - self._pos, length)

        # read toRead frames with interlaved channels (2*toRead samples)
        data = self.wf.readframes(toRead)  
        data_np = np.fromstring(data, dtype=self.sampleType_numpy)
        outBuffer[:, start:start + toRead] = data_np.reshape((self.nChannels, -1), order='F')
        outBuffer[:, start:start + toRead] = outBuffer[:, start:start + toRead] / self.normCoeff
        outBuffer[:, start + toRead:] = 0
        self._pos += toRead

        if(outRangeQueue is not None):
            outRangeQueue.push(Range(self._pos-toRead, self._pos))

        return toRead

    def getSampleType(self, samplewidth):
        if(samplewidth == 1):
            return np.int8
        elif(samplewidth == 2):
            return np.int16
        elif(samplewidth == 4):
            return np.int32

    def seek(self, pos):
        assert(pos >= 0)
        pos = np.minimum(pos, self.length)
        self.wf.setpos(pos)
        self._pos = pos

    def pos(self):
        return self._pos
