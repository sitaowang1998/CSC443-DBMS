from header import DHeader

page_read_number = 0

class Page:
    
    def __init__(self, page_no, dheader):
        self.page_no = page_no
        self.dheader = dheader

    def seek(self, db):
        db.seek((self.page_no - 1) * self.dheader.get_page_size())

class BTreePage(Page):
    
    def __init__(self, page_no, dheader, db):
        super().__init__(page_no, dheader)
        self.seek(db)
        self.type = int.from_bytes(db.read(1), byteorder='big', signed=False)
        self.first_free_block = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.cell_num = int.from_bytes(db.read(2), byteorder='big', signed=False)
        self.content_area = int.from_bytes(db.read(2), byteorder='big', signed=False)


# main for testing
if __name__ == "__main__":

    db = open("4096.db", 'rb')
    dheader = DHeader(db)
    page = BTreePage(2, dheader, db)
    db.close()
            

