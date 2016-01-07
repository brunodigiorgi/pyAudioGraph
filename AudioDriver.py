import pyaudio


class AudioDriver:
    def __init__(self, world):
        self.world = world
        self.sampleRate = world.sampleRate
        self.bufLen = world.bufLen
        self.nChannels = world.nChannels

        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(format=pyaudio.paFloat32,
                                    channels=world.nChannels,
                                    rate=world.sampleRate,
                                    frames_per_buffer=world.bufLen,
                                    input=True,
                                    output=True,
                                    stream_callback=self.callback,
                                    start=False)

    def start(self):
        self._stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        assert(frame_count == self.bufLen)
        out_data = self.world.run(in_data)
        return (out_data, pyaudio.paContinue)

    def stop(self):
        self._stream.stop_stream()

    def dispose(self):
        self._stream.close()
        self._p.terminate()
