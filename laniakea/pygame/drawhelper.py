"""
Handles the rendering of all visual elements in the Laniakea game using Pygame.
Includes functions for loading and scaling assets, drawing board pieces and their
states, rendering UI components like arrows, logos, and rule overlays, and visualizing
game mechanics such as stacked pieces, extra tiles, and the player's home area.
"""
import pygame
from laniakea.pygame.fonthelper import get_font
from laniakea.pygame.consts import SCREEN_WIDTH
from ..LaniakeaHelper import decode_stack
from .consts import *
import textwrap

turtle = None
arrow_right, arrow_left = None, None
logo = None
bg = None

rect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

def init_images():
    global turtle, arrow_right, arrow_left, logo, bg
    turtle = pygame.image.load("./assets/turtle.png").convert_alpha()
    turtle = pygame.transform.scale(turtle, (80, 80))
    arrow_right = pygame.image.load("./assets/arrow.png").convert_alpha()
    arrow_right = pygame.transform.scale(arrow_right, (80, 80))
    arrow_left = pygame.transform.rotate(arrow_right, 180)
    logo = pygame.image.load("./assets/logo.png").convert_alpha()
    logo = pygame.transform.scale(logo, (300, 300))
    bg = pygame.image.load("./assets/bg.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))


def draw_rect_with_border(surface, rect, fill_color, border_color, border_width):
    """
    Draw a rectangle with a border on a given surface.

    :param surface: The surface to draw on.
    :param rect: A pygame.Rect or 4-tuple (x, y, width, height).
    :param fill_color: The color to fill the rectangle (inside).
    :param border_color: The color of the border.
    :param border_width: The width of the border in pixels.
    """
    if border_width > 0:
        pygame.draw.rect(surface, border_color, rect)  # Outer rectangle (border)
        inner_rect = pygame.Rect(
            rect[0] + border_width,
            rect[1] + border_width,
            rect[2] - 2 * border_width,
            rect[3] - 2 * border_width
        )
        pygame.draw.rect(surface, fill_color, inner_rect)  # Inner rectangle (fill)
    else:
        pygame.draw.rect(surface, fill_color, rect)  # Just fill if border_width == 0

# field_type:
# 0: false
# 1: piece selected
# 2: possible move field
def draw_laniakea_piece(surface, stack_value, location, color):
    global turtle
    x = location[0]
    y = location[1]

    # background
    pygame.draw.rect(surface, FOREGROUND_ACCENT_2, (x, y, PIECE_SIZE + BORDER_SIZE * 2, PIECE_SIZE + BORDER_SIZE * 2))
    
    x += BORDER_SIZE
    y += BORDER_SIZE

     # if empty
    if stack_value == 0:
        pygame.draw.rect(surface, FOREGROUND, (x, y, PIECE_SIZE, PIECE_SIZE))
    
    # if turtle
    if stack_value == -1:
        surface.blit(turtle, (x, y))
        return
    
    pygame.draw.rect(surface, color, (x, y, PIECE_SIZE, PIECE_SIZE))

    stack = decode_stack(stack_value)
    n = len(stack)
    if n == 0:
        return

    base_diameter = int(PIECE_SIZE * 0.75)
    base_radius = base_diameter // 2.5
    overlap_factor = 0.75
    
    if n == 1:
        spacing = 0
        radius = base_radius
    else:
        max_spacing = (PIECE_SIZE - base_diameter) / (n - 1)
        desired_spacing = base_diameter * overlap_factor
        spacing = min(max_spacing, desired_spacing)
        spacing = max(spacing, 5)
        needed_height = spacing * (n - 1) + base_diameter
        if needed_height > PIECE_SIZE:
            scale_factor = PIECE_SIZE / needed_height
            radius = int(base_radius * scale_factor)
            spacing = int(spacing * scale_factor)
        else:
            radius = base_radius

    stack_height = spacing * (n - 1) + 2 * radius
    field_center_y = y + PIECE_SIZE // 2
    bottom_center_y = field_center_y + stack_height // 2 - radius

    border_width = 3

    for i, piece in enumerate(stack):
        center_x = x + PIECE_SIZE // 2
        center_y = bottom_center_y - i * spacing
        color = PIECE_BLUE if piece == 1 else PIECE_ORANGE
        surface_color = PIECE_BLUE_SURFACE if piece == 1 else PIECE_ORANGE_SURFACE
        pygame.draw.circle(surface, surface_color, (center_x, int(center_y)), radius)
        pygame.draw.circle(surface, color, (center_x, int(center_y)), radius - border_width)


def draw_pieces_in_house(surface, start_x, start_y, width, height, piece_count, piece_color):
    if piece_count == 0:
        return
    
    if piece_color == 1:
        piece_color = PIECE_BLUE
        surface_color = PIECE_BLUE_SURFACE
    elif piece_color == 3:
        piece_color = PIECE_ORANGE
        surface_color = PIECE_ORANGE_SURFACE
    
    base_diameter = int(height * 0.75) 
    base_radius = base_diameter // 2.5
    border_width = 3

    max_pieces = 8  # max pieces in house
    spacing = width / max_pieces

    radius = base_radius

    center_y = start_y + height // 2

    for i in range(piece_count):
        center_x = int(start_x + spacing * i + spacing / 2)
        # Schwarzer Rand
        pygame.draw.circle(surface, surface_color, (center_x, center_y), radius)
        # Innenfarbe (piece_color)
        pygame.draw.circle(surface, piece_color, (center_x, center_y), radius - border_width)

def draw_extra_plate(surface, top_left_pos, plate_tuple):
    """
    Zeichnet das extra Teil (zwei Felder nebeneinander) rechts neben dem Board.
    
    :param surface: Das pygame Surface.
    :param top_left_pos: (x, y) Position oben links.
    :param tile_tuple: Tupel (a, b), wobei a und b 0 oder -1 sein können.
    """
    x, y = top_left_pos

    # Gesamtabmessungen des Teils (zwei Felder + Rahmen außen herum)
    total_width = 2 * (PIECE_SIZE + BORDER_SIZE * 2)
    total_height = PIECE_SIZE + BORDER_SIZE * 2

    # Zeichne äußeren Rahmen
    draw_rect_with_border(
        surface,
        (x, y, total_width, total_height),
        fill_color=FOREGROUND_ACCENT_2,
        border_color=WHITE,
        border_width=3
    )

    # Zeichne die zwei Felder nacheinander
    for i in range(2):
        value = plate_tuple[i]
        field_x = x + i * (PIECE_SIZE + BORDER_SIZE * 2) + BORDER_SIZE
        field_y = y + BORDER_SIZE

        if value == -1:
            surface.blit(turtle, (field_x, field_y))
        else:
            pygame.draw.rect(surface, FOREGROUND, (field_x, field_y, PIECE_SIZE, PIECE_SIZE))

def draw_arrow(surface, pos, right=True):
    """
    Zeichnet einen Pfeil auf das Surface.
    
    :param surface: Das pygame Surface.
    :param pos: (x, y) Position des Pfeils.
    :param direction: 'right' oder 'left'.
    """
    
    surface.blit(arrow_right if right else arrow_left, pos)

def draw_rules_overlay(surface, game_type):
    padding = 30
    overlay_rect = pygame.Rect(150, 50, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100)
    pygame.draw.rect(surface, FOREGROUND_ACCENT_1, overlay_rect) 
    pygame.draw.rect(surface, FOREGROUND_ACCENT_2, overlay_rect, 3)

    font_regular = pygame.font.SysFont("chalkboardse", 20)
    font_bold = pygame.font.SysFont("chalkboardse", 28, bold=True)

    if game_type == 1:
        rules = [
            ("Spielziel:", True),
            "- Bringe 5 eigene Steine ins gegnerische Heimatfeld",
            "- ODER blockiere den Gegner komplett, sodass er keine Züge mehr machen kann",

            ("", False),
            ("1. Aktion: Ziehen", True),
            "- Eine Figur 2 Felder bewegen ODER zwei Figuren je 1 Feld bewegen",
            "- Rückwärts auf das Ausgangsfeld im gleichen Zug ist nicht erlaubt",
            "- Nur freie Felder dürfen betreten werden (Schildkrötenfelder sind gesperrt)",
            "- Figuren dürfen vom Spielfeld springen -> landen im Heimatbereich",
            "- Figuren dürfen auf andere Figuren gezogen werden -> Stapel",
            "- Ein Stapel darf maximal 3 Figuren hoch sein",
            "- Stapelhöhe = mögliche Zugweite",

            ("", False),
            ("2. Aktion: Einschieben", True),
            "- Fragment wird nach dem Ziehen an der Endposition eingeschoben",
            "- Rausgeschobene Figuren -> zurück ins Heimatfeld",
            "- Herausgeschobenes Fragment wird nächste Runde wiederverwendet",
            "- Bei Zielerreichung darf man eine beliebige Reihe wählen",
            "- Bei Rückkehr ins Heimatfeld darf kein Fragment eingeschoben werden",

            ("", False),
            ("", False),
            ("Tastatureingaben", True),
            "ESC drücken, um ausgewählten Stein rückgängig zu machen"
        ]
    else:
        rules = [
            ("Spielziel:", True),
            "- Bringe 1 eigenen Stein ins gegnerische Heimatfeld",
            "- ODER blockiere den Gegner komplett, sodass er keine Züge mehr machen kann",

            ("", False),
            ("1. Aktion: Ziehen", True),
            "- Eine Figur 1 Felder bewegen",
            "- Rückwärts auf das Ausgangsfeld im gleichen Zug ist nicht erlaubt",
            "- Nur freie Felder dürfen betreten werden (Schildkrötenfelder sind gesperrt)",
            "- Figuren dürfen vom Spielfeld springen -> landen im Heimatbereich",
            "- Figuren dürfen auf andere Figuren gezogen werden -> Stapel",
            "- Ein Stapel darf maximal 3 Figuren hoch sein",
            "- Stapelhöhe = mögliche Zugweite",

            ("", False),
            ("2. Aktion: Einschieben", True),
            "- Fragment wird nach dem Ziehen an der Endposition eingeschoben",
            "- Rausgeschobene Figuren -> zurück ins Heimatfeld",
            "- Herausgeschobenes Fragment wird nächste Runde wiederverwendet",
            "- Bei Zielerreichung darf man eine beliebige Reihe wählen",
            "- Bei Rückkehr ins Heimatfeld darf kein Fragment eingeschoben werden",

            ("", False),
            ("", False),
            ("Tastatureingaben", True),
            "ESC drücken, um ausgewählten Stein rückgängig zu machen"
        ]

    line_y = overlay_rect.y + padding
    max_line_width = overlay_rect.width - 2 * padding

    for entry in rules:
        if isinstance(entry, tuple):
            text, bold = entry
        else:
            text, bold = entry, False

        font = font_bold if bold else font_regular
        color = FOREGROUND_ACCENT_2 if bold else WHITE

        wrapped_lines = textwrap.wrap(text, width=120)
        for wrap_line in wrapped_lines:
            text_surface = font.render(wrap_line, True, color)

            text_width = text_surface.get_width()
            x_pos = overlay_rect.x + (overlay_rect.width - text_width) // 2
            surface.blit(text_surface, (x_pos, line_y))

            line_y += font.get_height() + 4 