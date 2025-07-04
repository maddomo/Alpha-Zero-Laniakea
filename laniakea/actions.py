# actions.py
from itertools import product

HOME_POS = (-1, -1)
INSERT_ROWS = 12
ROTATE_OPTIONS = 2
SCORING_POS = (-2,-2)

ALL_MOVES = []
for y, x, (dx, dy), h in product(range(6), range(8),
                                 [(1,0), (0,1), (-1,0), (0,-1)],
                                 range(1, 4)):
    
    tx, ty = x + dx*h, y + dy*h
    if ty < 0 or ty >= 6 or tx < 0 or tx >= 8:
        ALL_MOVES.append(((x, y), HOME_POS))  # Move to home position if out of bounds
    else:
        ALL_MOVES.append(((x, y), (tx, ty)))

# Home-Moves
for x in range(8):
    ALL_MOVES.append((HOME_POS, (x, 0)))  # Weiß
    ALL_MOVES.append((HOME_POS, (x, 5)))  # Schwarz

for x in range(8):
    for i in range(3):
        ALL_MOVES.append(((x, i), SCORING_POS))

# Für Schwarz ist Endzone unterhalb des Boards (y >= 6)
for x in range(8):
    for i in range(3):
        ALL_MOVES.append(((x, 5 -i), SCORING_POS))

seen = set()
unique_moves = []
for move in ALL_MOVES:
    if move not in seen:
        unique_moves.append(move)
        seen.add(move)
ALL_MOVES = unique_moves

MAX_MOVES = len(ALL_MOVES)          # 584
NULL_MOVE = MAX_MOVES               # Sonderwert für "kein zweiter Zug"
TOTAL_MOVES2 = MAX_MOVES + 1        # inkl. NULL_MOVE
ACTION_SIZE = MAX_MOVES * TOTAL_MOVES2 * INSERT_ROWS * ROTATE_OPTIONS
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}
print(f"Total Moves: {len(ALL_MOVES)}")
print(MOVE_TO_ID)
# ------------------------------------------------
# Encode to single index
# ------------------------------------------------
def encode_action(move1, move2=None, insert_row=0, rotate_tile=0):
    """
    Encode: ((move1, move2?), insert_row, rotate) → single int index
    """
    id1 = MOVE_TO_ID[move1]
    id2 = MOVE_TO_ID[move2] if move2 else NULL_MOVE

    index = (((id1 * TOTAL_MOVES2 + id2) * INSERT_ROWS) + insert_row) * ROTATE_OPTIONS + rotate_tile
    return index

# ------------------------------------------------
# Decode from index
# ------------------------------------------------
def decode_action(index):
    """
    Decode: int index → ((move1, move2), insert_row, rotate_tile)
    """
    pair, rotate = divmod(index, ROTATE_OPTIONS)
    pair_row, insert_row = divmod(pair, INSERT_ROWS)
    id1, id2 = divmod(pair_row, TOTAL_MOVES2)

    move1 = ID_TO_MOVE[id1]
    move2 = None if id2 == NULL_MOVE else ID_TO_MOVE[id2]

    return (move1, move2, insert_row, rotate)



