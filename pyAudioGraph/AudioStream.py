import wave
import numpy as np
from .Range import Range


class AudioStream:
    def __init__(self):
        # this props are set at construction time and do not change
        self.nchannels = 0
        self.sample_rate = 0
        self.length = 0
        pass

    # subclass should override next methods
    def read(self, out_buffer, start=0, length=None, out_range_queue=None):
        """
        write on out_buffer[start:start+length]
        return number of written frames
        """
        pass

    def seek(self, pos):
        pass

    def pos(self):
        pass


class AudioStreamWaveFile(AudioStream):
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
        self.nchannels = self.wf.getnchannels()
        self.length = self.wf.getnframes()
        self.sample_rate = self.wf.getframerate()
        self.samplewidth = self.wf.getsampwidth()
        self.sampleType_numpy = self._get_sample_type(self.samplewidth)
        self.normCoeff = np.iinfo(self.sampleType_numpy).max
        self._pos = 0

    def read(self, out_buffer, start=0, length=None, out_range_queue=None):
        assert(out_buffer.shape[0] == self.nchannels)
        if(length is None):
            length = out_buffer.shape[1]
        assert(start + length <= out_buffer.shape[1])

        to_read = np.minimum(self.length - self._pos, length)

        # read to_read frames with interlaved channels (2*to_read samples)
        data = self.wf.readframes(to_read)
        data_np = np.fromstring(data, dtype=self.sampleType_numpy)
        out_buffer[:, start:start + to_read] = data_np.reshape((self.nchannels, -1), order='F')
        out_buffer[:, start:start + to_read] = out_buffer[:, start:start + to_read] / self.normCoeff
        out_buffer[:, start + to_read:] = 0
        self._pos += to_read

        if(out_range_queue is not None):
            out_range_queue.push(Range(self._pos - to_read, self._pos))

        return to_read

    def _get_sample_type(self, samplewidth):
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

    def __del__(self):
        self.wf.close()
