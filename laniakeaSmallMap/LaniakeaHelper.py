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
INSERT_ROWS = 11
#ROTATE_OPTIONS = 2
SCORING_POS = (-2,-2)
rows = 5
cols = 6
ALL_MOVES = []
for y, x, (dx, dy), h in product(range(rows), range(cols),
                                 [(1,0), (0,1), (-1,0), (0,-1)],
                                 range(1, 4)):
    
    tx, ty = x + dx*h, y + dy*h
    if ty < 0 or ty >= rows or tx < 0 or tx >= cols:
        ALL_MOVES.append(((x, y), HOME_POS))  # Move to home position if out of bounds
    else:
        ALL_MOVES.append(((x, y), (tx, ty)))

# Home-Moves
for x in range(cols):
    ALL_MOVES.append((HOME_POS, (x, 0)))  # Weiß
    ALL_MOVES.append((HOME_POS, (x, rows - 1)))  # Schwarz

# Scoring-Moves for black from 3 rows
for x in range(cols):
    for i in range(3):
        ALL_MOVES.append(((x, i), SCORING_POS))

# Scoring-Moves for white from 3 rows
for x in range(cols):
    for i in range(3):
        ALL_MOVES.append(((x, rows- 1 - i), SCORING_POS))

seen = set()
unique_moves = []
for move in ALL_MOVES:
    if move not in seen:
        unique_moves.append(move)
        seen.add(move)
ALL_MOVES = unique_moves

MAX_MOVES = len(ALL_MOVES)
ACTION_SIZE = MAX_MOVES * INSERT_ROWS
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}
#print(f"Total Moves: {len(ALL_MOVES)}")
#print(MOVE_TO_ID,"\n")
#print(ID_TO_MOVE,"\n")
print(f"Total Actions: {ACTION_SIZE} (Moves: {MAX_MOVES}, Insert Rows: {INSERT_ROWS})")

# ------------------------------------------------
# Encode to single index
# ------------------------------------------------
def encode_action(move, insert_row):
    id1 = MOVE_TO_ID[move]
    return id1 * INSERT_ROWS + insert_row

# ------------------------------------------------
# Decode from index
# ------------------------------------------------
def decode_action(index):
    move_id, insert_row = divmod(index, INSERT_ROWS)
    move = ID_TO_MOVE[move_id]
    return (move, insert_row)

def mirror_action(action):
    move, insert_row = action
    move_copy = list(move)

    if move[0] != HOME_POS and move[0] != SCORING_POS:
        move_copy[0] = (cols - 1 - move[0][0], rows - 1 - move[0][1])

    if move[1] != HOME_POS and move[1] != SCORING_POS:
        move_copy[1] = (cols - 1 - move[1][0], rows - 1 - move[1][1])

    return (tuple(move_copy), rows * 2 - 1 - insert_row if insert_row < rows * 2 else rows * 2)


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
    
print(encode_action(((0, 0), (1, 0)), 0))