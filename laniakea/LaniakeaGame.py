from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .LaniakeaLogic import Board
from .LaniakeaHelper import ACTION_SIZE, decode_action, encode_action, decode_stack, mirror_action
from .LaniakeaBoardConverter import board_to_tensor, tensor_to_board
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
        return board_to_tensor(Board(False), 1)

    def getBoardSize(self):
        # Tensor dimension
        # 1 Dim for turtles
        # 1 Dim for empty spaces
        # 6 Dims for piece stacks (2 colors * 3 height)
        # 1 Dim Player turn
        # 2 Dim for amount of home pieces black/white
        # 2 Dim for "scored" pieces 
        # 3 Dims for free tile
        # ideas to try if AI performs poorly:
        # (5 * total dims for board history)
        # (1 Dim for movable pieces)
        return (8, 6, 17)

    def getActionSize(self):
        # return number of actions
        # 8*6 Board, 4 Directions, 8 possible moves from home area, 12 possible inserts, 2 rotations
        return ACTION_SIZE 

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        b = tensor_to_board(board)
        if action == -1:
            random_move = random.choice(b.get_legal_moves(player))
            from_pos1, to_pos1, from_pos2, to_pos2, insert_rows = random_move
            if(len(insert_rows) > 0):
                insert_row = random.choice(insert_rows)
            else:
                insert_row = 12
            decoded_action = (from_pos1, to_pos1), (from_pos2, to_pos2), insert_row
        else:
            decoded_action = decode_action(action)
        # mirror move if player is -1, due to canonical form bullshit
        if (player == -1):
            #print(f"Spiegel")
            decoded_action = mirror_action(decoded_action)
        b.execute_move(decoded_action, player)
        return (board_to_tensor(b, -player), -player)

    def getValidMoves(self, board, player):
        b = tensor_to_board(board)
        valid_moves = b.get_legal_moves(player)
        valid_actions = np.zeros(self.getActionSize(), dtype=np.int8)

        for first_move in valid_moves:
            for second_move in first_move[2]:
                if len(second_move[2]) == 0:
                    i = encode_action((first_move[0], first_move[1]), (second_move[0], second_move[1]), 12)
                    valid_actions[i] = 1
                for insert_row in second_move[2]: 
                    i = encode_action((first_move[0], first_move[1]), (second_move[0], second_move[1]), insert_row)
                    valid_actions[i] = 1

        return valid_actions
        
    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = tensor_to_board(board)

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

            # Swap white (2:5) and black (5:8) piece channels
            white_pieces = board_copy[:, :, 2:5].copy()
            black_pieces = board_copy[:, :, 5:8].copy()
            board_copy[:, :, 2:5] = black_pieces
            board_copy[:, :, 5:8] = white_pieces

            board_copy[:, :, 0:8] = np.flip(board_copy[:, :, 0:8], axis=(0, 1))



            # Set player channel to 1 (always from white's perspective)
            board_copy[:, :, 8] = 1.0

            # Swap home pieces (channels 9 and 10)
            white_home = board_copy[:, :, 9].copy()
            black_home = board_copy[:, :, 10].copy()
            board_copy[:, :, 9] = black_home
            board_copy[:, :, 10] = white_home

            # Swap scored pieces (channels 11 and 12)
            white_score = board_copy[:, :, 11].copy()
            black_score = board_copy[:, :, 12].copy()
            board_copy[:, :, 11] = black_score
            board_copy[:, :, 12] = white_score
            #print(f"Board after flip \n{self.boardToString(board_copy)}")
            return board_copy
            
    def getSymmetries(self, board, pi):
        return [(board, pi)]  # No symmetries in this game

    def stringRepresentation(self, board):
        return board.tobytes()
    
    @staticmethod
    def display( board):
        board = tensor_to_board(board).board
        board_str = ""
        board_str += f"Home W: {board[0, 6]}, Home B: {board[1, 6]}, Scored W: {board[2, 6]}, Scored B: {board[3, 6]}\n"
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
        