import torch

from laniakeaOnemove.LaniakeaBoardConverter import board_to_tensor
from laniakeaOnemove.LaniakeaHelper import decode_action, mirror_action
from laniakeaOnemove.pytorch.LaniakeaNNet import LaniakeaNNet
from laniakeaOnemove.pytorch.NNet import NNetWrapper as NNet
import numpy as np
class AIPlayer:
    def __init__(self, game, player):
        self.game = game
        self.nnet = NNet(game)
        self.nnet.load_checkpoint(folder="assets", filename="best_onemove.pth.tar")
        self.player = player

    def get_action(self, board):
        tensor_board = board_to_tensor(board, self.player)
        can_board = self.game.getCanonicalForm(tensor_board, self.player)
        pi, v = self.nnet.predict(can_board)
        valids = self.game.getValidMoves(can_board, 1)
        pi = pi * valids
        sum_pi = np.sum(pi)
        if sum_pi > 0:
            pi /= sum_pi

        move = np.argmax(pi)

        print("test")



        self.last_action = move
        return mirror_action(decode_action(self.last_action))

    def get_last_action(self):
        return decode_action(self.last_action)