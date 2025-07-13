from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .LaniakeaLogic import Board
from .LaniakeaHelper import ACTION_SIZE, decode_action, encode_action, decode_stack, mirror_action, encode_stack
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
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        return board_to_tensor(Board(False), 1)

    def getBoardSize(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
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
        """
        Returns:
            actionSize: number of all possible actions
        """
        # 8*6 Board, 4 Directions, 8 possible moves from home area, 12 possible inserts, 2 rotations
        return ACTION_SIZE 

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        b = tensor_to_board(board)  

        if action == -1:
            random_move = random.choice(b.get_legal_moves(player))
            from_pos, to_pos, insert_rows = random_move
            if(len(insert_rows) > 0):
                insert_row = random.choice(insert_rows)
            else:
                insert_row = 12 # setze 12 falls nicht da

            decoded_action = ((from_pos, to_pos), insert_row)
            
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        else:
            decoded_action = decode_action(action)

        if (player == -1):
            #print(f"Spiegel")
            decoded_action = mirror_action(decoded_action)
        b.execute_move(decoded_action, player)
        return (board_to_tensor(b, -player), -player)

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        b = tensor_to_board(board)
        valid_moves = b.get_legal_moves(player)
        valid_actions = np.zeros(self.getActionSize(), dtype=np.int8)

        for move in valid_moves:
            from_pos, to_pos, insert_rows = move  # Neu: Nur ein Move + Liste an Insert-Zeilen
            if len(insert_rows) == 0:
                index = encode_action((from_pos, to_pos), 12)
                valid_actions[index] = 1
            for insert_row in insert_rows:
                index = encode_action((from_pos, to_pos), insert_row)
                valid_actions[index] = 1

        return valid_actions

        
    def getGameEnded(self, board, player):
        """
        Returns:
            0 if the game is not over
            1 if the current player (player) has won
        -1 if the current player has lost
        """
        b = tensor_to_board(board)

        if b.is_win(player):
            return 1
        if b.is_win(-player):
            return -1

        

        return 0  # Spiel läuft weiter

        


    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
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
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        return [(board, pi)]  # No symmetries in this game

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
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
    



        