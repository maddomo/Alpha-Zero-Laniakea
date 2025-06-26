'''
Board class for the game of TicTacToe.
Default board size is 3x3.
Board data:
  1=white(O), -1=black(X), 0=empty
  first dim is column , 2nd is row:
     pieces[0][0] is the top left square,
     pieces[2][0] is the bottom left square,
Squares are stored and manipulated as (x,y) tuples.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the board for the game of Othello by Eric P. Nichols.

'''
import random
import numpy as np

# from bkcharts.attributes import color

# Board fields explained:
#   0000 0000 0000 0000 0000 0000 0000 0000 -> empty
#   1000 0000 0000 0000 0000 0000 0000 0001 -> turtle
#   ... 0000 0000 0011                      -> one black piece
#   ... 0000 0001 0001                      -> two white pieces stacked 
#   ... 0011 0001 0011                      -> black, white, black stack
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self):
        "Set up initial board configuration."
        self.plates = [5, 12, 5]    # two, one, none
        rows = 6
        cols = 8
        board = [[None for _ in range(cols)] for _ in range(rows + 1)]
        for i in range(rows):
            position = random.randint(0, 3) * 2

            board[i][position] = 0
            board[i][position + 1] = 0
        for i in range(rows):
            for j in range(4):
                if (board[i][j * 2] != None): continue
                random_plate = self.get_random_plate()
                board[i][j * 2] = random_plate[0]
                board[i][j * 2 + 1] = random_plate[1]
        
        board[rows][0] = 8 #White pieces in white's space
        board[rows][1] = 8 #Black pieces in black's space

        board[rows][2] = 0 #White pieces in black's space
        board[rows][3] = 0 #Black pieces in white's space
        self.board = np.array(board)

            
    def get_random_plate(self):
        randomIndex = random.randint(0,2)

        while(self.plates[randomIndex] == 0):
            randomIndex = random.randint(0,2)
        self.plates[randomIndex] = self.plates[randomIndex] - 1

        if randomIndex == 0:
            return [-1, -1]
        elif randomIndex == 1:
            return random.choice([[-1, 0], [0, -1]])
        elif randomIndex == 2:
            return [0, 0]


    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.board[index]

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        @param color not used and came from previous version.        
        """
        moves = set()  # stores the legal moves.

        piecesAtHome = self[6][0 if color == 1 else 1]
        
        
        


        # Get all the empty squares (color==0)
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    newmove = (x,y)
                    moves.add(newmove)
        return list(moves)
    
    

    def has_legal_moves(self):
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    return True
        return False
    
    def is_win(self, color):
        """Check whether the given player has won; Player has won by either bringing all his pieces
        into the endzone of the opponent or if the opponent doesn't have any moves left
        @param color (1=white,-1=black)
        """
        is_in_endzone = self[6][2 + (0 if color == 1 else 1)] == 8

        opp_has_moves_left = len(self.get_legal_moves(1 if color == -1 else 1)) != 0

        return is_in_endzone or (not opp_has_moves_left)

    def execute_move(self, move, color):
        """Perform the given move on the board; 
        color gives the color pf the piece to play (1=white,-1=black)
        """

        (x,y) = move

        # Add the piece to the empty square.
        assert self[x][y] != -1 and not self.isfullstack(x, y)
        self[x][y] = color

    def is_fullstack(self, x, y):
        return (self.board[x][y] & 1 << 8) != 0
    
    def get_stack_height(self, x, y):
        if (self.is_fullstack(x, y)):
            return 3
        elif ((self.board[x][y] & 1 << 4) != 0):
            return 2
        elif ((self.board[x][y] & 1) != 0):
            return 1
        else: 
            return 0
        
test = Board()