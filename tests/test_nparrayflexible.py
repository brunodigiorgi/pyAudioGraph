import numpy as np


def test_nparrayflexible():
    from pyAudioGraph import NumpyArrayFlexible

    n = NumpyArrayFlexible.NPArrayFlexible(n_rows=2, capacity=4)
    n.new_row()
    n.append(1)
    n.append(2)
    n.new_row()
    n.append(3)
    n.append(4)
    assert(n[1,1] == 4)
    n.new_row()
    n.append(5)
    n.append(6)
    assert(np.all(n[2] == np.array([5, 6])))
    n.append_row(np.array([7, 8]))
    assert(np.all(n[3] == np.array([7, 8])))
    assert(np.all(n[-1] == np.array([7, 8])))
    assert(n.n_rows() == 4)