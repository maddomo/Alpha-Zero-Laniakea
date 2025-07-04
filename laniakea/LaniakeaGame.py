from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .LaniakeaLogic import Board
from .actions import ACTION_SIZE, decode_action, encode_action
from .LaniakeaBoardConverter import board_to_tensor, tensor_to_board

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
        return board_to_tensor(Board(), 1)

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
        return (8, 6, 16)

    def getActionSize(self):
        # return number of actions
        # 8*6 Board, 4 Directions, 8 possible moves from home area, 12 possible inserts, 2 rotations
        return ACTION_SIZE

    def getNextState(self, board, player, action):
        b = tensor_to_board(board)
        move1, move2, insert_row, rotate_tile = decode_action(action)
        moves = [move1]
        if move2 is not None:
            moves.append(move2)
        actions = (moves, insert_row, rotate_tile)
        b.execute_move(actions, player)
        print(b.board[2][6]) #print score
        print(f"Player {player} executed action: {actions}")
        return (board_to_tensor(b, -player), -player)

    def getValidMoves(self, board, player):
        b = tensor_to_board(board)
        valid_actions = [0 for _ in range(self.getActionSize())]

        first_moves, rotatable = b.get_legal_moves(player)
        for first_move in first_moves:
            from1, to1, second_moves = first_move

            for second_move in second_moves:
                from2, to2 = second_move[0], second_move[1]
                for insert_row in b.plate_positions(to2[1]):
                    for rotate_tile in ([0, 1] if rotatable else [0]):
                        idx = encode_action((from1, to1), (from2, to2), insert_row, rotate_tile)
                        valid_actions[idx] = 1

        return valid_actions

        
    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = tensor_to_board(board)

        if b.is_win(player):
            return 1
        if b.is_win(-player):
            return -1
        if b.has_legal_moves(player):
            return 0


    def getCanonicalForm(self, board, player):
        if player == 1:
            return board.copy()
        else:
            board = board.copy()  # Don't modify the original

            # Swap white (2:5) and black (5:8) piece channels
            white_pieces = board[:, :, 2:5].copy()
            black_pieces = board[:, :, 5:8].copy()
            board[:, :, 2:5] = black_pieces
            board[:, :, 5:8] = white_pieces

            # Set player channel to 1 (always from white's perspective)
            board[:, :, 8] = 1.0

            # Swap home pieces (channels 9 and 10)
            white_home = board[:, :, 9].copy()
            black_home = board[:, :, 10].copy()
            board[:, :, 9] = black_home
            board[:, :, 10] = white_home

            # Swap scored pieces (channels 11 and 12)
            white_score = board[:, :, 11].copy()
            black_score = board[:, :, 12].copy()
            board[:, :, 11] = black_score
            board[:, :, 12] = white_score

            return board
            
    def getSymmetries(self, board, pi):
        return [(board, pi)]  # No symmetries in this game

    def stringRepresentation(self, board):
        return board.tobytes()