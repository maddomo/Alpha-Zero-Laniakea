from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .LaniakeaLogic import Board
from .LaniakeaHelper import ACTION_SIZE, decode_action, encode_action, decode_stack, mirror_action
import numpy as np
import random

"""
Game class implementation for the game of TicTacToe.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""
class LaniakeaGame(Game):

    def getInitBoard(self):
        # return initial board (numpy board)
        return Board().board

    def getBoardSize(self):
        # Tensor dimension
        # 1 Dim for turtles
        # 1 Dim for empty spaces
        # 3 Dims for piece stacks (1/-1 * 3 height)
        # 2 Dim for amount of home pieces black/white
        # 2 Dim for "scored" pieces 
        # 4 Dims for free tile
        return (8, 6, 13)

    def getActionSize(self):
        # return number of actions
        return ACTION_SIZE 

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        b = Board(False)
        b.board = board
        # Pick a random action if action is not found
        if action == -1:
            action = random.choice(self.getValidMoves(board, player))
        decoded_action = decode_action(action)
        # mirror move if player is -1, due to canonical form
        if (player == -1):
            #print(f"Spiegel")
            decoded_action = mirror_action(decoded_action)
        b.execute_move(decoded_action, player)
        return (b.board, -player)

    def getValidMoves(self, board, player):
        b = Board(False)
        b.board = board
        valid_moves = b.get_legal_moves(player)
        valid_actions = np.zeros(self.getActionSize(), dtype=np.int8)

        for first_move in valid_moves:
            for second_move in first_move[2]:
                for insert_row in second_move[2]: 
                    i = encode_action((first_move[0], first_move[1]), (second_move[0], second_move[1]), insert_row)
                    valid_actions[i] = 1

        return valid_actions
        
    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(False)
        b.board = board

        if b.is_win(player):
            #print(f"Player {player} wins!")
           # print(b.board)
           # print(f"\n Player 1 legal moves{b.has_legal_moves(player)}\nPlayer -1 legal moves{b.has_legal_moves(-player)}\n")
            return 1
        if b.is_win(-player):
            #print(f"Player {-player} wins!")
            #print(b.board)
            #print(f"\n Player 1 legal moves{b.has_legal_moves(player)}\nPlayer -1 legal moves{b.has_legal_moves(-player)}\n")
            return -1
        if b.has_legal_moves(player):
            return 0


    def getCanonicalForm(self, board, player):
        if player == 1:
            return board.copy()
        else:
            #print(f"Board before flip \n{self.boardToString(board)}")
            board_copy = board.copy()  # Don't modify the original

            # Negate piece channels
            board_copy[:, :, 2:5] *= -1

            board_copy[:, :, 0:5] = np.flip(board_copy[:, :, 0:5], axis=(0, 1))

            # Swap home pieces (channels 5 and 6)
            white_home = board_copy[:, :, 5].copy()
            black_home = board_copy[:, :, 6].copy()
            board_copy[:, :, 5] = black_home
            board_copy[:, :, 6] = white_home

            # Swap scored pieces (channels 7 and 8)
            white_score = board_copy[:, :, 7].copy()
            black_score = board_copy[:, :, 8].copy()
            board_copy[:, :, 7] = black_score
            board_copy[:, :, 8] = white_score
            #print(f"Board after flip \n{self.boardToString(board_copy)}")
            return board_copy
            
    def getSymmetries(self, board, pi):
        return [(board, pi)]  # No symmetries in this game

    def stringRepresentation(self, board):
        return board.tobytes()
    
    def boardToString(self, board):
        board_str = ""
        board_str += f"Home W: {board[0][0][5]*8}, Home B: {board[0][0][6]*8}, Scored W: {board[0][0][7]*5}, Scored B: {board[0][0][8]*5}\n"
        for y in range(5, -1, -1):
            for x in range(8):
                field = board[x, y]
                if field == 0:
                    board_str += " 0 "
                elif field == -1:
                    board_str += " X "
                else:
                    stack = decode_stack(board[x, y])
                    for piece in stack:
                        if piece == 1:
                            board_str += "W"
                        else:
                            board_str += "B"
                    board_str += "E" * (3 - len(stack))  # Fill with zeros
                board_str += " "
            board_str += "\n\n\n"
        return board_str
        