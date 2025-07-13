import pygame

from laniakea.pygame.ui.difficulty_selector_menu import DifficultySelectorMenu
from laniakea.pygame.ui.game_menu_one import GameMenuOne
from laniakea.pygame.ui.game_menu_small import GameMenuSmall

from .game_menu import GameMenu

from .elements.button import Button
from .menu import Menu
from .. import fonthelper as fh
from ..consts import *
from .. import drawhelper as dh

smallmap_dict = {
    "easy.pth.tar": "Easy",
    "best.pth.tar": "Best",
}

onemove_dict = {
    "easy.pth.tar": "Easy",
    "medium.pth.tar": "Medium",
    "hard.pth.tar": "Hard",
}

class MainMenu(Menu):
    
    def __init__(self, screen):
        super().__init__(screen)
        self.font = fh.get_font(100)
        
        self.button1 = Button(screen, None, "Player vs Player", 48, self.on_button_click)
        self.button1.set_disabled(True)

        bounds1 = self.button1.get_bounds()
        self.button1.set_pos((SCREEN_WIDTH / 2 - bounds1[0] / 2, 300))

        self.button2 = Button(screen, None, "Player vs Player | One Move", 48, self.on_button_click_slimmed)

        bounds2 = self.button2.get_bounds()
        self.button2.set_pos((SCREEN_WIDTH / 2 - bounds2[0] / 2, 450))

        self.button3 = Button(screen, None, "Player vs Player | Small", 48, self.on_button_click_small)
        bounds3 = self.button3.get_bounds()
        self.button3.set_pos((SCREEN_WIDTH / 2 - bounds3[0] / 2, 600))

        self.buttonAI = Button(screen, (10, 10), "AI: Orange", 24, self.on_button_click_ai)
        self.buttonRandomize = Button(screen, (10, 60), "Randomize: On", 24, self.on_button_click_randomize)

        self.ai = -1
        self.randomize = True
        self.elements.append(self.button1)
        self.elements.append(self.button2)
        self.elements.append(self.button3)
        self.elements.append(self.buttonAI)
        self.elements.append(self.buttonRandomize)


    def draw_screen(self):
        self.screen.blit(dh.bg, (0, 0))
        text_width = dh.logo.get_rect().width
        self.screen.blit(dh.logo, (SCREEN_WIDTH / 2 - text_width / 2, -10))
        super().draw_screen()

    def on_button_click(self):
        self.swap_menu(GameMenu(self.screen, self.randomize))

    def on_button_click_slimmed(self):
        def create_game_menu(screen, ai, randomize, model):
            return GameMenuOne(screen, ai, randomize, model)
        self.swap_menu(DifficultySelectorMenu(self.screen, onemove_dict, create_game_menu, self.ai, self.randomize))

    def on_button_click_small(self):
        def create_game_menu(screen, ai, randomize, model):
            return GameMenuSmall(screen, ai, randomize, model)
        self.swap_menu(DifficultySelectorMenu(self.screen, smallmap_dict, create_game_menu, self.ai, self.randomize))

    def on_button_click_ai(self):
        self.ai = (self.ai + 2) % 3 - 1  # Cycle through -1, 0, 1
        self.button1.set_disabled(False if self.ai == 0 else True)
        dict = {
            -1: "AI: Orange",
            0: "AI: Off",
            1: "AI: Blue"
        }
        self.buttonAI.set_text(dict[self.ai])

    def on_button_click_randomize(self):
        self.randomize = not self.randomize
        self.buttonRandomize.set_text(f"Randomize: {'On' if self.randomize else 'Off'}")