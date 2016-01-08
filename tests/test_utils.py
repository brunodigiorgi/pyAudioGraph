import pytest
import numpy as np


def test_RingBuffer_as_framer():
	from pyAudioGraph import RingBuffer

	nChannels = 2
	x = np.arange(60).reshape(nChannels,-1)
	myRingBuf = RingBuffer(nChannels,60)
	myRingBuf.write(x[:,:10])
	myRingBuf.write(x[:,10:])

	a = np.zeros(20).reshape(nChannels,-1)

	myRingBuf.read(a)
	a_expected = np.array([[  0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.],
 						   [ 30., 31., 32., 33., 34., 35., 36., 37., 38., 39.]])
	assert(np.allclose(a, a_expected))

	myRingBuf.advanceReadIndex(10)
	myRingBuf.read(a)
	a_expected = np.array([[ 10., 11., 12., 13., 14., 15., 16., 17., 18., 19.],
 			  			   [ 40., 41., 42., 43., 44., 45., 46., 47., 48., 49.]])
	assert(np.allclose(a, a_expected))

	myRingBuf.advanceReadIndex(2)
	myRingBuf.read(a)
	a_expected = np.array([[ 12., 13., 14., 15., 16., 17., 18., 19., 20., 21.],
						   [ 42., 43., 44., 45., 46., 47., 48., 49., 50., 51.]])
	assert(np.allclose(a, a_expected))

