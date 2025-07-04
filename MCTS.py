import logging
import math
from laniakea.actions import ID_TO_MOVE, MAX_MOVES, encode_action  # falls noch nicht importiert
import numpy as np

EPS = 1e-8

log = logging.getLogger(__name__)


class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard)

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.game.getActionSize())]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    def search(self, canonicalBoard, visited_states=None):
        s = self.game.stringRepresentation(canonicalBoard)

        if visited_states is None:
            visited_states = set()

        # Zykluscheck: Wenn Zustand schon besucht, abbrechen
        if s in visited_states:
            # Zyklus erkannt, neutraler Rückgabewert (z.B. 0)
            return 0

        visited_states.add(s)

        if s not in self.Es:
            self.Es[s] = self.game.getGameEnded(canonicalBoard, 1)
        if self.Es[s] != 0:
            visited_states.remove(s)
            return -self.Es[s]

        if s not in self.Ps:
            (pi1, pi2, pir, prt), v = self.nnet.predict(canonicalBoard)

            valids = self.game.getValidMoves(canonicalBoard, 1)
            flat_policy = np.zeros_like(valids, dtype=np.float32)

            for i1 in range(len(pi1)):
                for i2 in range(len(pi2)):
                    for ir in range(len(pir)):
                        for rt in range(len(prt)):
                            action_id = encode_action(
                                ID_TO_MOVE[i1],
                                ID_TO_MOVE[i2],
                                ir,
                                rt
                            )
                            if valids[action_id] == 1:
                                flat_policy[action_id] = (
                                    pi1[i1] * pi2[i2] * pir[ir] * prt[rt]
                                )

            if np.sum(flat_policy) > 0:
                flat_policy /= np.sum(flat_policy)
            else:
                log.error("All valid moves were masked, doing a workaround.")
                flat_policy = flat_policy + valids
                flat_policy /= np.sum(flat_policy)

            self.Ps[s] = flat_policy
            self.Vs[s] = valids
            self.Ns[s] = 0
            visited_states.remove(s)
            return -v

        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                            1 + self.Nsa[(s, a)])
                else:
                    u = self.args.cpuct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)
        next_s = self.game.getCanonicalForm(next_s, next_player)

        v = self.search(next_s, visited_states)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1
        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1
        visited_states.remove(s)
        return -v

