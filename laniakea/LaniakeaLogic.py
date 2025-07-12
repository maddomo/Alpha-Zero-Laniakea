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

    def __init__(self, randomize=True):
        """
        Initializes the board. If randomize is False, it initializes
        to an empty or default state without random placements.
        """ 
         # (6 plates removed from none, as they are added in each row before adding the rest)
        self.plates = [5, 12, 5]    # two turtles, one turtle, no turtle
        if not randomize:
            self.board = np.array([
                [0, 0, -1, 0, 0, 0, 8],
                [0, 0, 0, 0, -1, -1, 8],
                [0, -1, -1, 0, 0, 0, 0],
                [0, -1, 0, 0, -1, 0, 0],
                [0, -1, 0, -1, 0, 0, 3],
                [0, -1, 0, 0, -1, -1, None],
                [-1, 0, -1, 0, 0, -1, None],
                [-1, -1, -1, 0, 0, -1, None]
            ], dtype=object)  # dtype=object, um auch None zu erlauben
            self.lastMove = (None, None)
            return
        
        # Randomized setup
        rows = 6
        cols = 8
        board = [[None for _ in range(rows + 1)] for _ in range(cols)]
        for i in range(rows):
            position = random.randint(0, 3) * 2
            board[position][i] = 0
            board[position + 1][i] = 0
        for i in range(rows):
            for j in range(4):
                if (board[j * 2][i] != None): continue
                random_plate = self.get_random_plate()
                board[j*2][i] = random_plate[0]
                board[j*2 + 1][i] = random_plate[1]
        
        board[0][rows] = 8 # White pieces in white's home space
        board[1][rows] = 8 # Black pieces in black's home space

        board[2][rows] = 0 # White pieces in scoring space
        board[3][rows] = 0 # Black pieces in scoring space
        insert_plate = self.get_random_plate()
        board[4][rows] = encode_plate(insert_plate)  # Insertable tile type
        self.board = np.array(board)
            
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
        moves = Board.step_move(self.board, color)
        #print(f"Legal moves for player {color}: {moves} \n")
        return moves
       
    @staticmethod
    def plate_positions(row):
        if row == -1: return []
        # 0-5 = insert from left into row
        # 6-11 = insert from right into row
        if row == -2: return [i for i in range(0, 12)]
        return [row, row + 6]

    @staticmethod
    def step_move(board, color, lastPosition=None, newPosition=None):
        # moveList type: List[Tuple,Tuple,List[Tuple()]]
        moveList = []
        player_home = 0 if color == 1 else 1
        # Check if a move from home is possible and if so, move a piece to the board
        # Not checking all directions, as only the first row from each side is relevant
        if board[player_home][6] > 0:
            for x in range(8):
                y = 0 if color == 1 else 5
                square = board[x][y]
                
                if square == -1: continue
                # Skip if move reverses the last move
                # If a piece scores, lastPosition will not be close to home, so reversing is not possible
                if (lastPosition is not None and newPosition is not None):
                    if (-1,-1) == newPosition and (x, y) == lastPosition: 
                        continue

                stack = decode_stack(square)
                if len(stack) == 3: continue

                stack.append(color)
                cloned_board = np.copy(board)
                cloned_board[player_home][6] -= 1
                cloned_board[x][y] = encode_stack(stack)
                if lastPosition is not None and newPosition is not None:
                    moveList.append(((-1, -1), (x, y), Board.plate_positions(y)))
                else:
                    # Check if a second move is possible
                    second_moves = Board.step_move(cloned_board, color, (-1, -1), (x, y))
                    if any(second_moves):
                        moveList.append(((-1, -1), (x, y), second_moves))
            
        for y in range(6):
            for x in range(8):
                if board[x][y] == -1 or board[x][y] == 0: continue
                from_stack = decode_stack(board[x][y])
                height = len(from_stack)
                top_color = from_stack[height - 1]
                if top_color != color: continue
                for tuple in Board.__directions:
                    from_stack_copy = list(from_stack)
                    new_x = x + tuple[0] * height
                    new_y = y + tuple[1] * height


                    if new_x < 0 or new_x >= 8 or new_y < 0 or new_y >= 6:
                        # Signaling, that the last move was move to the home row
                        if (lastPosition is not None and newPosition is not None):
                            if (x, y) == newPosition and (-1, -1) == lastPosition:
                                continue
                    else:
                        if (lastPosition is not None and newPosition is not None):
                            if (x, y) == newPosition and (new_x, new_y) == lastPosition:
                                continue
                        if board[new_x][new_y] == -1: 
                            continue #Cannot bemoved on Turtle
                            
                    # Out of bounds left or right
                    if new_x < 0 or new_x >= 8:
                        new_x = -1
                        new_y = -1
                        from_stack_copy.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = encode_stack(from_stack_copy)
                        cloned_board[player_home][6] += 1
                        if lastPosition is not None and newPosition is not None:
                            moveList.append(((x, y), (new_x, new_y), Board.plate_positions(new_y)))
                        else:
                            moveList.append(((x, y), (new_x, new_y), Board.step_move(cloned_board, color, (x, y), (new_x, new_y))))
                        continue

                    # Scoring move
                    if (color == 1 and new_y >= 6) or (color == -1 and new_y < 0):
                        # Signaling, that the last move was a scoring move
                        new_x = -2
                        new_y = -2
                        from_stack_copy.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = encode_stack(from_stack_copy)
                        cloned_board[2 + player_home][6] += 1
                        #print(f"lastPosition {lastPosition}, newPosition {newPosition} \n")
                        if lastPosition is not None and newPosition is not None:
                            #print("Second move \n")
                            moveList.append(((x, y), (new_x, new_y), Board.plate_positions(new_y)))
                        else:
                            # Check if a second move is possible
                            # if the game would be won after the first move, but no second move is possible, it would not get returned :(
                            # not including this, because we would need to rewrite everything
                            #print("First move \n")
                            second_moves = Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                            if any(second_moves):
                                #print("Adding second moves \n")
                                moveList.append(((x, y), (new_x, new_y), second_moves))
                        continue

                    # Back to home
                    if (color == -1 and new_y >= 6) or (color == 1 and new_y < 0):
                        new_x = -1
                        new_y = -1
                        from_stack_copy.pop()
                        cloned_board = np.copy(board)
                        cloned_board[x][y] = encode_stack(from_stack_copy)
                        cloned_board[0 + player_home][6] += 1
                        if lastPosition is not None and newPosition is not None:
                            moveList.append(((x, y), (new_x, new_y), Board.plate_positions(new_y)))
                        else:
                            # Check if a second move is possible
                            second_moves = Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                            if any(second_moves):
                                moveList.append(((x, y), (new_x, new_y), second_moves))
                        continue

                    to_stack = decode_stack(board[new_x][new_y])

                    if len(to_stack) == 3: continue

                    to_stack.append(color)
                    from_stack_copy.pop()
                    cloned_board = np.copy(board)
                    cloned_board[x][y] = encode_stack(from_stack_copy)
                    cloned_board[new_x][new_y] = encode_stack(to_stack)
                    if lastPosition is not None and newPosition is not None:
                        moveList.append(((x, y), (new_x, new_y), Board.plate_positions(new_y)))
                    else:
                        # Check if a second move is possible
                        second_moves = Board.step_move(cloned_board, color, (x, y), (new_x, new_y))
                        if any(second_moves):
                            moveList.append(((x, y), (new_x, new_y), second_moves))
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
        is_in_endzone = self.board[2 + (0 if color == 1 else 1)][6] == 5

        opp_has_moves_left = self.has_legal_moves(-color)

        return is_in_endzone or (not opp_has_moves_left)

    def execute_move(self, actions, color):
        """Perform the given move on the board; 
        color gives the color pf the piece to play (1=white,-1=black)
        """
        #print(f"Executing move for player {color} with actions: {actions}")
        #print("Board before move:\n", self.board)
        moves, insert_row = actions
        player_home = 0 if color == 1 else 1
        for move in moves:
            from_pos, to_pos = move[0], move[1]
            if from_pos == (-1,-1):
                # Move from Home
            
                x, y = to_pos
                stack = decode_stack(self.board[x][y])
                stack.append(color)
                self.board[x][y] = encode_stack(stack)
                self.board[player_home][6] -= 1
            else:
                x1, y1 = from_pos
                x2, y2 = to_pos
            

                # Remove top piece from stack
                from_stack = decode_stack(self.board[x1][y1])
                piece = from_stack.pop()
                self.board[x1][y1] = encode_stack(from_stack)

                if to_pos == (-2,-2):
                    # Scoring Move
                    #print("SCORED Player", color, "has scored\n")
                    self.board[2 + player_home][6] += 1
                    #print(f"Moved piece from ({x1}, {y1}) to scoring area")
                    #print(self.board[2 + player_home][6], "pieces in scoring area")
                    
                elif to_pos == (-1,-1):
                    # Back Home
                    self.board[player_home][6] += 1
                    
                else:
                    # Normal Move
                    to_stack = decode_stack(self.board[x2][y2])
                    to_stack.append(piece)
                    self.board[x2][y2] = encode_stack(to_stack)
        if (insert_row < 12):
            self.insert_plate_into_row(insert_row)
        #print("Board after move:\n", self.board)


    def insert_plate_into_row(self, row):
        """Insert a plate into the row at the given position.
        row <= 5 indicates the row is inserted from the left side.   -> 0000
        row > 5 indicates the row is inserted from the right side.      0000 <-
        @param row: row to insert the plate into
        """
        assert row >= 0 and row < 12, "Row must be between 0 and 11"
        # insert from left
        if row < 6:
            for i in range(2):
                if self.board[6+i][row] == 0 or self.board[6+i][row] == -1:
                    continue
                # Return the pieces to the home row when pushing them off the board
             
                stack = decode_stack(self.board[6+i][row])
                
                for piece in stack:
                    self.board[0 + (0 if piece == 1 else 1)][6] += 1
                # Set the field to empty, so the tile can be saved properly
                self.board[6+i][row] = 0

            # Shift the row to the right
            board_copy = np.copy(self.board)
            for i in range(2, 8):
                self.board[i][row] = board_copy[i - 2][row]
            insert_plate = decode_plate(self.board[4][6])
            self.board[0][row] = insert_plate[0]
            self.board[1][row] = insert_plate[1]
            self.board[4][6] = encode_plate([board_copy[6][row], board_copy[7][row]])



        # insert from right
        else:
            row -= 6  # Adjust row for right side insertion
            for i in range(2):
                if self.board[0+i][row] == 0 or self.board[0+i][row] == -1:
                    continue
                # Return the pieces to the home row when pushing them off the board
               
                stack = decode_stack(self.board[0+i][row])
                
                for piece in stack:
                    self.board[0 + (0 if piece == 1 else 1)][6] += 1
                # Set the field to empty, so the tile can be saved properly
                self.board[0+i][row] = 0

            # Shift the row to the left
            board_copy = np.copy(self.board)
            for i in range(0, 6):
                self.board[i][row] = board_copy[i + 2][row]
            insert_plate = decode_plate(self.board[4][6])
            self.board[6][row] = insert_plate[0]
            self.board[7][row] = insert_plate[1]
            self.board[4][6] = encode_plate([board_copy[0][row], board_copy[1][row]])
            
