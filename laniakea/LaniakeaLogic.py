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
import LaniakeaHelper as lh
# from bkcharts.attributes import color

# list of all 4 directions on the board, as (x,y) offsets
__directions = [(1,0),(0,1),(-1,0),(0,-1)]

# Board field encoding explained assuming 32 bit integers:
#   0b 0000 0000 0000 0000 0000 0000 0000 0000 -> empty  (0 decimal)
#   0b 1111 1111 1111 1111 1111 1111 1111 1111 -> turtle (-1 decimal)

# last bit of nibble indicates piece, previous bit indicates color, 
# shift by 4 bits for each stacked piece: 

# 00(color)(piece)    black=1, white=0  piece=1, empty=0: 
# 0001 = white piece

#   0b ... 0000 0000 0011                      -> one black piece
#   0b ... 0000 0001 0001                      -> two white pieces stacked 
#   0b ... 0011 0001 0011                      -> (black, white, black) stack
class Board():

    def __init__(self):
        "Set up initial board configuration."
        # (6 removed from none, as they are added in each row before adding the rest)
        self.plates = [5, 12, 5]    # two turtles, one turtle, no turtle    
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
    
    @staticmethod
    def step_move(board, color, lastPosition=None, newPosition=None):
        moveList = []
        # Check if a move from home is possible and if so, move a piece to the board
        # Not checking all directions, as only the first row from each side is relevant
        if board[6][0 if color == 1 else 1] > 0:
            for x in range(8):
                y = 0 if color == 1 else 5
                square = board[x][y]
                
                if square == -1: continue
                # Skip if move reverses the last move
                # If a piece scores, lastPosition will not be close to home, so reversing is not possible
                if (lastPosition is not None and newPosition is not None):
                    if (-1,-1) == newPosition and (x, y) == lastPosition: 
                        continue

                stack = lh.decode_stack(board[square])
                if len(stack) == 3: continue

                stack.append(color)
                board[6][0 if color == 1 else 1] -= 1
                cloned_board = np.copy(board)
                cloned_board[x][y] = lh.encode_stack(stack)
                Board.step_move(cloned_board, color, (-1, -1), (x, y))
                
            
        for y in range(6):
            for x in range(8):
                if board[x][y] == -1 or board[x][y] == 0: continue
                from_stack = lh.decode_stack(board[x][y])
                height = len(from_stack)
                top_color = from_stack[height - 1]
                if top_color != color: continue
                for tuple in __directions:
                    new_x = x + tuple[0] * height
                    new_y = y + tuple[1] * height

                    # Setting new position early for the reversing move check
                    if new_x < 0 or new_x >= 8 or new_y < 0:
                        new_x = -1
                        new_y = -1
                    # Skip if move reverses the last move
                    if (lastPosition is not None and newPosition is not None):
                        if (x, y) == newPosition and (new_x, new_y) == lastPosition: 
                            continue

                    # Out of bounds left or right
                    if new_x < 0 or new_x >= 8:
                        from_stack.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = lh.encode_stack(from_stack)
                        cloned_board[6][0 if color == 1 else 1] += 1
                        Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                        continue
                    
                    # Scoring move
                    if (color == 1 and new_y >= 6) or (color == -1 and new_y < 0):
                        from_stack.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = lh.encode_stack(from_stack)
                        cloned_board[6][2 + (0 if color == 1 else 1)] += 1
                        Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                        continue

                    # Back to home
                    if (color == -1 and new_y >= 6) or (color == 1 and new_y < 0):
                        from_stack.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = lh.encode_stack(from_stack)
                        cloned_board[6][0 + (0 if color == 1 else 1)] += 1
                        Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                        continue

                    to_stack = lh.decode_stack(board[x][y])

                    if len(to_stack) == 3: continue

                    to_stack.append(color)
                    from_stack.pop()
                    cloned_board = np.copy(board)
                    cloned_board[x][y] = lh.encode_stack(from_stack)
                    cloned_board[new_x][new_y] = lh.encode_stack(to_stack)
                    Board.step_move(cloned_board, color, (x, y), (new_x, new_y))

                    



    def has_legal_moves(board, color):
        """Check whether the current player has any legal moves left.
        Returns True if there are legal moves, False otherwise.
        """
        move_list = step_move(board, color)
        if not any(move_list): 
            return False
        return True


    
    def is_win(self, color):
        """Check whether the given player has won; Player has won by either bringing all his pieces
        into the endzone of the opponent or if the opponent doesn't have any moves left
        @param color (1=white,-1=black)
        """
        is_in_endzone = self[6][2 + (0 if color == 1 else 1)] == 5

        opp_has_moves_left = len(self.get_legal_moves(1 if color == -1 else 1)) != 0

        return is_in_endzone or (not opp_has_moves_left)

    def execute_move(self, move, color):
        """Perform the given move on the board; 
        color gives the color pf the piece to play (1=white,-1=black)
        """

        (x,y) = move

        # Add the piece to the empty square.
        assert self.board[x][y] != -1 and not self.isfullstack(x, y)
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
        
    # returns 1 for black and 0 for white
    def get_highest_piece(self, x, y):
        assert self.get_stack_height(x,y) != 0
        if (self.get_stack_height(x,y) == 1):
            return 1 if self.board << 1 == 0 else -1
        return 1 if self.board << (2 ** self.get_stack_height(x,y) + 1) else -1