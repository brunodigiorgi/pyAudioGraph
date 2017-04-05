import numpy as np
from .RingList import RingList
from .NumpyArrayFlexible import NPArrayFlexible


class MovingViterbi:
    """Perform causal smoothing by extracting optimal path within the last [size] frames."""

    def __init__(self, size, trans_fun, stability, n_elem=2048):
        self.size = size
        self.trans_fun = trans_fun
        self.l = RingList(self.size)
        self.cumscores = np.zeros(n_elem)
        self.cumscores_prev = np.zeros(n_elem)
        self.backlinks = NPArrayFlexible(size, n_elem, dtype=np.int)
        self.stability = stability

    def clear(self):
        self.l.clear()

    def push(self, frame, verbose=False):
        """
        Push a new frame of candidate pts.

        Parameters
        ----------
        frame : object with .obs property
            a frame has (at least) a .obs attribute which is a list of floats
        """
        self.l.push(frame)
        backlinks, score = self.viterbi(verbose)
        return backlinks, score

    def viterbi(self, verbose=False):

        b = self.backlinks
        b.clear()

        cs = self.cumscores
        cs_prev = self.cumscores_prev

        if(verbose):
            print("====NEWFRAME=====")

        f = self.l.front()
        for i in range(len(f)):
            cs_prev[i] = cs[i] = f.obs[i]

        for i in range(self.size - 1):
            if(self.l[i] is None):
                continue

            if(verbose):
                print("  ====NEWROW=====")
                print('  prev_pts', self.l[i].f0[:])
                print('  prev_scores', cs_prev[len(self.l[i])])

            b.new_row()

            n = len(self.l[i + 1])  # length of the next frame
            for ii in range(n):
                ic, ts = self.trans_fun(self.l[i], self.l[i + 1], ii)

                scores = self.stability * ts + cs_prev[ic]
                xx = np.argmax(scores)

                if(verbose):
                    print('  ==target_point', ii, self.l[i + 1].f0[ii])
                    print('    transitions', self.stability * ts)
                    print('    winner', ic[xx], self.l[i].f0[ic[xx]])

                b.append(ic[xx])
                cs[ii] = scores[xx] + self.l[i + 1].obs[ii]

            # store cs_prev = cs
            for ii in range(n):
                cs_prev[ii] = cs[ii]

        n_last = len(self.l[-1])
        scores = cs[:n_last]
        return b, scores

    def backtrack(self, backlinks, scores, verbose=False):

        n_frames = len(backlinks)
        if(n_frames == 0):
            return [np.argmax(scores)]

        i_term = np.argmax(scores)
        path = [i_term]

        for i in reversed(range(n_frames)):
            path.append(backlinks[i, path[-1]])
        path = path[::-1]

        if(verbose):
            print('cs_last_frame', scores)
            print('path', path)

        return path
