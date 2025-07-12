import pygame

from laniakea.pygame.ui.game_menu_one import GameMenuOne
from laniakea.pygame.ui.game_menu_small import GameMenuSmall

from .game_menu import GameMenu

from .elements.button import Button
from .menu import Menu
from .. import fonthelper as fh
from ..consts import *
from .. import drawhelper as dh
class MainMenu(Menu):
    
    def __init__(self, screen, swap_menu):
        super().__init__(screen, swap_menu)
        self.font = fh.get_font(100)
        
        self.button1 = Button(screen, None, "Player vs Player", 48, self.on_button_click)
        
        bounds1 = self.button1.get_bounds()
        self.button1.set_pos((SCREEN_WIDTH / 2 - bounds1[0] / 2, 300))

        self.button2 = Button(screen, None, "Player vs Player (one move)", 48, self.on_button_click_slimmed)

        bounds2 = self.button2.get_bounds()
        self.button2.set_pos((SCREEN_WIDTH / 2 - bounds2[0] / 2, 450))

        self.button3 = Button(screen, None, "Player vs Player (small)", 48, self.on_butoon_click_small)
        bounds3 = self.button3.get_bounds()
        self.button3.set_pos((SCREEN_WIDTH / 2 - bounds3[0] / 2, 600))

        self.elements.append(self.button1)
        self.elements.append(self.button2)
        self.elements.append(self.button3)



    def draw_screen(self):
        self.screen.blit(dh.bg, (0, 0))
        text_width = dh.logo.get_rect().width
        self.screen.blit(dh.logo, (SCREEN_WIDTH / 2 - text_width / 2, -10))
        super().draw_screen()

    def on_button_click(self):
        self.swap_menu(GameMenu(self.screen, self.swap_menu))

    def on_button_click_slimmed(self):
        self.swap_menu(GameMenuOne(self.screen, self.swap_menu))

    def on_butoon_click_small(self):
        self.swap_menu(GameMenuSmall(self.screen, self.swap_menu))