import os
import abc

from header import DHeader
from cell import CellPointer, CellPointerArray, Cell, TableLeafCell

page_read_number = 0

class Page:
    
    def __init__(self, page_no, dheader):
        self.page_no = page_no
        self.dheader = dheader

    def seek(self, db):
        db.seek((self.page_no - 1) * self.dheader.page_size)

    @abc.abstractmethod
    def seek_content_area(self, db):
        return
    
    @abc.abstractmethod
    def seek_cell_pointer(self, db):
        return

class BTreePage(Page):
    
    def __init__(self, page_no, dheader, db):
        super().__init__(page_no, dheader)
        self.seek(db)
        self.type = int.from_bytes(db.read(1), byteorder='big', signed=False)
        self.first_free_block = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_num = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.content_area_offset = int.from_bytes(db.read(2), byteorder='big', signed=False)
        db.seek(1, os.SEEK_CUR)
        self.cell_pointer_array_offset = 8
        if self.type == 0x02 or self.type == 0x05:
            self.cell_pointer_array_offset = 12
            self.rightmost_pointer = int.from_bytes(db.read(2), byteorder='big', signed=False) 
        
        # Construct the cell pointer array
        self.seek(db)
        db.seek(self.cell_pointer_array_offset, os.SEEK_CUR)
        self.cell_pointer_array = CellPointerArray(db, self.cell_num)
        

    def seek_content_area(self, db):
        self.seek(db)
        db.seek(self.content_area_offset, os.SEEK_CUR)
    
    def seek_cell_pointer(self, db):
        self.seek(db)
        db.seek(self.cell_pointer_array_offset, os.SEEK_CUR)
    

class FirstPage(Page):

    def __init__(self, dheader, db):
        super().__init__(1, dheader)
        db.seek(100)
        self.type = int.from_bytes(db.read(1), byteorder='big', signed=False)
        self.first_free_block = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_num = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.content_area_offset = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_pointer_array_offset = 108
        
        # Construct the cell pointer array
        self.seek(db)
        db.seek(self.cell_pointer_array_offset, os.SEEK_CUR)
        self.cell_pointer_array = CellPointerArray(db, self.cell_num)


    def seek_content_area(self, db):
        db.seek(self.content_area_offset)
        
    def seek_cell_pointer(self, db):
        db.seek(self.cell_pointer_array_offset)

# main for testing
if __name__ == "__main__":

    db = open("4096.db", 'rb')
    dheader = DHeader(db)
    page = BTreePage(3, dheader, db)
    print(page.content_area_offset)
    print(hex(page.type))
    print(page.cell_pointer_array)
    page.seek_content_area(db)
    page.seek(db)
    db.seek(page.cell_pointer_array.cell_pointer_array[0].offset, os.SEEK_CUR)
    cell = TableLeafCell(page.type, db, page.dheader)
    print(cell.row_id, cell.payload_size, cell.payload)
    firstPage = FirstPage(dheader, db)
    print(firstPage.content_area_offset)
    print(hex(firstPage.type))
    print(firstPage.cell_pointer_array)
    firstPage.seek_content_area(db)
    print(db.read(20))
    db.close()
            

