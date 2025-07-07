def encode_stack(list):

    result = 0

    for i in list:
        result <<= 4
        result |= (0b1 if i == 1 else 0b11)

    return result

def get_stack_height(n):
    count = 0
    while n > 0:
        nibble = n & 0xF  # mask lowest 4 bits
        if nibble != 0:
            count += 1
        n >>= 4  # shift right by 4 bits (1 nibble)
    return count

def get_top_color(n):
    list = decode_stack(n)
    return list[len(list) - 1]

def decode_stack(n):
    result = []
    if n is None or n == 0:
        return result
    while n > 0:
        nibble = n & 0xF  # mask lowest 4 bits
        if nibble != 0:
            result.insert(0, 1 if nibble == 1 else -1)
        n >>= 4  # shift right by 4 bits (1 nibble)
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
ACTION_SIZE = MAX_MOVES * MAX_MOVES * INSERT_ROWS * ROTATE_OPTIONS
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}
#print(f"Total Moves: {len(ALL_MOVES)}")
#print(MOVE_TO_ID,"\n")
#print(ID_TO_MOVE,"\n")

# ------------------------------------------------
# Encode to single index
# ------------------------------------------------
def encode_action(move1, move2, insert_row, rotate_tile):
    """
    Encode: ((move1, move2?), insert_row, rotate) → single int index
    """
    id1 = MOVE_TO_ID[move1]
    id2 = MOVE_TO_ID[move2]
    return (((id1 * MAX_MOVES + id2) * INSERT_ROWS) + insert_row) * ROTATE_OPTIONS + rotate_tile

# ------------------------------------------------
# Decode from index
# ------------------------------------------------
def decode_action(index):
    """
    Decode: int index → ((move1, move2), insert_row, rotate_tile)
    """
    pair, rotate = divmod(index, ROTATE_OPTIONS)
    pair_row, insert_row = divmod(pair, INSERT_ROWS)
    id1, id2 = divmod(pair_row, MAX_MOVES)

    move1 = ID_TO_MOVE[id1]
    move2 = ID_TO_MOVE[id2]

    return ((move1, move2), insert_row, rotate)

def mirror_action(action):
    """
    Mirror action for player -1
    """
    (move1, move2), insert_row, rotate_tile = action

    mirrored_moves = []
    for move in (move1, move2):
        move_copy = list(move)  # Umwandlung in veränderbare Liste

        if move[0] != HOME_POS and move[0] != SCORING_POS:
            move_copy[0] = (7 - move[0][0], 5 - move[0][1])

        if move[1] != HOME_POS and move[1] != SCORING_POS:
            move_copy[1] = (7 - move[1][0], 5 - move[1][1])

        mirrored_moves.append(tuple(move_copy))  # wieder zurück zu Tuple

    return (tuple(mirrored_moves), 11 - insert_row, rotate_tile)


def encode_plate(plate):
    if plate == [-1, -1]:
        return 0
    elif plate in [[-1, 0], [0, -1]]:
        return 1
    elif plate == [0, 0]:
        return 2
    else:
        raise ValueError("Invalid plate encoding: {}".format(plate))

def decode_plate(index):
    if index == 0:
        return [-1, -1]
    elif index == 1:
        return [-1, 0]
    elif index == 2:
        return [0, 0]
    else:
        raise ValueError("Invalid plate decoding: {}".format(index))