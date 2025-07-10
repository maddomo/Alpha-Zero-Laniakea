def get_top_color(x, y, board):
    list = decode_stack(x, y, board)
    return list[len(list) - 1]

def decode_stack(x, y, board):
    result = []
    for i in range(3):
        n = board[x][y][2+i]
        if n == 0:
            return result
        result.append(n)
    return result

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

# Scoring-Moves for black from 3 rows
for x in range(8):
    for i in range(3):
        ALL_MOVES.append(((x, i), SCORING_POS))

# Scoring-Moves for white from 3 rows
for x in range(8):
    for i in range(3):
        ALL_MOVES.append(((x, 5 - i), SCORING_POS))

seen = set()
unique_moves = []
for move in ALL_MOVES:
    if move not in seen:
        unique_moves.append(move)
        seen.add(move)
ALL_MOVES = unique_moves

MAX_MOVES = len(ALL_MOVES)
ACTION_SIZE = MAX_MOVES * MAX_MOVES * INSERT_ROWS 
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}
#print(f"Total Moves: {len(ALL_MOVES)}")
#print(MOVE_TO_ID,"\n")
#print(ID_TO_MOVE,"\n")

# ------------------------------------------------
# Encode to single index
# ------------------------------------------------
def encode_action(move1, move2, insert_row):
    """
    Encode: ((move1, move2?), insert_row, rotate) → single int index
    """
    id1 = MOVE_TO_ID[move1]
    id2 = MOVE_TO_ID[move2]
    return ((id1 * MAX_MOVES + id2) * INSERT_ROWS) + insert_row

# ------------------------------------------------
# Decode from index
# ------------------------------------------------
def decode_action(index):
    """
    Decode: int index → ((move1, move2), insert_row, rotate_tile)
    """
   
    pair_row, insert_row = divmod(index, INSERT_ROWS)
    id1, id2 = divmod(pair_row, MAX_MOVES)

    if(id1 < 0 or id2 < 0):
        raise ValueError(f"Invalid action index: {index}. id1: {id1}, id2: {id2}")

    move1 = ID_TO_MOVE[id1]
    move2 = ID_TO_MOVE[id2]

    return ((move1, move2), insert_row)

def mirror_action(action):
    """
    Mirror action for player -1
    """
    (move1, move2), insert_row = action

    mirrored_moves = []
    for move in (move1, move2):
        move_copy = list(move)  # Umwandlung in veränderbare Liste

        if move[0] != HOME_POS and move[0] != SCORING_POS:
            move_copy[0] = (7 - move[0][0], 5 - move[0][1])

        if move[1] != HOME_POS and move[1] != SCORING_POS:
            move_copy[1] = (7 - move[1][0], 5 - move[1][1])

        mirrored_moves.append(tuple(move_copy))  # wieder zurück zu Tuple

    return (tuple(mirrored_moves), 11 - insert_row)


def encode_plate(plate):
    if plate == [-1, -1]:
        return 0
    elif plate == [-1, 0]:
        return 1
    elif plate == [0, 0]:
        return 2
    elif plate == [0, -1]:
        return 3
    else:
        raise ValueError("Invalid plate encoding: {}".format(plate))

def decode_plate(index):
    if index == 0:
        return [-1, -1]
    elif index == 1:
        return [-1, 0]
    elif index == 2:
        return [0, 0]
    elif index == 3:
        return [0, -1]
    else:
        raise ValueError("Invalid plate decoding: {}".format(index))