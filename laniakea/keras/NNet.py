import argparse
import os
import shutil
import time
import random
import numpy as np
import math
import sys
sys.path.append('..')
from utils import *
from NeuralNet import NeuralNet

import argparse
from .LaniakeaNNet import LaniakeaNNet as onnet

"""
NeuralNet wrapper class for the TicTacToeNNet.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on (copy-pasted from) the NNet by SourKream and Surag Nair.
"""

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': True,
    'num_channels': 512,
})

class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = onnet(game, args)
        self.board_x, self.board_y, self.board_c = game.getBoardSize()
        self.action_size = game.getActionSize()

    def train(self, examples):
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_vs = np.asarray(target_vs)
        print(zip(*target_pis))
        # target_pis = [(pi1, pi2, pi_insert, pi_rotate), ...]
        pi1, pi2, pi_insert, pi_rotate = zip(*target_pis)

        pi1 = np.asarray(pi1)
        pi2 = np.asarray(pi2)
        pi_insert = np.asarray(pi_insert)
        pi_rotate = np.asarray(pi_rotate)

        self.nnet.model.fit(
            x=input_boards,
            y=[pi1, pi2, pi_insert, pi_rotate, target_vs],
            batch_size=args.batch_size,
            epochs=args.epochs
        )


    def predict(self, board):
        start = time.time()
        # board shape should be (board_x, board_y, board_c)
        board = board[np.newaxis, :, :, :]  # Add batch dimension with channels
        pi1, pi2, pi_insert, pi_rotate, v = self.nnet.model.predict(board, verbose=False)
        return (pi1[0], pi2[0], pi_insert[0], pi_rotate[0]), v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # change extension
        filename = filename.split(".")[0] + ".h5"

        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # change extension
        filename = filename.split(".")[0] + ".h5"

        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise ValueError("No model in path '{}'".format(filepath))
        self.nnet.model.load_weights(filepath)
