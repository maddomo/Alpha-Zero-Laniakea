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
from .LaniakeaHelper import encode_plate, decode_plate, encode_stack, decode_stack
# from bkcharts.attributes import color

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
    # list of all 4 directions on the board, as (x,y) offsets
    __directions = [(1,0),(0,1),(-1,0),(0,-1)]
    rows = 5
    cols = 6
    def __init__(self, randomize=True):
        """
        Initializes the board. If randomize is False, it initializes
        to an empty or default state without random placements.
        """ 
         # (6 plates removed from none, as they are added in each row before adding the rest)
        self.plates = [5, 12, 5]    # two turtles, one turtle, no turtle
        if not randomize:
            self.board = np.array([
                [ 0, -1, 0, 0, 0, 8],
                [ 0, 0, 0, -1, -1, 8],
                [ -1, -1, 0, 0, 0, 0],
                [ -1, 0, 0, -1, 0, 0],
                [ -1, 0, -1, 0, 0, 3],
                [ -1, 0, 0, -1, -1, None]
               
            ], dtype=object)  # dtype=object, um auch None zu erlauben
            self.lastMove = (None, None)
            return
        
        # Randomized setup
    
        board = [[None for _ in range(Board.rows + 1)] for _ in range(Board.cols)]
        for i in range(Board.rows):
            position = random.randint(0, (Board.cols -2) // 2) * 2
            board[position][i] = 0
            board[position + 1][i] = 0
        for i in range(Board.rows):
            for j in range(3):
                if (board[j * 2][i] != None): continue
                random_plate = self.get_random_plate()
                board[j*2][i] = random_plate[0]
                board[j*2 + 1][i] = random_plate[1]
        
        board[0][Board.rows] = 8 # White pieces in white's home space
        board[1][Board.rows] = 8 # Black pieces in black's home space

        board[2][Board.rows] = 0 # White pieces in scoring space
        board[3][Board.rows] = 0 # Black pieces in scoring space
        insert_plate = self.get_random_plate()
        board[4][Board.rows] = encode_plate(insert_plate)  # Insertable tile type
        self.board = np.array(board)
        self.lastMove = (None, None)
            
    def get_random_plate(self):        
        available_indices = [i for i, count in enumerate(self.plates) if count > 0]
        if not available_indices:
            raise ValueError("No plates available")

        randomIndex = random.choice(available_indices)
        self.plates[randomIndex] -= 1

        if randomIndex == 0:
            return [-1, -1]
        elif randomIndex == 1:
            return random.choice([[-1, 0], [0, -1]])
        elif randomIndex == 2:
            return [0, 0]
        else:
            raise ValueError("Invalid plate random Index: {}".format(randomIndex))


    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.board[index]

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)       
        """ 
        last_from = self.lastMove[0] if hasattr(self, 'lastMove') and self.lastMove else None
        last_to = self.lastMove[1] if hasattr(self, 'lastMove') and self.lastMove else None     
        moves = Board.step_move(self.board, color, last_from, last_to)
        #print(f"Legal moves for player {color}: {moves} \n")
        return moves
       
    @staticmethod
    def plate_positions(row):
        if row == -1: return []
        # 0-4 = insert from left into row
        # 5-9 = insert from right into row
        if row == -2: return [i for i in range(0, 10)]
        return [row, row + Board.rows]

    @staticmethod
    def step_move(board, color, lastPosition = None, newPosition = None):
        moveList = []
        player_home = 0 if color == 1 else 1
         

        # Zug aus der Heimatreihe
        if board[player_home][Board.rows] > 0:
            for x in range(Board.cols):
                y = 0 if color == 1 else Board.rows - 1
                square = board[x][y]
                if square == -1: continue
                if (lastPosition is not None and newPosition is not None):
                    if (-1, -1) == newPosition and (x, y) == lastPosition:
                        continue

                stack = decode_stack(square)
                if len(stack) == 3: continue

                moveList.append(((-1, -1), (x, y), Board.plate_positions(y)))

        for y in range(Board.rows):
            for x in range(Board.cols):
                if board[x][y] == -1 or board[x][y] == 0:
                    continue

                from_stack = decode_stack(board[x][y])
                height = len(from_stack)
                if from_stack[-1] != color:
                    continue

                for dx, dy in Board.__directions:
                    new_x = x + dx * height
                    new_y = y + dy * height

                    # Grenzen prüfen
                    if new_x < 0 or new_x >= Board.cols or new_y < 0 or new_y >= Board.rows:
                        # Scoring oder Rückkehr nach Hause
                        if (color == 1 and new_y >= Board.rows) or (color == -1 and new_y < 0):
                            moveList.append(((x, y), (-2, -2), Board.plate_positions(-2)))
                        elif (color == -1 and new_y >= Board.rows) or (color == 1 and new_y < 0):
                            moveList.append(((x, y), (-1, -1), Board.plate_positions(-1)))
                        elif (new_x < 0 or new_x >= Board.cols):
                            moveList.append(((x, y), (-1, -1), Board.plate_positions(-1)))
                        continue

                    # Verhindere Rückwärtsbewegung
                    if (lastPosition is not None and newPosition is not None):
                        if (x, y) == newPosition and (new_x, new_y) == lastPosition:
                            continue

                    if board[new_x][new_y] == -1:
                        continue

                    to_stack = decode_stack(board[new_x][new_y])
                    if len(to_stack) == 3:
                        continue

                    moveList.append(((x, y), (new_x, new_y), Board.plate_positions(new_y)))
        return moveList

                    

    def has_legal_moves(self, color):
        """Check whether the current player has any legal moves left.
        Returns True if there are legal moves, False otherwise.
        """
        move_list = self.get_legal_moves(color)
        return any(move_list)

    
    def is_win(self, color):
        """Check whether the given player has won; Player has won by either bringing all his pieces
        into the endzone of the opponent or if the opponent doesn't have any moves left
        @param color (1=white,-1=black)
        """
        is_in_endzone = self.board[2 + (0 if color == 1 else 1)][Board.rows] == 1

        no_moves_left = not self.has_legal_moves(-color)
        return is_in_endzone or (no_moves_left)

    def execute_move(self, action, color):
        """
        Führt einen einzigen Zug + Einschüben aus.
        action: ((from_pos, to_pos), insert_row)
        """
        move, insert_row = action
        from_pos, to_pos = move
        player_home = 0 if color == 1 else 1
        if from_pos == (-1, -1):
            # Aus Heimatreihe auf das Brett
            x, y = to_pos
            stack = decode_stack(self.board[x][y])
            stack.append(color)
            self.board[x][y] = encode_stack(stack)
            self.board[player_home][Board.rows] -= 1

        else:
            x1, y1 = from_pos
            x2, y2 = to_pos

            # Entferne oberstes Element vom Stack am Startfeld
            from_stack = decode_stack(self.board[x1][y1])
        
            
            piece = from_stack.pop()
            self.board[x1][y1] = encode_stack(from_stack)

            if to_pos == (-2, -2):
                # Punkt erzielt
                self.board[2 + player_home][Board.rows] += 1
            elif to_pos == (-1, -1):
                # Zurück in Heimatreihe
                self.board[player_home][Board.rows] += 1
            else:
                # Normales Platzieren
                to_stack = decode_stack(self.board[x2][y2])
                to_stack.append(piece)
                self.board[x2][y2] = encode_stack(to_stack)

        # Einschüben nach dem Zug
        if(insert_row < 10):
            self.insert_plate_into_row(insert_row)
        self.lastMove = (from_pos, to_pos)
        
        


    def insert_plate_into_row(self, row):
        """Insert a plate into the row at the given position.
        row <= 5 indicates the row is inserted from the left side.   -> 0000
        row > 5 indicates the row is inserted from the right side.      0000 <-
        @param row: row to insert the plate into
        """
        assert row >= 0 and row < Board.rows * 2, "Row must be between 0 and 11"
        # insert from left
        if row < Board.rows:
            for i in range(2):
                if self.board[Board.cols - 2 + i][row] == 0 or self.board[Board.cols - 2 + i][row] == -1:
                    continue
                # Return the pieces to the home row when pushing them off the board
             
                stack = decode_stack(self.board[Board.cols - 2+i][row])
                
                for piece in stack:
                    self.board[0 + (0 if piece == 1 else 1)][Board.rows] += 1
                # Set the field to empty, so the tile can be saved properly
                self.board[Board.cols - 2+i][row] = 0

            # Shift the row to the right
            board_copy = np.copy(self.board)
            for i in range(2, Board.cols):
                self.board[i][row] = board_copy[i - 2][row]
            insert_plate = decode_plate(self.board[4][Board.rows])
            self.board[0][row] = insert_plate[0]
            self.board[1][row] = insert_plate[1]
            self.board[4][Board.rows] = encode_plate([board_copy[Board.cols - 2][row], board_copy[Board.cols -1][row]])



        # insert from right
        else:
            row -= Board.rows  # Adjust row for right side insertion
            for i in range(2):
                if self.board[0+i][row] == 0 or self.board[0+i][row] == -1:
                    continue
                # Return the pieces to the home row when pushing them off the board
               
                stack = decode_stack(self.board[0+i][row])
                
                for piece in stack:
                    self.board[0 + (0 if piece == 1 else 1)][Board.rows] += 1
                # Set the field to empty, so the tile can be saved properly
                self.board[0+i][row] = 0

            # Shift the row to the left
            board_copy = np.copy(self.board)
            for i in range(0, Board.cols - 2):
                self.board[i][row] = board_copy[i + 2][row]
            insert_plate = decode_plate(self.board[4][Board.rows])
            self.board[Board.cols -2][row] = insert_plate[0]
            self.board[Board.cols -1][row] = insert_plate[1]
            self.board[4][Board.rows] = encode_plate([board_copy[0][row], board_copy[1][row]])

    
            
