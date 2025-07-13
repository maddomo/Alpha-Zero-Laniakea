"""
Main game loop that initializes the screen, loads the main menu, and handles user input. 
It continuously draws the current menu and updates the display 
at 60 FPS until the window is closed.
"""
import pygame

from .ui.main_menu import MainMenu
from . import drawhelper as dh
import random
from ..LaniakeaLogic import Board
from ..LaniakeaHelper import decode_stack, encode_stack
from .consts import *
from . import consts
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
dh.init_images()

consts.current_menu = MainMenu(screen)

running = True
while running:

    consts.current_menu.draw_screen()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            consts.current_menu.handle_mouse_input(mouse_x, mouse_y)
            #handle_mouse_input(mouse_x, mouse_y)
        elif event.type == pygame.KEYDOWN:
            consts.current_menu.handle_key_input(event.key)

    # Flip the display
    pygame.display.flip()

    clock.tick(60)

# Done! Time to quit.
pygame.quit()