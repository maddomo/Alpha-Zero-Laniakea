import pygame

BACKGROUND = "#6E97CC"
FOREGROUND = "#FFCF85"
FOREGROUND_ACCENT_1 = "#E4AB72"
FOREGROUND_ACCENT_2 = "#BB854E"
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
    return PIECE_SIZE * 2 + BORDER_SIZE * 3

def get_laniakea_piece_height():
    return PIECE_SIZE * 1 + BORDER_SIZE * 2


# type:
# 00 -> leer leer
# 01 -> leer turt
# ...
def draw_laniakea_piece(surface, type, location):
    global turtle
    x = location[0]
    y = location[1]

    # background
    pygame.draw.rect(surface, FOREGROUND_ACCENT_2, (x, y, PIECE_SIZE * 2 + BORDER_SIZE * 3, PIECE_SIZE + BORDER_SIZE * 2))
    
    # first piece
    x += BORDER_SIZE
    y += BORDER_SIZE
    if (type >> 1) == 0:
        pygame.draw.rect(surface, FOREGROUND, (x, y, PIECE_SIZE, PIECE_SIZE))
    else:
        surface.blit(turtle, (x, y))

    # border
    x += PIECE_SIZE
    pygame.draw.rect(surface, FOREGROUND_ACCENT_1, (x, y, BORDER_SIZE, PIECE_SIZE))

    # second piece
    x += BORDER_SIZE
    if (type % 2) == 0:
        pygame.draw.rect(surface, FOREGROUND, (x, y, PIECE_SIZE, PIECE_SIZE))
    else:
        surface.blit(turtle, (x, y))

    


