import numpy as np


def test_control_fir_filter():
    import pyAudioGraph as ag

    w = ag.World()

    csg = ag.Nodes.ControlSeqGen(w, [1, 0, 0, 1, 0, 0, 1, 0])
    fir = ag.Nodes.ControlFIRFilter(w, [1, .5, .2])
    rec = ag.Nodes.ControlRateRecorder(w, 1)
    csg.w_out.plug_into(fir.w_in)
    fir.w_out.plug_into(rec.w_in[0])

    w.append(rec)
    w.sort()

    for i in range(8):
        w._topGroup.calc_func()
    a = rec.data[0][:8]

    a_expected = np.array([[1., 0.5, 0.2, 1., 0.5, 0.2, 1., 0.5]])
    assert(np.allclose(a, a_expected))
