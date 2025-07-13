import pygame


class Menu:

    def __init__(self, screen):
        self.screen = screen    # set instance attribute
        self.elements = []
        

    def draw_screen(self):
        for element in self.elements:
            element.draw()

    def handle_mouse_input(self, mouse_x, mouse_y):
        for element in self.elements:
            pos = element.get_pos()
            bounds = element.get_bounds()

            if mouse_x >= pos[0] and mouse_x <= pos[0] + bounds[0] and mouse_y >= pos[1] and mouse_y <= pos[1] + bounds[1]:
                element.click()

    def handle_key_input(self, key):
        pass

    def swap_menu(self, menu):
        from .. import consts
        consts.current_menu = menu