def cast_bit_to_boolean(b):
    if b == 0:
        return False
    elif b == 1:
        return True
    else:
        raise RuntimeError('Argument is expected to be 0 or 1, but was passed ' + b)
