try:
    import pyaudio
    pyaudio_available = True
except ImportError:
    pyaudio_available = False


class AudioDriver:
    def __init__(self, world):
        self.world = world
        self.sample_rate = world.sample_rate
        self.buf_len = world.buf_len
        self.nchannels = world.nchannels

        if(pyaudio_available):
            self._p = pyaudio.PyAudio()
            self._stream = self._p.open(format=pyaudio.paFloat32,
                                        channels=world.nchannels,
                                        rate=world.sample_rate,
                                        frames_per_buffer=world.buf_len,
                                        input=True,
                                        output=True,
                                        stream_callback=self.callback,
                                        start=False)

    def start(self):
        assert(pyaudio_available)
        self._stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        assert(frame_count == self.buf_len)
        out_data = self.world.run(in_data)
        return (out_data, pyaudio.paContinue)

    def stop(self):
        assert(pyaudio_available)
        self._stream.stop_stream()

    def dispose(self):
        if(pyaudio_available):
            self._stream.close()
            self._p.terminate()
