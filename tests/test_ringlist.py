import numpy as np


def test_ringlist():
	from pyAudioGraph import RingList

	r = RingList.RingList(3)
	r.push(1)
	assert(r.front() == 1)
	assert(r.back() == 1)
	r.push(2)
	print(r)
	assert(r.front() == 1)
	assert(r.back() == 2)
	r.push(3)
	assert(r.front() == 1)
	assert(r.back() == 3)
	r.push(4)
	assert(r.front() == 2)
	assert(r.back() == 4)