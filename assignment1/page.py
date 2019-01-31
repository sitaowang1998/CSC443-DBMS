import os

from header import DHeader

page_read_number = 0

class Page:
    
    def __init__(self, page_no, dheader):
        self.page_no = page_no
        self.dheader = dheader

    def seek(self, db):
        db.seek((self.page_no - 1) * self.dheader.page_size)

class BTreePage(Page):
    
    def __init__(self, page_no, dheader, db):
        super().__init__(page_no, dheader)
        self.seek(db)
        self.type = int.from_bytes(db.read(1), byteorder='big', signed=False)
        self.first_free_block = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_num = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.content_area = int.from_bytes(db.read(2), byteorder='big', signed=False)
        db.seek(1, os.SEEK_CUR)
        self.cell_pointer_array = 8
        if self.type == 0x02 or self.type == 0x05:
            self.cell_pointer_array = 12
            self.rightmost_pointer = int.from_bytes(db.read(2), byteorder='big', signed=False) 

    def seek_content_area(self, db):
        self.seek(db)
        db.seek(self.content_area, os.SEEK_CUR)
    
    

class FirstPage(Page):

    def __init__(self, dheader, db):
        super().__init__(1, dheader)
        db.seek(100)
        self.type = int.from_bytes(db.read(1), byteorder='big', signed=False)
        self.first_free_block = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_num = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.content_area = int.from_bytes(db.read(2), byteorder='big', signed=False)
        db.seek(1, os.SEEK_CUR)
        self.cell_pointer_array = 108
        if self.type == 0x02 or self.type == 0x05:
            self.cell_pointer_array = 112
            self.rightmost_pointer = int.from_bytes(db.read(2), byteorder='big', signed=False) 
        
    def seek_content_area(self, db):
        db.seek(self.content_area)

# main for testing
if __name__ == "__main__":

    db = open("4096.db", 'rb')
    dheader = DHeader(db)
    page = BTreePage(2, dheader, db)
    print(page.content_area)
    print(hex(page.type))
    page.seek_content_area(db)
    print(db.read(20))
    firstPage = FirstPage(dheader, db)
    print(firstPage.content_area)
    print(hex(firstPage.type))
    firstPage.seek_content_area(db)
    print(db.read(20))
    db.close()
            

