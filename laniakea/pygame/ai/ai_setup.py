import torch

from laniakea.LaniakeaBoardConverter import board_to_tensor
from laniakea.LaniakeaHelper import decode_action
from laniakeaOnemove.pytorch.LaniakeaNNet import LaniakeaNNet
from laniakeaOnemove.pytorch.NNet import NNetWrapper as NNet

class AIPlayer:
    def __init__(self, game, player):
        self.game = game
        self.nnet = NNet(game)
        self.nnet.load_checkpoint(folder="assets", filename="best_onemove.pth.tar")
        self.player = player

    def get_action(self, board):
        tensor_board = board_to_tensor(board, self.player)
        can_board = self.game.getCanonicalForm(tensor_board, self.player)
        action = self.nnet.predict(can_board)
        self.last_action = action.argmax()
        return decode_action(self.last_action)

    def get_last_action(self):
        return decode_action(self.last_action)