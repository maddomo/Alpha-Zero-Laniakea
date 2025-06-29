import pygame
import drawhelper as dh
import random

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

BACKGROUND = "#6E97CC"
FOREGROUND = "#FFCF85"
FOREGROUND_ACCENT = "#BB854E"

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
dh.init_images()

def draw_board():
    
    y = 10
    piece_width = dh.get_laniakea_piece_width()
    piece_height = dh.get_laniakea_piece_height()
    
    board_width = piece_width * 4
    board_height = piece_height * 8

    x = SCREEN_WIDTH / 2 - board_width / 2
    y = SCREEN_HEIGHT / 2 - board_height / 2

    #background
    pygame.draw.rect(screen, FOREGROUND_ACCENT, (x, y, board_width, board_height))

    #first row
    dh.draw_rect_with_border(screen, (x, y, board_width, piece_height), FOREGROUND, FOREGROUND_ACCENT, 2)

    y += piece_height

    #laniakea rows
    for offset_y in range(6):
        for offset_x in range(4):
            dh.draw_laniakea_piece(screen, 3, (x + offset_x * piece_width, y + offset_y * piece_height))
    
    y += piece_height * 6

    #second row
    dh.draw_rect_with_border(screen, (x, y, board_width, piece_height), FOREGROUND, FOREGROUND_ACCENT, 2)

    #dh.draw_laniakea_piece(screen, 3, (x, y))

    #x += piece_width
    #dh.draw_laniakea_piece(screen, 3, (x, y))
    



running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill(BACKGROUND)

    # Draw a solid blue circle in the center
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    draw_board()

    # Flip the display
    pygame.display.flip()




# Done! Time to quit.
pygame.quit()