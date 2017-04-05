import numpy as np
from .Nodes.PitchTrackerNode import PitchTrackerBase
from .AudioBuffer import RingBuffer
import pyPitchTracking


class PitchTrackerFramed(PitchTrackerBase):

    def __init__(self, frame_size, hop_size):
        super().__init__()

        self.frame_size = frame_size
        self.hop_size = hop_size
        self.framer = RingBuffer(1, 2 * frame_size)
        self.tmpBuffer = np.zeros((1, frame_size), dtype=np.float32)
        self.f0 = 0
        self.voiced = False

    def process(self, x):
        """
        Extract pitch from audio buffer x.

        Parameters
        ----------
        x : numpy array float32 dim=2 shape=1,n
            array of samples

        Returns
        -------
        f0 : float
            fundamental frequency
        voiced : float {0, 1}
            a flag, 1 for pitched signal
        """
        if(len(x[0]) > self.hop_size):
            raise ValueError("len(x[0]) > hop_size")

        self.framer.write(x)

        # since (len(x) < self.hop_size) process at max 1 frame per call (usually less)
        if(self.framer.available() >= self.frame_size):
            self.framer.read(self.tmpBuffer)
            self.framer.advance_read_index(self.hop_size)

            self.f0, self.voiced = self.pitch_track(self.tmpBuffer[0])

        return self.f0, self.voiced

    def pitch_track(self, x):
        """Interface for the pitch tracking function, override in subclasses."""
        return 0, True

    def clear(self):
        """
        Reset the framer.

        Remember to call this if overriding.
        """
        self.framer.clear()

    def latency(self):
        """Return latency in number of samples."""
        return 0


class PitchTrackerDetContext:
    """
    Base class for a deterministic PitchTracker Context.

    It is expected to perform some kind of smoothing of data coming from the
    deterministic pitch tracker based on Yin (for each frame, a f0 estimate and an aperiodicity value)
    """

    def __init__(self, ap_thresh=0.2):
        self.context_type = 'det'  # for usage checking
        self.ap_thresh = ap_thresh

    def push(self, f0, ap):
        voiced = ap < self.ap_thresh
        return f0, voiced

    def clear(self):
        """Reset any internal state."""
        pass

    def latency(self):
        """Number of latency frames."""
        return int(0)


class PitchTrackerProbContext:
    """
    Base class for a probabilistic PitchTracker context.

    It is expected to perform some kind of smoothing of data coming from the
    probabilistic pitch tracker based on pYin
    for each frame:
    - a numpy array of f0 estimate and
    - relative numpy array of probability values
    """

    def __init__(self):
        self.context_type = 'prob'  # for usage checking
        pass

    def push(self, f0, p):
        i = np.argmax(p)
        return f0[i], True

    def clear(self):
        """Reset any internal state."""
        pass

    def latency(self):
        """Number of latency frames."""
        return int(0)


class PitchTrackerYin(PitchTrackerFramed):
    def __init__(self, sample_rate, frame_size=1024, hop_size=512, max_freq=1500, thresh=0.1,
                 context=PitchTrackerDetContext()):
        super().__init__(frame_size=frame_size, hop_size=hop_size)

        if(not context.context_type == 'det'):
            raise ValueError("You should use a subclass of PitchTrackerDetContext as context")

        self.yin = pyPitchTracking.PyPitchTrackerYin(sample_rate, max_freq=max_freq, thresh=thresh)
        self.context = context

    def pitch_track(self, x):
        f0, ap = self.yin.process(self.tmpBuffer[0])
        f0, voiced = self.context.push(f0, ap)
        return f0, voiced

    def latency(self):
        return int(.5 * self.frame_size + self.hop_size * self.context.latency())

    def clear(self):
        super().clear()
        self.context.clear()


class PitchTrackerPYin(PitchTrackerFramed):
    def __init__(self, sample_rate, frame_size=1024, hop_size=512, max_freq=1500, min_weight=0.01,
                 context=PitchTrackerProbContext()):
        super().__init__(frame_size=frame_size, hop_size=hop_size)

        if(not context.context_type == 'prob'):
            raise ValueError("You should use a subclass of PitchTrackerProbContext as context")

        self.yin = pyPitchTracking.PyPitchTrackerYin(sample_rate, max_freq=max_freq, min_weight=min_weight)
        self.context = context

    def pitch_track(self, x):
        f0, prob = self.yin.process_prob(self.tmpBuffer[0])
        f0, voiced = self.context.push(f0, prob)
        return f0, voiced

    def latency(self):
        return int(.5 * self.frame_size + self.hop_size * self.context.latency())

    def clear(self):
        super().clear()
        self.context.clear()
