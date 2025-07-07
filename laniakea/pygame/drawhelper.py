import pygame
from ..LaniakeaHelper import decode_stack

BACKGROUND = "#6E97CC"
FOREGROUND = "#FFCF85"
FOREGROUND_ACCENT_1 = "#E4AB72"
FOREGROUND_ACCENT_2 = "#BB854E"
SELECTED_COLOR = "#C2FFFD"
WHITE = "#FFFFFF"
BLACK = "#000000"
PIECE_SIZE = 80
BORDER_SIZE = 2
turtle = None

def init_images():
    global turtle
    turtle = pygame.image.load("./assets/turtle.png").convert_alpha()
    turtle = pygame.transform.scale(turtle, (80, 80))



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

def get_laniakea_piece_width():
    return PIECE_SIZE * 1 + BORDER_SIZE * 2

def get_laniakea_piece_height():
    return PIECE_SIZE * 1 + BORDER_SIZE * 2


# type:
# 00 -> leer leer
# 01 -> leer turt
# ...
def draw_laniakea_piece(surface, stack_value, location, selected):
    global turtle
    x = location[0]
    y = location[1]

    # background
    pygame.draw.rect(surface, FOREGROUND_ACCENT_2, (x, y, PIECE_SIZE + BORDER_SIZE * 2, PIECE_SIZE + BORDER_SIZE * 2))
    
    x += BORDER_SIZE
    y += BORDER_SIZE

     # Wenn leer
    if stack_value == 0:
        pygame.draw.rect(surface, FOREGROUND, (x, y, PIECE_SIZE, PIECE_SIZE))
        return
    
    # Wenn Turtle
    if stack_value == -1:
        surface.blit(turtle, (x, y))
        return
    
    # HIER den Hintergrund fürs Feld einfügen, bevor der Stack gezeichnet wird
    if(selected == 1):
        pygame.draw.rect(surface, SELECTED_COLOR, (x, y, PIECE_SIZE, PIECE_SIZE))
    else:
        pygame.draw.rect(surface, FOREGROUND, (x, y, PIECE_SIZE, PIECE_SIZE))

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
        color = WHITE if piece == 1 else BLACK
        pygame.draw.circle(surface, BLACK, (center_x, int(center_y)), radius)
        pygame.draw.circle(surface, color, (center_x, int(center_y)), radius - border_width)


def draw_pieces_in_house(surface, start_x, start_y, width, height, piece_count, piece_color):
    if piece_count == 0:
        return
    
    if piece_color == 1:
        piece_color = WHITE
    elif piece_color == 3:
        piece_color = BLACK

    # Parameter aus draw_laniakea_piece für radius:
    base_diameter = int(height * 0.75)  # Analog PIECE_SIZE * 0.75, hier height als Zellenhöhe
    base_radius = base_diameter // 2.5
    border_width = 3

    max_pieces = 8  # Max. Anzahl Stücke, die ins Haus passen sollen
    spacing = width / max_pieces

    radius = base_radius
    # Optional: Wenn zu viele Stücke, Radius anpassen, damit sie reinpassen
    if piece_count > max_pieces:
        # z.B. skaliere Radius proportional runter
        scale_factor = max_pieces / piece_count
        radius = int(base_radius * scale_factor)
        spacing = width / piece_count

    center_y = start_y + height // 2

    for i in range(piece_count):
        center_x = int(start_x + spacing * i + spacing / 2)
        # Schwarzer Rand
        pygame.draw.circle(surface, BLACK, (center_x, center_y), radius)
        # Innenfarbe (piece_color)
        pygame.draw.circle(surface, piece_color, (center_x, center_y), radius - border_width)



