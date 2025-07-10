import pygame

from laniakea.pygame.consts import SCREEN_WIDTH
from ..LaniakeaHelper import decode_stack
from .consts import *

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

# field_type:
# 0: false
# 1: piece selected
# 2: possible move field
def draw_laniakea_piece(surface, stack_value, location, field_type):
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
        return
    
    # if turtle
    if stack_value == -1:
        surface.blit(turtle, (x, y))
        return
    
    if(field_type == 1):
        pygame.draw.rect(surface, SELECTED_COLOR, (x, y, PIECE_SIZE, PIECE_SIZE))
    elif(field_type == 2):
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

def draw_board_helper(screen, board, selected_field, possible_moves, current_player):
    global rows, cols
    piece_height = PIECE_HEIGHT
    piece_width = PIECE_WIDTH
    
    board_width = piece_width * 8
    board_height = piece_height * 8

    x = SCREEN_WIDTH / 2 - board_width / 2
    y = 4

    #background
    pygame.draw.rect(screen, FOREGROUND_ACCENT_2, (x, y, board_width, board_height))

    # Black house
    if selected_field == (-1, -1) and current_player == -1:
        draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
    else:
        draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
    # Black pieces in black's home space
    draw_pieces_in_house(screen, x, y + piece_height, board_width, piece_height, board[1][ROWS], 3)
    # White pieces in scoring space
    draw_pieces_in_house(screen, x, y, board_width, piece_height, board[2][ROWS], 1)

    y += piece_height * 2

    test = filter_possible_moves(possible_moves, selected_field)

    #laniakea rows
    for offset_y in range(6):  # 0 → 5 (unten → oben)
        for offset_x in range(COLS):
            board_y = 5 - offset_y  # Invertiere y, sodass 0 = unten
            if (selected_field == (offset_x, offset_y)):
                draw_laniakea_piece(screen, board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 1)
            elif ((offset_x, offset_y) in possible_moves):
                draw_laniakea_piece(screen, board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 2)
            else:
                draw_laniakea_piece(screen, board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 0)

    
    y += piece_height * 6

    # White house
    if selected_field == (-1, -1) and current_player == 1:
        draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
    else:
        draw_rect_with_border(screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
    # White pieces in white's home space
    draw_pieces_in_house(screen, x, y, board_width, piece_height, board[0][ROWS], 1)
    # Black pieces in scoring space
    draw_pieces_in_house(screen, x, y + piece_height, board_width, piece_height, board[3][ROWS], 3)

def filter_possible_moves(possible_moves, selected_field):
    filtered_list = [n for n in possible_moves if n[0] == selected_field]
    return filtered_list