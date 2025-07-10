from ...LaniakeaHelper import decode_stack
from ..consts import *
from .menu import Menu
from .. import drawhelper as dh
from ...LaniakeaLogic import Board

ROWS = 6
COLS = 8

class GameMenu(Menu):

    def __init__(self, screen, swap_menu):
        super().__init__(screen, swap_menu)
        self.board = Board()
        self.selected_field = None
        self.possible_moves = []
        self.current_player = 1

    def draw_screen(self):

        self.screen.fill(BACKGROUND)
        dh.draw_board_helper(self.screen, self.board, self.selected_field, self.possible_moves, self.current_player)
        super().draw_screen()
    
    #def handle_mouse_input(self, mouse_x, mouse_y):
    #    return super().handle_mouse_input(mouse_x, mouse_y)
        

    def handle_mouse_input(self, mouse_x, mouse_y):

        board_x = SCREEN_WIDTH / 2 - (dh.PIECE_WIDTH * 8) / 2
        board_y = 4  # upper edge

        board_pixel_width = dh.PIECE_WIDTH * 8
        house_height = dh.PIECE_WIDTH * 2
        field_height = dh.PIECE_HEIGHT * 6

        # click in black house (upper house)
        if board_x <= mouse_x < board_x + board_pixel_width and board_y <= mouse_y < board_y + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == -1:
                self.set_selected_field((-1, -1))
            return

        # click in 8x6 board
        if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height <= mouse_y < board_y + house_height + field_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            row = int((mouse_y - (board_y + house_height)) // dh.PIECE_HEIGHT)
            row = ROWS - 1 - row
            print("selected field: ",(col,row))
            if 0 <= col < COLS and 0 <= row < ROWS:
                stack = self.board[col][row]
                if self.stack_top_matches_player(stack, self.current_player):
                    self.selected_field = (col, row)
                    possible_moves = self.get_legal_moves_for_piece(self.selected_field)
                    #print(possible_moves)
            return

        # click in white house (lower house)
        if board_x <= mouse_x < board_x + board_pixel_width and board_y + house_height + field_height <= mouse_y < board_y + house_height + field_height + house_height:
            col = int((mouse_x - board_x) // dh.PIECE_WIDTH)
            if self.current_player == 1:
                self.set_selected_field((-1, -1))
            return
        
    def stack_top_matches_player(self, stack, current_player):
        decoded = decode_stack(stack)
        return decoded and decoded[-1] == current_player
    
    def get_legal_moves_for_piece(self, piece):
        """
        Gibt alle Zielpositionen (x, y) zurück, zu denen ein Spielstein
        vom Feld `selected_field` (x, y) aus ziehen kann.
        """
        all_moves = self.board.get_legal_moves(self.current_player)
        print("all moves:", all_moves)
        x, y = piece
        result = []

        for move in all_moves:
            from_pos, to_pos, _ = move
            if from_pos == (x, y):
                result.append(to_pos)

        return result
    
    def set_selected_field(self, field):
        self.selected_field = field
        self.possible_moves = self.board.get_legal_moves(self.current_player)
        
