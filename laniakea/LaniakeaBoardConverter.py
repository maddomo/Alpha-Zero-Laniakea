import numpy as np
from .LaniakeaHelper import decode_stack, encode_stack
from .LaniakeaLogic import Board

# Converts a Laniakea board to a tensor representation
# The tensor has the shape (8, 6, 16):
# - 8 columns (x-axis)
# - 6 rows (y-axis)
# - 17 channels:
#   - 1 channel for turtle
#   - 1 channel for empty fields
#   - 3 channels for white pieces (bottom to top)
#   - 3 channels for black pieces (bottom to top)
#   - 1 channel for player turn (1 if white, 0 if black)
#   - 2 channels for home pieces (white and black)
#   - 2 channels for scored pieces (white and black)
#   - 4 channels for the insertable tile type (0, 1, or 2, 3)

def board_to_tensor(board, player):
    tensor = np.zeros((8, 6, 17), dtype=np.float16)
    board = board.board
    rows = 6
    cols = 8

    for x in range(cols):
        for y in range(rows):
            field = board[x][y]

            if field == -1:
                tensor[x][y][0] = 1  # Turtle
            elif field == 0:
                tensor[x][y][1] = 1  # Empty
            else:
                stack = decode_stack(field)
                stack_height = len(stack)
                assert stack_height <= 3 and stack_height > 0, "Invalid stack height"

                for i in range(stack_height):
                    color = stack[i]
                    if color == 1:
                        tensor[x][y][2 + i] = 1  # White piece
                    else:
                        tensor[x][y][5 + i] = 1  # Black piece

    # Player turn: 1 if white, 0 if black
    tensor[:, :, 8] = 1 if player == 1 else 0

    # Home pieces
    tensor[:, :, 9] = board[0][6] / 8.0  # White
    tensor[:, :, 10]  = board[1][6] / 8.0  # Black
    

    # Scored pieces
    tensor[:, :, 11] = board[2][6] / 5.0  # White
    tensor[:, :, 12] = board[3][6] / 5.0  # Black
    

    tile_type = board[4][rows]
    tensor[:, :, 13 + tile_type] = 1.0

    return tensor


def tensor_to_board(tensor):
    board_array = [[None for _ in range(7)] for _ in range(8)]  # 6 rows + 1 meta row

    for x in range(8):
        for y in range(6):
            if tensor[x][y][0] == 1:
                board_array[x][y] = -1  # Turtle
            elif tensor[x][y][1] == 1:
                board_array[x][y] = 0   # Empty
            else:
                # Add pieces to the board, order both colors from bottom to top
                for i in [2, 5, 3, 6, 4, 7]:
                    if tensor[x][y][i] == 1:
                        offset = i - 2
                        color = 1 if offset < 3 else -1
                        stack = decode_stack(board_array[x][y])
                        stack.append(color)
                        board_array[x][y] = encode_stack(stack)

    # Decode home and scored pieces from constant channel slices
    white_home = int(round(tensor[0][0][9] * 8))
    black_home = int(round(tensor[0][0][10] * 8))
    white_score = int(round(tensor[0][0][11] * 5))
    black_score = int(round(tensor[0][0][12] * 5))
    

    board_array[0][6] = white_home
    board_array[1][6] = black_home
    board_array[2][6] = white_score
    board_array[3][6] = black_score

    # Insert plate logic
    insert_plate = -1
    for i in range(13,17):
        if tensor[0][0][i] == 1:
            insert_plate = i-13
            break
    assert insert_plate != -1, "No insert plate found in tensor!"

    new_board = Board(False)
    new_board.board = np.array(board_array)
    new_board.board[4][6] = insert_plate
    return new_board