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

INSERT_ROWS = 12
MAX_MOVES = 8*6*4*3 + 8 # 8x6 Board, 4 Directions, 3 possible stack heights + 8 moves from home
ROTATE_OPTIONS = 2
ACTION_SIZE = MAX_MOVES * MAX_MOVES * INSERT_ROWS * ROTATE_OPTIONS

HOME_POS = (-1, -1)
ALL_MOVES = []

# Board-Züge (4 Richtungen von jedem der 48 Felder)
for y in range(6):
    for x in range(8):
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            # Multiply with height for stacks
            for i in range(1, 4):
                tx, ty = x + dx * i, y + dy * i
                ALL_MOVES.append(((x, y), (tx, ty)))

# Home-Züge (für Weiß z. B. aus Home auf y=0, für Schwarz y=5)
for x in range(8):
    ALL_MOVES.append((HOME_POS, (x, 0)))  # Weiß
    ALL_MOVES.append((HOME_POS, (x, 5)))  # Schwarz

# Maximal MAX_MOVES Moves verwenden
ALL_MOVES = ALL_MOVES[:MAX_MOVES]

# ---------- Mapping ----------
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}

# ---------- Encode-Funktion ----------
def encode_action(move1, move2, insert_row, rotate_tile):
    """
    Encodes (move1, move2, insert_row, rotate_tile) to a unique integer (0–959999)
    """
    id1 = MOVE_TO_ID[move1]
    id2 = MOVE_TO_ID[move2]
    return ((id1 * MAX_MOVES + id2) * INSERT_ROWS + insert_row) * ROTATE_OPTIONS + rotate_tile

# ---------- Decode-Funktion ----------
def decode_action(index):
    """
    Decodes integer back to (move1, move2, insert_row, rotate_tile)
    """
    pair, rotate = divmod(index, ROTATE_OPTIONS)
    pair_row, insert_row = divmod(pair, INSERT_ROWS)
    id1, id2 = divmod(pair_row, MAX_MOVES)
    return (ID_TO_MOVE[id1], ID_TO_MOVE[id2]), insert_row, rotate

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