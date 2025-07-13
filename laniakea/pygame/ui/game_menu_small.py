"""
GUI for Laniakea with a 6x5 board and two actions per move.
1. action: move a piece
2. action: insert a plate into the board
"""
from laniakea.pygame.fonthelper import get_font
from laniakeaSmallMap.pytorch.NNet import NNetWrapper
from laniakeaSmallMap.LaniakeaGame import LaniakeaGame
from laniakeaSmallMap.LaniakeaHelper import decode_stack, encode_stack, decode_plate, encode_action
from ..consts import *
from .menu import Menu
from .. import drawhelper as dh
from laniakeaSmallMap.LaniakeaLogic import Board
import pygame
import copy
from .elements.button import Button

ROWS = 5
COLS = 6

class GameMenuSmall(Menu):

    def __init__(self, screen, ai, randomize, ai_model=None):
        super().__init__(screen)
        self.board = Board(randomize)
        self.visual_board = copy.deepcopy(self.board)
        self.selected_field = None
        self.current_player = 1
        self.first_move = None
        self.selected_row = None
        self.possible_moves = self.board.get_legal_moves(self.current_player)
        self.tick = 0
        self.font = get_font(48)
        self.white_won_text = self.font.render("Blue has won!", True, "#FFFFFF")
        self.black_won_text = self.font.render("Orange has won!", True, "#FFFFFF")
        self.who_won = -1  # -1 = no one, 0 = white, 1 = black
        self.won_tick = -1 # -1 = no one has won yet, otherwise the tick when the game was won
        self.upper_board_edge = (SCREEN_HEIGHT - BOARD_HEIGHT_SMALL - (PIECE_WIDTH * 4)) / 2 + 30
        # rules-button
        self.showing_rules = False  
        self.rules_button = Button(screen, None, "Rules", 32, self.on_rules_click)
        bounds = self.rules_button.get_bounds()
        self.rules_button.set_pos((SCREEN_WIDTH - bounds[0] - 10, 10))
        self.elements.append(self.rules_button)

        if ai != 0:
            from laniakea.pygame.ai.ai_setup import AIPlayer
            game = LaniakeaGame()
            self.ai_player = AIPlayer(game, ai, NNetWrapper(game), "smallmap")
            if ai == 1:
                self.play_ai_move()


    def draw_screen(self):

        self.screen.blit(dh.bg, (0, 0))
        self.draw_board_helper()

        if self.who_won != -1:
            won_text = self.white_won_text if self.who_won == 0 else self.black_won_text
            self.screen.blit(won_text, (SCREEN_WIDTH / 2 - won_text.get_rect().width / 2, SCREEN_HEIGHT / 2 - won_text.get_rect().height / 2))
        if self.won_tick != -1 and self.tick - self.won_tick > 60 * 5:
            from laniakea.pygame.ui.main_menu import MainMenu
            self.swap_menu(MainMenu(self.screen, self.swap_menu))
            self.won_tick = -1

        self.tick += 1
        super().draw_screen()

        if self.showing_rules:
            dh.draw_rules_overlay(self.screen, 2)

    def on_rules_click(self):
        self.showing_rules = not self.showing_rules 

    def handle_mouse_input(self, mouse_x, mouse_y):
        """
        Handles mouse input by determining which board element or field was clicked based on the mouse coordinates.
        - Checks if any UI element was clicked and triggers its click event.
        - Calculates if the click was inside the black house, the main 8x6 board, or the white house, and identifies the corresponding field.
        - Based on the current move state, filters possible moves and updates the selected field or move.
        """
        for element in self.elements:
            pos = element.get_pos()
            bounds = element.get_bounds()

            if pos[0] <= mouse_x <= pos[0] + bounds[0] and pos[1] <= mouse_y <= pos[1] + bounds[1]:
                element.click()
                return

        board_x = SCREEN_WIDTH / 2 - (dh.PIECE_WIDTH * COLS_SMALL) / 2
        board_y = self.upper_board_edge  # upper edge

        board_pixel_width = dh.PIECE_WIDTH * COLS_SMALL
        house_height = dh.PIECE_WIDTH * 2
        field_height = dh.PIECE_HEIGHT * ROWS_SMALL

        field = None
        move_state = self.get_move_state()

        # click in black house
        if board_x <= mouse_x < board_x + board_pixel_width and board_y <= mouse_y < board_y + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == -1:
                field = (-1, -1)
            if self.current_player == 1:
                field = (-2, -2)

        # click in board
        elif board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height <= mouse_y < board_y + house_height + field_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            row = int((mouse_y - (board_y + house_height)) // dh.PIECE_HEIGHT)
            row = ROWS - 1 - row
            if 0 <= col < COLS and 0 <= row < ROWS:
                field = (col, row)

        # click in white house
        elif board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height + field_height <= mouse_y < board_y + house_height + field_height + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == 1:
                field = (-1, -1)
            if self.current_player == -1:
                field = (-2, -2)

        if field == (-1, -1):
            self.set_selected_field(field)
            return

        if move_state == 0:
            filtered_possible_moves = self.filter_possible_first_moves()
        else: filtered_possible_moves = []

        # click outside of the board
        if field is None:
            if move_state == 1:
                insert_moves = self.filter_possible_insert_moves()
                for insert_move in insert_moves:
                    x = SCREEN_WIDTH / 2 - BOARD_WIDTH_SMALL / 2 - PIECE_WIDTH + (PIECE_WIDTH * (COLS_SMALL + 1) * (insert_move // ROWS_SMALL))
                    y = board_y + PIECE_HEIGHT * (ROWS_SMALL + 1) - (PIECE_HEIGHT * (insert_move % ROWS_SMALL))
                    if mouse_x >= x and mouse_x <= x + PIECE_WIDTH and mouse_y >= y and mouse_y <= y + PIECE_HEIGHT:
                        self.selected_row = insert_move
                        self.complete_move()
                        print(insert_move)
                return
            elif (-1, -1) in filtered_possible_moves:
                field = (-1, -1)
            else:
                return


        stack = self.visual_board[field[0]][field[1]]

        # click on own piece or second click on possible move field
        if self.stack_top_matches_player(stack, self.current_player) or (self.first_move is not None and field == self.first_move[1]):
            if field in filtered_possible_moves:
                if move_state == 0:
                    self.set_move(self.selected_field, field)
            else:
                self.set_selected_field(field)
        elif field in filtered_possible_moves:
            if move_state == 0:
                self.set_move(self.selected_field, field)
        

        
    def stack_top_matches_player(self, stack, current_player):
        """
        Returns if piece on top of a stack is one of the current player's
        """
        decoded = decode_stack(stack)
        return decoded and decoded[-1] == current_player
    
    def set_selected_field(self, field):
        self.selected_field = field
        self.possible_moves = self.board.get_legal_moves(self.current_player)
        
    def get_move_state(self):
        """
        Returns the current move state for the active player.
        0: Player has not selected the move yet
        2: Player has selected his move but not yet chosen a row to insert
        """
        if self.first_move == None:
            return 0
        if self.selected_row == None:
            return 1
    
    def set_move(self, from_field, to_field):
        """
        Updates the visual board by moving a piece from one field to another.
        Handles moves from home, scoring moves, returning home, and normal moves.
        Sets the first move and completes the move if the piece returns home.
        """
        color = 1 if self.current_player == 1 else -1
        player_home = 0 if color == 1 else 1

        if from_field == (-1, -1):
            # Move from home
            x, y = to_field
            stack = decode_stack(self.visual_board[x][y])
            stack.append(color)
            self.visual_board[x][y] = encode_stack(stack)
            self.visual_board[player_home][ROWS] -= 1
        else:
            x1, y1 = from_field
            x2, y2 = to_field

            # Remove top piece from stack
            from_stack = decode_stack(self.visual_board[x1][y1])
            piece = from_stack.pop()
            self.visual_board[x1][y1] = encode_stack(from_stack)

            if to_field == (-2,-2):
                # Scoring Move
                self.visual_board[2 + player_home][ROWS_SMALL] += 1
                
            elif to_field == (-1,-1):
                # Back Home
                self.visual_board[player_home][ROWS_SMALL] += 1
                
            else:
                # Normal Move
                to_stack = decode_stack(self.visual_board[x2][y2])
                to_stack.append(piece)
                self.visual_board[x2][y2] = encode_stack(to_stack)

        self.first_move = (from_field, to_field)
        if to_field == (-1, -1):
            self.selected_row = 12
            self.complete_move()
            
        self.selected_field = None

    def complete_move(self):
        """
        Finalizes the current player's move by executing it on the board, updating the visual board state, 
        and resetting move-related selections. Checks for a win condition and switches to the next player.
        """
        self.board.execute_move((self.first_move, self.selected_row), self.current_player)
        self.visual_board = copy.deepcopy(self.board)
        self.selected_field = None
        self.first_move = None
        self.selected_row = None
        if self.board.is_win(self.current_player):
            self.who_won = 0 if self.current_player == 1 else 1
            self.won_tick = self.tick
        self.current_player *= -1
        if self.ai_player is not None:
            self.play_ai_move()

    def play_ai_move(self):
        """
        Gets the AI's move, executes it on the board, updates the visual board,
        checks for a win, and switches to the other player.
        """
        action = self.ai_player.get_action(self.board)
        self.board.execute_move(action, self.current_player)
        self.visual_board = copy.deepcopy(self.board)
        if self.board.is_win(self.current_player):
            self.who_won = 0 if self.current_player == 1 else 1
            self.won_tick = self.tick
        self.current_player *= -1

    def filter_possible_first_moves(self):
        """
        Returns all possible fields for the position of the current selected field
        """
        filtered_list = [n[1] for n in self.possible_moves if n[0] == self.selected_field]
        return filtered_list
    
    def filter_possible_insert_moves(self):
        """
        Returns all possible insert moves based on the selected first move.
        """
        if self.first_move is None:
            return []
        
        return [n[2] for n in self.possible_moves if n[0] == self.first_move[0] and n[1] == self.first_move[1]][0]


    def draw_board_helper(self):
        """
        Controls how the game board is drawn. It decides which fields and areas to highlight 
        based on the current player and move state. Then it calls helper functions to actually draw the board, 
        the pieces, and the possible moves on the screen.
        """
        move_state = self.get_move_state()

        if move_state == 0:
            filtered_possible_moves = self.filter_possible_first_moves()            
        else: filtered_possible_moves = []

        if (-1, -1) in filtered_possible_moves:
            self.screen.fill(MOVE_COLOR)
        
        x = SCREEN_WIDTH / 2 - BOARD_WIDTH_SMALL / 2
        y = self.upper_board_edge

        #background
        pygame.draw.rect(self.screen, FOREGROUND_ACCENT_2, (x, y, BOARD_WIDTH_SMALL, BOARD_HEIGHT_SMALL))
        # Black house
        if self.selected_field == (-1, -1) and self.current_player == -1:
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
        elif (self.current_player == 1 and (-2, -2) in filtered_possible_moves):
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), MOVE_COLOR, FOREGROUND_ACCENT_2, 2)
        else:
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
        # Black pieces in black's home space
        dh.draw_pieces_in_house(self.screen, x, y + PIECE_HEIGHT, BOARD_WIDTH_SMALL, PIECE_HEIGHT, self.visual_board[1][ROWS], 3)
        # White pieces in scoring space
        dh.draw_pieces_in_house(self.screen, x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT, self.visual_board[2][ROWS], 1)

        y += PIECE_HEIGHT * 2

        #laniakea rows
        for offset_y in range(ROWS):  
            for offset_x in range(COLS):
                board_y = 4 - offset_y  # invert y so that 0 = bottom
                color = self.get_field_color((offset_x, board_y), filtered_possible_moves)
                dh.draw_laniakea_piece(self.screen, self.visual_board[offset_x][board_y], (x + offset_x * PIECE_WIDTH, y + offset_y * PIECE_HEIGHT), color)
                
        y += PIECE_HEIGHT * ROWS

        # White house
        if self.selected_field == (-1, -1) and self.current_player == 1:
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), SELECTED_COLOR, FOREGROUND_ACCENT_2, 2)
        elif (self.current_player == -1 and (-2, -2) in filtered_possible_moves):
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), MOVE_COLOR, FOREGROUND_ACCENT_2, 2)
        else:
            dh.draw_rect_with_border(self.screen, (x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT * 2), FOREGROUND, FOREGROUND_ACCENT_2, 2)
        # White pieces in white's home space
        dh.draw_pieces_in_house(self.screen, x, y, BOARD_WIDTH_SMALL, PIECE_HEIGHT, self.visual_board[0][ROWS], 1)
        # Black pieces in scoring space
        dh.draw_pieces_in_house(self.screen, x, y + PIECE_HEIGHT, BOARD_WIDTH_SMALL, PIECE_HEIGHT, self.visual_board[3][ROWS], 3)

        insert_plate = decode_plate(self.visual_board[4][ROWS])
        dh.draw_extra_plate(self.screen, (10, 10), insert_plate)

        if move_state == 1:
            list = self.filter_possible_insert_moves()
            for num in list:
                x = SCREEN_WIDTH / 2 - BOARD_WIDTH_SMALL / 2 - PIECE_WIDTH + (PIECE_WIDTH * (COLS_SMALL + 1) * (num // ROWS_SMALL))
                y = self.upper_board_edge + PIECE_HEIGHT * (ROWS_SMALL + 1) - (PIECE_HEIGHT * (num % ROWS_SMALL))
                
                dh.draw_arrow(self.screen, (x, y), not num // ROWS_SMALL)
            pass

    def get_field_color(self, pos, filtered_possible_moves): 
        if self.selected_field == pos:
            return SELECTED_COLOR
        elif pos in filtered_possible_moves:
            return MOVE_COLOR
        elif (self.first_move is not None and pos in self.first_move):
            return FOREGROUND_ACCENT_1
        else:
            return FOREGROUND
        
    def cancel_selection(self):
        if(self.selected_field is not None):
            self.selected_field = None

    def handle_key_input(self, key):
        if key == pygame.K_ESCAPE:
            if self.get_move_state() == 0:
                self.cancel_selection()