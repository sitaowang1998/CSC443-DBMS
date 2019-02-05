import os

from header import DHeader
from helper import Reader

class CellPointer:

    def __init__(self, db):
        """
        Construct the cell pointer given the file pointer.
        """
        self.offset = int.from_bytes(db.read(2), byteorder='big', signed=False)

    def __str__(self):
        return str(self.offset)

class CellPointerArray:

    def __init__(self, db, cell_num):
        self.cell_pointer_array = [CellPointer(db) for _ in range(cell_num)]

    def __str__(self):
        return str([str(cell_pointer) for cell_pointer in self.cell_pointer_array])

class Cell:

    def __init__(self, type):
        self.type = type

class TableLeafCell(Cell):

    def __init__(self, type, db, dheader):
        super().__init__(type)
        self.payload_size = Reader.read_varint(db)
        self.row_id = Reader.read_varint(db)
        U = dheader.page_size - dheader.reserved_size
        X = U-35
        M = ((U-12)*32/255)-23
        K = M+((self.payload_size-M)%(U-4))
        if self.payload_size >= X:
            if K <= X:
                self.payload = db.read(K)
            else:
                self.payload = db.read(M)
            self.first_overflow = int.from_bytes(db.read(4), byteorder='big', signed=False)
        else:
            self.payload = db.read(self.payload_size)

    