from ...LaniakeaHelper import decode_stack, encode_stack
from ..consts import *
from .menu import Menu
from .. import drawhelper as dh
from ...LaniakeaLogic import Board
import pygame

ROWS = 6
COLS = 8

class GameMenu(Menu):

    def __init__(self, screen, swap_menu):
        super().__init__(screen, swap_menu)
        self.board = Board()
        self.visual_board = self.board
        self.selected_field = None
        self.possible_moves = []
        self.current_player = 1
        self.first_move = None
        self.second_move = None
        self.selected_row = None

    def draw_screen(self):

        self.screen.fill(BACKGROUND)
        self.draw_board_helper()
        super().draw_screen()
    
    #def handle_mouse_input(self, mouse_x, mouse_y):
    #    return super().handle_mouse_input(mouse_x, mouse_y)
        

    def handle_mouse_input(self, mouse_x, mouse_y):

        board_x = SCREEN_WIDTH / 2 - (dh.PIECE_WIDTH * 8) / 2
        board_y = 4  # upper edge

        board_pixel_width = dh.PIECE_WIDTH * 8
        house_height = dh.PIECE_WIDTH * 2
        field_height = dh.PIECE_HEIGHT * 6

        field = None

        # Klick in black house
        if board_x <= mouse_x < board_x + board_pixel_width and board_y <= mouse_y < board_y + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == -1:
                field = (-1, -1)

        # Klick in 8x6 board
        elif board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height <= mouse_y < board_y + house_height + field_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            row = int((mouse_y - (board_y + house_height)) // dh.PIECE_HEIGHT)
            row = ROWS - 1 - row
            if 0 <= col < COLS and 0 <= row < ROWS:
                field = (col, row)

        # Klick in white house
        elif board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height + field_height <= mouse_y < board_y + house_height + field_height + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == 1:
                field = (-1, -1)

        # Wenn nichts relevantes geklickt wurde, abbrechen
        if field is None:
            return

        move_state = self.get_move_state()
        if move_state == 0:
            filtered_possible_moves = self.filter_possible_first_moves()
        elif move_state == 1:
            filtered_possible_moves = self.filter_possible_second_moves()
        else: filtered_possible_moves = []

        if field == (-1, -1):
            self.set_selected_field(field)
            return

        stack = self.visual_board[field[0]][field[1]]

        # Klick auf eigenes Piece oder zweiter Klick auf vorheriges Zielfeld
        if self.stack_top_matches_player(stack, self.current_player) or (self.first_move is not None and field == self.first_move[1]):
            if field in filtered_possible_moves:
                if move_state == 0:
                    self.set_move(self.selected_field, field, 1)
                elif move_state == 1:
                    self.set_move(self.selected_field, field, 2)
            else:
                self.set_selected_field(field)
        elif field in filtered_possible_moves:
            if move_state == 0:
                self.set_move(self.selected_field, field, 1)
            elif move_state == 1:
                self.set_move(self.selected_field, field, 2)
        
    def stack_top_matches_player(self, stack, current_player):
        decoded = decode_stack(stack)
        return decoded and decoded[-1] == current_player
    
    def set_selected_field(self, field):
        self.selected_field = field
        self.possible_moves = self.board.get_legal_moves(self.current_player)
        
    
    def get_move_state(self):
        """
        Gibt den aktuellen Status des Zuges für den aktuellen Spieler zurück.
        0: Spieler hat noch keinen ersten Zug ausgewählt
        1: Spieler hat ersten Zug ausgewählt, aber noch keinen zweiten
        2: Spieler hat beide Züge ausgewählt, aber noch keine Reihe zum Teil einschieben
        """
        if self.first_move == None:
            return 0
        if self.second_move == None:
            return 1
        if self.selected_row == None:
            return 2
    
    def set_move(self, from_field, to_field, move_num):
        """
        move_num: 1 für den ersten Move, 2 für den zweiten
        """
        color = 1 if self.current_player == 1 else -1
        player_home = 0 if color == 1 else 1

        if from_field == (-1, -1):
            # Move from home
            x, y = to_field
            stack = decode_stack(self.visual_board[x][y])
            stack.append(color)
            self.visual_board[x][y] = encode_stack(stack)
            self.visual_board[player_home][y]
        else:
            x1, y1 = from_field
            x2, y2 = to_field

            # Remove top piece from stack
            from_stack = decode_stack(self.visual_board[x1][y1])
            piece = from_stack.pop()
            self.visual_board[x1][y1] = encode_stack(from_stack)

            if to_field == (-2,-2):
                # Scoring Move
                #print("SCORED Player", color, "has scored\n")
                self.visual_board[2 + player_home][6] += 1
                #print(f"Moved piece from ({x1}, {y1}) to scoring area")
                #print(self.board[2 + player_home][6], "pieces in scoring area")
                
            elif to_field == (-1,-1):
                # Back Home
                self.visual_board[player_home][6] += 1
                
            else:
                # Normal Move
                to_stack = decode_stack(self.visual_board[x2][y2])
                to_stack.append(piece)
                self.visual_board[x2][y2] = encode_stack(to_stack)

        if move_num == 1:
            self.first_move = (from_field, to_field)
        else: 
            self.second_move = (from_field, to_field)
        
        self.selected_field = None

    def set_second_move(self, from_field, to_field):
        if from_field == -1:
            if self.current_player == 1:
                self.white_homepieces -= 1
            else: 
                self.black_homepieces -= 1
        self.second_move = (from_field, to_field)
        self.selected_field = None

    def complete_move(self):
        self.selected_field = None
        self.first_move = None
        self.second_move = None
        self.selected_row = None
        self.current_player *= -1

    def filter_possible_first_moves(self):
        filtered_list = [n[1] for n in self.possible_moves if n[0] == self.selected_field]
        return filtered_list
    
    def filter_possible_second_moves(self):
        index = -1
        for i, move in enumerate(self.possible_moves):
            if move[0] == self.first_move[0] and move[1] == self.first_move[1]:
                index = i

        move = self.possible_moves[index]
        # move hat Struktur: (start_coord, end_coord, move_list)
        if len(move) != 3:
            return []  # Absicherung, falls Struktur nicht stimmt
        _, _, move_list = move
        # move_list ist eine Liste von Tupeln mit Struktur: (start_field, end_field, weitere Daten)
        # Wir wollen alle end_field, bei denen start_field == selected_field ist
        to_positions = [to_pos for from_pos, to_pos, _ in move_list if from_pos == self.selected_field]
        return to_positions


    def draw_board_helper(self):
        global ROWS, COLS
        piece_height = PIECE_HEIGHT
        piece_width = PIECE_WIDTH
        
        board_width = piece_width * 8
        board_height = piece_height * 8

        x = SCREEN_WIDTH / 2 - board_width / 2
        y = 4

        #background
        pygame.draw.rect(self.screen, FOREGROUND_ACCENT_2, (x, y, board_width, board_height))
        
        # Black house
        if self.selected_field == (-1, -1) and self.current_player == -1:
            dh.draw_rect_with_border(self.screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
        else:
            dh.draw_rect_with_border(self.screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
        # Black pieces in black's home space
        dh.draw_pieces_in_house(self.screen, x, y + piece_height, board_width, piece_height, self.visual_board[1][ROWS], 3)
        # White pieces in scoring space
        dh.draw_pieces_in_house(self.screen, x, y, board_width, piece_height, self.visual_board[2][ROWS], 1)

        y += piece_height * 2

        move_state = self.get_move_state()

        if move_state == 0:
            filtered_possible_moves = self.filter_possible_first_moves()
        elif move_state == 1:
            filtered_possible_moves = self.filter_possible_second_moves()
        else: filtered_possible_moves = []

        #laniakea rows
        for offset_y in range(6):  # 0 → 5 (unten → oben)
            for offset_x in range(COLS):
                board_y = 5 - offset_y  # Invertiere y, sodass 0 = unten
                if (self.selected_field == (offset_x, board_y)):
                    dh.draw_laniakea_piece(self.screen, self.visual_board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 1)
                elif ((offset_x, board_y) in filtered_possible_moves):
                    dh.draw_laniakea_piece(self.screen, self.visual_board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 2)
                else:
                    dh.draw_laniakea_piece(self.screen, self.visual_board[offset_x][board_y], (x + offset_x * piece_width, y + offset_y * piece_height), 0)

        
        y += piece_height * 6

        # White house
        if self.selected_field == (-1, -1) and self.current_player == 1:
            dh.draw_rect_with_border(self.screen, (x, y, board_width, piece_height * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
        else:
            dh.draw_rect_with_border(self.screen, (x, y, board_width, piece_height * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
        # White pieces in white's home space
        dh.draw_pieces_in_house(self.screen, x, y, board_width, piece_height, self.visual_board[0][ROWS], 1)
        # Black pieces in scoring space
        dh.draw_pieces_in_house(self.screen, x, y + piece_height, board_width, piece_height, self.visual_board[3][ROWS], 3)

    