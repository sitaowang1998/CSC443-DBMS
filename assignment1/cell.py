import os

from helper import Reader

class Cell:

    def __init__(self, type, db):
        self.type = type
        if self.type == 0x05 or self.type == 0x02:
            self.left_child_page_no = int.from_bytes(db.read(4), byteorder='big', signed=False)
        if self.type != 0x05:
            self.payload_size = Reader.read_varint(db)
        if self.type == 0x0d or self.type == 0x05:
            self.rowID = Reader.read_varint(db)
        if self.type != 0x05:
            self.parload = db.read(self.payload_size)
        if self.type != 0x05:
            self.overflow_page = int.from_bytes(db.read(4), byteorder='big', signed=False)