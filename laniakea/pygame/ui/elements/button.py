import pygame

from ...fonthelper import get_font
from .element import Element
from ...consts import *

base_padding = 0.5



class Button(Element):
    def __init__(self, screen, pos, text, size, callback=None):
        super().__init__(screen, pos)
        self.text = text
        self.size = size
        self.font = get_font(size)
        self.text_surface = self.font.render(text, True, "#FFFFFF")
        self.callback = callback

    def draw(self):
        text_width = self.text_surface.get_rect().width
        text_height = self.text_surface.get_rect().height

        padding = self.size * base_padding

        box_bounds = (text_width + padding * 2, text_height + padding * 2)

        pygame.draw.rect(self.screen, FOREGROUND_ACCENT_1, self.pos + box_bounds, border_radius=int(min(box_bounds[0] / 2, box_bounds[1] / 2)))

        self.screen.blit(self.text_surface, (self.pos[0] + padding, self.pos[1] + padding))

    def get_bounds(self):
        text_width = self.text_surface.get_rect().width
        text_height = self.text_surface.get_rect().height

        padding = self.size * base_padding

        return (text_width + padding * 2, text_height + padding * 2)
    
    def set_pos(self, pos):
        self.pos = pos

    def click(self):
        if self.callback is not None:
            self.callback()