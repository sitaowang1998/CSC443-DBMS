
class Reader:

    @staticmethod
    def read_varint(db):
        """
        Read the varint from db file object
        """
        value = 0
        for _ in range(8):
            byte = int.from_bytes(db.read(1), byteorder='big', signed=False)
            value = value << 7 | (byte & 0x7F)
            if not (byte & 0x80):
                return value
        byte = int.from_bytes(db.read(1), byteorder='big', signed=False)
        value = value << 8 | byte
        return value
    
    @staticmethod
    def read_varint_string(barray):
        """
        Read varint from a string
        """
        value = 0
        for size in range(8):
            byte = barray[size]
            value = value << 7 | (byte & 0x7F)
            if not (byte & 0x80):
                return value, size + 1
        byte = barray[8]
        value = value << 8 | byte
        return value, 9