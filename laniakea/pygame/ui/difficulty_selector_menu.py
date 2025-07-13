import pygame

from laniakea.pygame.ui.game_menu_one import GameMenuOne
from laniakea.pygame.ui.game_menu_small import GameMenuSmall

from .game_menu import GameMenu

from .elements.button import Button
from .menu import Menu
from .. import fonthelper as fh
from ..consts import *
from .. import drawhelper as dh
class DifficultySelectorMenu(Menu):
    
    def __init__(self, screen, dict, create_game_menu, ai, randomize):
        super().__init__(screen)
        self.buttons = []
        for key in dict:
            def on_button_click():
                menu = create_game_menu(screen, ai, randomize, key)
                self.swap_menu(menu)
            button = Button(screen, None, dict[key], 48, on_button_click)
            bounds = button.get_bounds()
            button.set_pos((SCREEN_WIDTH / 2 - bounds[0] / 2, 300 + len(self.buttons) * 100))
            self.buttons.append(button)

        self.elements = self.elements + self.buttons


    def draw_screen(self):
        self.screen.blit(dh.bg, (0, 0))
        text_width = dh.logo.get_rect().width
        self.screen.blit(dh.logo, (SCREEN_WIDTH / 2 - text_width / 2, -10))
        super().draw_screen()