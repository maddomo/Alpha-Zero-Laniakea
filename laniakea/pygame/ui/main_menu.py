import pygame

from .game_menu import GameMenu

from .elements.button import Button
from .menu import Menu
from .. import fonthelper as fh
from ..consts import *
class MainMenu(Menu):
    
    def __init__(self, screen, swap_menu):
        super().__init__(screen, swap_menu)
        self.font = fh.get_font(100)
        self.text_surface = self.font.render("Laniakea", True, "#FFFFFF")
        self.button1 = Button(screen, None, "against Player 2", 48, self.on_button_click)
        
        bounds1 = self.button1.get_bounds()
        self.button1.set_pos((SCREEN_WIDTH / 2 - bounds1[0] / 2, 200))

        self.button2 = Button(screen, None, "against AI", 48)

        bounds2 = self.button2.get_bounds()
        self.button2.set_pos((SCREEN_WIDTH / 2 - bounds2[0] / 2, 300))

        self.elements.append(self.button1)
        self.elements.append(self.button2)



    def draw_screen(self):
        self.screen.fill(BACKGROUND)
        text_width = self.text_surface.get_rect().width
        self.screen.blit(self.text_surface, (SCREEN_WIDTH / 2 - text_width / 2, 50))
        super().draw_screen()

    def on_button_click(self):
        self.swap_menu(GameMenu(self.screen, self.swap_menu))