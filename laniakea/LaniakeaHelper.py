
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
    while n > 0:
        nibble = n & 0xF  # mask lowest 4 bits
        if nibble != 0:
            result.insert(0, 1 if nibble == 1 else -1)
        n >>= 4  # shift right by 4 bits (1 nibble)
    return result

INSERT_ROWS = 12
MAX_MOVES = 200
ACTION_SIZE = MAX_MOVES * MAX_MOVES * INSERT_ROWS

HOME_POS = (-1, -1)
ALL_MOVES = []

# Board-Züge (4 Richtungen von jedem der 48 Felder)
for y in range(6):
    for x in range(8):
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            tx, ty = x + dx, y + dy
            if 0 <= tx < 8 and 0 <= ty < 6:
                ALL_MOVES.append(((x, y), (tx, ty)))

# Home-Züge (für Weiß z. B. aus Home auf y=0, für Schwarz y=5)
for x in range(8):
    ALL_MOVES.append((HOME_POS, (x, 0)))  # Weiß
    ALL_MOVES.append((HOME_POS, (x, 5)))  # Schwarz

# Maximal 200 Moves verwenden
ALL_MOVES = ALL_MOVES[:MAX_MOVES]

# ---------- Mapping ----------
MOVE_TO_ID = {m: i for i, m in enumerate(ALL_MOVES)}
ID_TO_MOVE = {i: m for m, i in MOVE_TO_ID.items()}

# ---------- Encode-Funktion ----------
def encode_action(move1, move2, insert_row):
    """
    Kodiert (move1, move2, insert_row) als eindeutigen Integer (0–479999)
    """
    id1 = MOVE_TO_ID[move1]
    id2 = MOVE_TO_ID[move2]
    return (id1 * MAX_MOVES + id2) * INSERT_ROWS + insert_row

# ---------- Decode-Funktion ----------
def decode_action(index):
    """
    Dekodiert Integer zurück zu (move1, move2, insert_row)
    """
    pair, insert_row = divmod(index, INSERT_ROWS)
    id1, id2 = divmod(pair, MAX_MOVES)
    return ID_TO_MOVE[id1], ID_TO_MOVE[id2], insert_row


