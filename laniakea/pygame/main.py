import pygame
from . import drawhelper as dh
import random
from ..LaniakeaLogic import Board
from ..LaniakeaHelper import decode_stack, encode_stack

pygame.init()

rows = 6
cols = 8

# 1 = WHITE, -1 = BLACK
current_player = 1

piece_width = dh.get_laniakea_piece_width()
piece_height = dh.get_laniakea_piece_height()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700 + (piece_height * 2)

BACKGROUND = "#63d14f"
FOREGROUND = "#FFCF85"
FOREGROUND_ACCENT = "#BB854E"
SELECTED_COLOR = "#C2FFFD"

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
dh.init_images()
board = Board(False)
board[3][2] = 1
board[4][2] = 1
board[0][0] = -1


selected_field = None
possible_moves = []

def draw_board():
    global screen, board, selected_field, possible_moves, SCREEN_WIDTH
    dh.draw_board_helper(screen, board, selected_field, possible_moves, SCREEN_WIDTH)

def stack_top_matches_player(stack, current_player):
    decoded = decode_stack(stack)
    return decoded and decoded[-1] == current_player

# return a list of possible moves for a (selected) piece
def get_legal_moves_for_piece(piece):
    """
    Gibt alle Zielpositionen (x, y) zurück, zu denen ein Spielstein
    vom Feld `selected_field` (x, y) aus ziehen kann.
    """
    all_moves, _ = board.get_legal_moves(current_player)
    print("all moves:", all_moves)
    x, y = piece
    result = []

    for move in all_moves:
        from_pos, to_pos, _ = move
        if from_pos == (x, y):
            result.append(to_pos)

    return result
    
def handle_mouse_input(mouse_x, mouse_y):
    global selected_field, current_player, possible_moves

    board_x = SCREEN_WIDTH / 2 - (piece_width * 8) / 2
    board_y = 4  # upper edge

    board_pixel_width = piece_width * 8
    house_height = piece_height * 2
    field_height = piece_height * 6

    # click in black house (upper house)
    if board_x <= mouse_x < board_x + board_pixel_width and board_y <= mouse_y < board_y + house_height:
        col = int((mouse_x - board_x) // piece_width)
        if current_player == -1:
            selected_field = (1, rows)
            draw_board()
        return

    # click in 8x6 board
    if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height <= mouse_y < board_y + house_height + field_height:
        col = int((mouse_x - board_x) // piece_width)
        row = int((mouse_y - (board_y + house_height)) // piece_height)
        row = rows - 1 - row
        print("selected field: ",(col,row))
        if 0 <= col < cols and 0 <= row < rows:
            stack = board[col][row]
            if stack_top_matches_player(stack, current_player):
                selected_field = (col, row)
                possible_moves = get_legal_moves_for_piece(selected_field)
                #print(possible_moves)
                draw_board()
        return

    # click in white house (lower house)
    if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height + field_height <= mouse_y < board_y + house_height + field_height + house_height:
        col = int((mouse_x - board_x) // piece_width)
        if current_player == 1:
            selected_field = (0, rows)
            draw_board()
        return

screen.fill(BACKGROUND)

# Draw a solid blue circle in the center
pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

draw_board()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            handle_mouse_input(mouse_x, mouse_y)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()