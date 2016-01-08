import numpy as np


def test_framer():
    from pyAudioGraph import RingBuffer

    nchannels = 2
    x = np.arange(60).reshape(nchannels, -1)
    ring_buffer = RingBuffer(nchannels, 60)
    ring_buffer.write(x[:, :10])
    ring_buffer.write(x[:, 10:])

    a = np.zeros(20).reshape(nchannels, -1)

    ring_buffer.read(a)
    a_expected = np.array([[0., 1., 2., 3., 4., 5., 6., 7., 8., 9.],
                           [30., 31., 32., 33., 34., 35., 36., 37., 38., 39.]])
    assert(np.allclose(a, a_expected))

    ring_buffer.advance_read_index(10)
    ring_buffer.read(a)
    a_expected = np.array([[10., 11., 12., 13., 14., 15., 16., 17., 18., 19.],
                           [40., 41., 42., 43., 44., 45., 46., 47., 48., 49.]])
    assert(np.allclose(a, a_expected))

    ring_buffer.advance_read_index(2)
    ring_buffer.read(a)
    a_expected = np.array([[12., 13., 14., 15., 16., 17., 18., 19., 20., 21.],
                           [42., 43., 44., 45., 46., 47., 48., 49., 50., 51.]])
    assert(np.allclose(a, a_expected))


def test_overlapper():
    from pyAudioGraph import RingBuffer

    nchannels = 2
    x = np.ones(60).reshape(nchannels, -1)
    ring_buffer = RingBuffer(nchannels, 20)

    # accumulate 2x30 ones
    ring_buffer.accumulate(x)
    # advance write index (-> 2x5 available)
    ring_buffer.advance_write_index(5)

    out_buf = np.zeros(20).reshape(nchannels, -1)

    # read on out_buf (2x10)
    ring_buffer.read(out_buf)
    out_buf_exp = np.array([[1., 1., 1., 1., 1., 0., 0., 0., 0., 0.],
                            [1., 1., 1., 1., 1., 0., 0., 0., 0., 0.]])
    assert(np.allclose(out_buf, out_buf_exp))

    ring_buffer.advance_read_index(5)
    # accumulate 2x30 ones
    ring_buffer.accumulate(x)
    # advance write index (-> 2x5 available)
    ring_buffer.advance_write_index(5)

    # read on out_buf (2x10)
    ring_buffer.read(out_buf)
    out_buf_exp = np.array([[2., 2., 2., 2., 2., 0., 0., 0., 0., 0.],
                            [2., 2., 2., 2., 2., 0., 0., 0., 0., 0.]])
    assert(np.allclose(out_buf, out_buf_exp))
