import pygame

from .ui.main_menu import MainMenu
from . import drawhelper as dh
import random
from ..LaniakeaLogic import Board
from ..LaniakeaHelper import decode_stack, encode_stack
from .consts import *
pygame.init()


# 1 = WHITE, -1 = BLACK
current_player = 1

clock = pygame.time.Clock()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
dh.init_images()
board = Board(False)
board[3][2] = 305
board[4][2] = 1
board[0][6] = 1
board[0][0] = -1

selected_field = None
possible_moves = []

def stack_top_matches_player(stack, current_player):
    decoded = decode_stack(stack)
    return decoded and decoded[-1] == current_player

# return a list of possible moves for a (selected) piece
def get_legal_moves_for_piece(piece):
    """
    Gibt alle Zielpositionen (x, y) zurück, zu denen ein Spielstein
    vom Feld `selected_field` (x, y) aus ziehen kann.
    """
    all_moves = board.get_legal_moves(current_player)
    print("all moves:", all_moves)
    x, y = piece
    result = []

    for move in all_moves:
        from_pos, to_pos, _ = move
        if from_pos == (x, y):
            result.append(to_pos)

    return result
    



# Draw a solid blue circle in the center
#pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

#draw_board()

def setter(menu):
    global current_menu
    current_menu = menu


current_menu = MainMenu(screen, setter)

running = True
while running:

    current_menu.draw_screen()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            current_menu.handle_mouse_input(mouse_x, mouse_y)
            #handle_mouse_input(mouse_x, mouse_y)

    # Flip the display
    pygame.display.flip()

    clock.tick(60)

# Done! Time to quit.
pygame.quit()