import os

from header import DHeader

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

