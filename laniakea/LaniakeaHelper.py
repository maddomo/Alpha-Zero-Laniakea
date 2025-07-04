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