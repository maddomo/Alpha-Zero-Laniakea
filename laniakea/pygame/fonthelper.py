
import pygame


map = {}

def get_font(font_size):
    if font_size in map:
        return map[font_size]
    
    map[font_size] = pygame.font.SysFont("Georgia", font_size)
    return map[font_size]