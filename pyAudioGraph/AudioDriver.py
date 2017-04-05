"""Audio Driver module implements the audio callback using pyAudio (portaudio)."""

# This conditional import is needed for passing Travis CI compilation
try:
    import pyaudio
    pyaudio_available = True
except ImportError:
    pyaudio_available = False


class AudioDriver:
    """Wraps the pyAudio functionality needed to manage the audio thread."""

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
        """Start the audio thread."""
        assert(pyaudio_available)
        self._stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        """
        Called within the audio thread.

        Parameters
        ----------
        in_data : binary buffer interlaved
            input samples from the audio input device
        frame_count : int
            number of frames
        time_info : dictionary
            contains keys input_buffer_adc_time, current_time, and output_buffer_dac_time
        status : PaCallbackFlag
            can be paInputUnderflow, paInputOverflow, paOutputUnderflow, paOutputOverflow, paPrimingOutput

        Returns
        -------
        tuple
            (out_data, flag)

        out_data is an interlaved binary buffer (frame_count * channels * bytes-per-channel)
        flag must be either paContinue, paComplete or paAbort
        """
        assert(frame_count == self.buf_len)
        out_data = self.world.run(in_data)
        return (out_data, pyaudio.paContinue)

    def stop(self):
        """Stop the audio thread."""
        assert(pyaudio_available)
        self._stream.stop_stream()

    def dispose(self):
        if(pyaudio_available):
            self._stream.close()
            self._p.terminate()
