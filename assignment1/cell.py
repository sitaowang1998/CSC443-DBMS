import os
import struct

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

    
class Record:

    @staticmethod
    def serial_type_to_size(serial_type):
        serial_type_size = [0, 1, 2, 3, 4, 6, 8, 8, 0, 0]
        if serial_type < 10:
            return serial_type_size[serial_type]
        if serial_type == 10 or serial_type == 11:
            return None
        if serial_type >= 12 and serial_type % 2 == 0:
            return int((serial_type - 12) / 2)
        if serial_type >= 13 and serial_type % 2 == 1:
            return int((serial_type - 13) / 2)

    @staticmethod
    def bytes_to_entry(serial_type, byte):
        if serial_type == 0:
            return None
        if serial_type >= 1 and serial_type <= 6:
            print(byte)
            return int.from_bytes(byte, byteorder='big', signed=True)
        if serial_type == 7:
            return struct.unpack('d', byte)
        if serial_type == 8:
            return 0
        if serial_type == 9:
            return 1
        if serial_type == 10 or serial_type == 11:
            return None
        if serial_type == 12 or 13:
            return byte.decode('utf-8')


    def __init__(self, barray):
        self.header_size, offset = Reader.read_varint_string(barray)
        self.serial_types = []
        while offset < self.header_size:
            serialType, newOffset = Reader.read_varint_string(barray[offset:])
            self.serial_types.append(serialType)
            offset = offset + newOffset
        self.column_sizes = [Record.serial_type_to_size(serial_type) for serial_type in self.serial_types]
        self.record = []
        offset = self.header_size
        for i in range(len(self.column_sizes)):
            self.record.append(Record.bytes_to_entry(self.serial_types[i], barray[offset : offset + self.column_sizes[i]]))
            offset = offset + self.column_sizes[i]

# main for testing
if __name__ == "__main__":
    
    barray = b"&\x03\x17#\x0f'\x0fW?='!#\x17\x11!\x11\x11\x15\x11\x1f\x13\x11\x1f\x13\x17\x19\x13#%A9A\x11\x17\x1f++\r\x14{Ms.  Hermila    JSuhr         Fhermila.suhr@gmail.com               Todd Suhr                Cathrine Suhr           Hinojosa     9/4/1992  04:29:56 AM24.91579/9/2014  Q3H220149 SeptemberSep9 Tuesday  Tue2.88 16899112%275-17-8844479-539-4593Peach Orchard             Clay                  Peach Orchard             AR72453South    hjsuhr         oZ%{<6wN!A     "
    r = Record(barray)
    print(r.header_size, r.column_sizes)
    print(r.record)
