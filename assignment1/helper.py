

def read_big_endian(db, size):
    """
    Read the big endian int from db.
    """
    value = 0
    for _ in range(size):
        byte = ord(db.read(1))
        value = value << 8 | byte
    return value

def read_varint(db):
    """
    Read the varint from db
    """
    value = 0
    for _ in range(8):
        byte = ord(db.read(1))
        value = value << 7 | (byte & 0x7F)
        if byte & 0x80:
            return value
    byte = ord(db.read(1))
    value = value << 8 | byte
    return value