import pygame
from . import drawhelper as dh
import random
from ..LaniakeaLogic import Board
from ..LaniakeaHelper import decode_stack

pygame.init()

rows = 6
cols = 8

# 1 = WHITE, -1 = BLACK
current_player = -1

piece_width = dh.get_laniakea_piece_width()
piece_height = dh.get_laniakea_piece_height()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700 + (piece_height * 2)

BACKGROUND = "#6E97CC"
FOREGROUND = "#FFCF85"
FOREGROUND_ACCENT = "#BB854E"
SELECTED_COLOR = "#C2FFFD"

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
dh.init_images()
board = Board()
board[3][2] = 305
board[4][2] = 787


selected_field = None

def draw_board():
    print(selected_field)
    y = 10
    
    board_width = piece_width * 8
    board_height = piece_height * 8

    x = SCREEN_WIDTH / 2 - board_width / 2
    y = SCREEN_HEIGHT / 2 - board_height / 2

    y = 4

    #background
    pygame.draw.rect(screen, FOREGROUND_ACCENT, (x, y, board_width, board_height))

    # Black house
    if isinstance(selected_field, tuple) and selected_field[1] == 'top':
        dh.draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT, 2)
    else:
        dh.draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT, 2)
    # Black pieces in black's home space
    dh.draw_pieces_in_house(screen, x, y + piece_height, board_width, piece_height, board[1][rows], 3)
    # White pieces in scoring space
    dh.draw_pieces_in_house(screen, x, y, board_width, piece_height, board[2][rows], 1)

    y += piece_height * 2

    #laniakea rows
    for offset_y in range(rows):
        for offset_x in range(cols):
            if (selected_field == (offset_x, offset_y)):
                dh.draw_laniakea_piece(screen, board[offset_x][offset_y], (x + offset_x * piece_width, y + offset_y * piece_height), 1)
                print('hallo')
            else:
                dh.draw_laniakea_piece(screen, board[offset_x][offset_y], (x + offset_x * piece_width, y + offset_y * piece_height), 0)
    
    y += piece_height * 6

    # White house
    if isinstance(selected_field, tuple) and selected_field[1] == 'bottom':
        dh.draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT, 2)
    else:
        dh.draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT, 2)
    # White pieces in white's home space
    dh.draw_pieces_in_house(screen, x, y, board_width, piece_height, board[0][rows], 1)
    # Black pieces in scoring space
    dh.draw_pieces_in_house(screen, x, y + piece_height, board_width, piece_height, board[3][rows], 3)


def stack_top_matches_player(stack, current_player):
    decoded = decode_stack(stack)
    return decoded and decoded[-1] == current_player
    
def handle_mouse_input(mouse_x, mouse_y):
    global selected_field
    global current_player

    board_x = SCREEN_WIDTH / 2 - (piece_width * 8) / 2
    board_y = 4  # upper edge

    board_pixel_width = piece_width * 8
    house_height = piece_height * 2
    field_height = piece_height * 6

    # click in black house (upper house)
    if board_x <= mouse_x < board_x + board_pixel_width and board_y <= mouse_y < board_y + house_height:
        col = int((mouse_x - board_x) // piece_width)
        if current_player == -1:
            selected_field = (col, 'top')
            draw_board()
        return

    # click in 8x6 board
    if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height <= mouse_y < board_y + house_height + field_height:
        col = int((mouse_x - board_x) // piece_width)
        row = int((mouse_y - (board_y + house_height)) // piece_height)
        if 0 <= col < cols and 0 <= row < rows:
            stack = board[col][row]
            if stack_top_matches_player(stack, current_player):
                selected_field = (col, row)
                draw_board()
        return

    # click in white house (lower house)
    if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height + field_height <= mouse_y < board_y + house_height + field_height + house_height:
        col = int((mouse_x - board_x) // piece_width)
        if current_player == 1:
            selected_field = (col, 'bottom')
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