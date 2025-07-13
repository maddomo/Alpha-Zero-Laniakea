"""
Provides a helper function `get_font(font_size)` that returns a cached 
Pygame font object using a specific font.
"""
import pygame


map = {}

def get_font(font_size):
    if font_size in map:
        return map[font_size]
    
    map[font_size] = pygame.font.SysFont("chalkboardse", font_size)
    return map[font_size]