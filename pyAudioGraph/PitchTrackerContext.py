import numpy as np
from .MovingViterbi import MovingViterbi
from .PitchTrackerYin import PitchTrackerDetContext, PitchTrackerProbContext


class PT_Frame:
    """Simply encapsulate f0 and prob of a probabilistic Pitch Tracker output frame"""
    def __init__(self, f0, prob):
        assert(len(f0) == len(prob))
        self.obs = prob
        self.f0 = f0

    def __len__(self):
        return len(self.f0)


class F0_trans_fun:
    def __init__(self, max_interval_semitones=7, voiced_transition=-10):
        self.max_int = max_interval_semitones
        self.voiced_transition = voiced_transition

    def trans(self, f_candidates, f_target):
        n = len(f_candidates)
        ic = np.arange(n, dtype=int)
        ts = np.zeros(n)
        min_ts = - np.power(np.log2(2 ** (self.max_int / 12)), 2)

        for ii in range(n):
            if(f_candidates[ii] <= 0 and f_target <= 0):
                ts[ii] = 0
            elif(f_candidates[ii] <= 0 or f_target <= 0):
                ts[ii] = self.voiced_transition
            else:
                ts[ii] = - np.power(np.log2(f_target / f_candidates[ii]), 2)
                ts[ii] = np.maximum(ts[ii], min_ts)
        return ic, ts

    def __call__(self, frame1, frame2, i):
        """
        Compute the transition penalty (<0) in going from frame1.f0[:] to frame2.f0[i].

        Parameters
        ----------
        frame1 : PT_Frame
            source frame contains f0 of source points
        frame2 : PT_Frame
            target frame. frame2.f0[i] is the frequency of the target point
        i : int
            index of the target point in frame2
        """
        f_target = frame2.f0[i]
        f_candidates = frame1.f0
        return self.trans(f_candidates, f_target)


class PitchTrackerProbContextMovingViterbi(PitchTrackerProbContext):
    """Perform smoothing optimizing a path over the last frames, using dynamic programming."""

    def __init__(self, size=4,
                 vit_vtp=-1, vit_mis=7, vit_stab=1.2,
                 pri_vtp=-.003, pri_mis=1, pri_stab=120):
        """
        Constructor for PitchTrackerProbContextMovingViterbi.

        vit_* are the parameters of the moving viterbi path finder.
        pri_* are the parameters of the transition function applied a posteriori,
        in order to exploit the knowledge of the previous f0.

        Parameters
        ----------
        size : int
            number of frames over which to optimize a path
        vit_vtp : float < 0
            viterbi voiced transition penalty
        vit_mis : float > 0
            viterbi maximum interval semitones
        vit_stab : float > 0
            viterbi stability parameter, relative weight of transition with respect to observations
        pri_vtp : float < 0
            prior voiced transition penalty
        pri_mis : float > 0
            prior maximum interval semitones
        pri_stab : float > 0
            prior stability parameter, relative weight of transition with respect to observations
        """
        super().__init__()

        self.size = size
        self.vit_vtp = vit_vtp
        self.vit_mis = vit_mis
        self.vit_stab = vit_stab
        self.pri_vtp = pri_vtp
        self.pri_mis = pri_mis
        self.pri_stab = pri_stab

        self.f0_trans_fun = F0_trans_fun(max_interval_semitones=self.vit_mis,
                                         voiced_transition=vit_vtp)
        self.m = MovingViterbi(self.size, self.f0_trans_fun, self.vit_stab)
        self.f0_trans_funMM = F0_trans_fun(max_interval_semitones=self.pri_mis,
                                           voiced_transition=self.pri_vtp)
        self.clear()

    def clear(self):
        self.startup = True
        self.last_voiced_f0 = 0
        self.non_voiced_count = 0

    # TODO: I want to be able to add many contexts with different time-span and differently weighted F0 transition functions
    # the longer the context the lesser/smoother the effect (transition penalty)
    def push(self, f0, p):
        frame = PT_Frame(f0, p)
        backlinks, scores = self.m.push(frame)
        
        if(not self.startup):  # update scores
            nvc = self.non_voiced_count
            if(nvc > 0 and nvc < 5):
                ic, ts = self.f0_trans_funMM.trans(frame.f0, self.last_voiced_f0)
            else:
                ic, ts = self.f0_trans_funMM.trans(frame.f0, self.prev_f)
            scores += self.pri_stab * ts
        else:
            self.startup = False

        self.i_term = np.argmax(scores)
        self.prev_f = out_f0 = frame.f0[self.i_term]

        voiced = out_f0 > 0

        if(not voiced):
            self.non_voiced_count += 1
            return self.last_voiced_f0, voiced
        else:
            self.non_voiced_count = 0
            self.last_voiced_f0 = out_f0
            return out_f0, voiced

    def latency(self):
        return int(0)


class PitchTrackerDetContextAdaptive(PitchTrackerDetContext):
    """Aperiodicity threshold relaxes with time if steady pitch."""

    def __init__(self, ap_thresh_min=0.05, ap_thresh_max=1.0, ap_thresh_speed=.5, f0_range_st=1):
        super().__init__()

        self.ap_thresh_min = ap_thresh_min
        self.ap_thresh_max = ap_thresh_max
        self.ap_thresh_speed = ap_thresh_speed
        self.f0_range_st = f0_range_st
        self.clear()

    def push(self, f0, ap):
        if((not self.startup) and self.voiced_temp and
                np.abs(np.log2(f0 / self.f0_temp)) < self.f0_range_st / 12.0):
            self.ap_thresh += (self.ap_thresh_max - self.ap_thresh) * self.ap_thresh_speed
        elif(self.startup):
            self.startup = False
        else:
            self.ap_thresh = self.ap_thresh_min

        self.voiced_temp = ap < self.ap_thresh

        self.f0_temp = f0
        return self.f0_temp, self.voiced_temp

    def clear(self):
        self.ap_thresh = self.ap_thresh_min
        self.startup = True
        self.f0_temp = 1
        self.voiced_temp = False

    def latency(self):
        return int(0)

