
class Reader:

    @staticmethod
    def read_varint(db):
        """
        Read the varint from db
        """
        value = 0
        for _ in range(8):
            byte = int.from_bytes(db.read(1), byteorder='big', signed=False)
            value = value << 7 | (byte & 0x7F)
            if not (byte & 0x80):
                return value
        byte = ord(db.read(1))
        value = value << 8 | byte
        return value