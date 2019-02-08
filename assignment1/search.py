import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

def TableTreeSearch(root_page_no, key, dheader, db):
    """
    Search the key in a table b tree. Return None if key not found.
    """
    page = BTreePage(root_page_no, dheader, db)
    while page.type == 0x05:
        # Linear search for the key
        index = 0
        while index < page.cell_num and page.read_cell(db, index).cell.rowid < key:
            index = index + 1

        if index == page.cell_num:
            page_no = page.rightmost_pointer
        else:
            page_no = page.read_cell(db, index).cell.page_no
        page = BTreePage(page_no, dheader, db)

    for i in range(page.cell_num):
        cell = page.read_cell(db, i)
        if cell.cell.rowid == key:
            return (cell.cell.rowid, Record(cell.cell.payload).record)
    
    return None
            


class BinarySearch:
    """
    A class that returns index according to binary search.
    """
    def __init__(self, low, high):
        self.low = low
        self.high = high
        self.index = int((low + high) / 2)
    
    def get_index(self):
        return self.index
    
    def left(self):
        self.high = self.index
        self.index = int((self.low + self.high) / 2)
    
    def right(self):
        self.low = self.index
        self.index = int((self.low + self.high) / 2)
    
    def stop(self):
        return self.high - self.low <= 1
    
    def __str__(self):
        return str((self.low, self.index, self.high))


# main for testing
if __name__ == "__main__":
    fileName = "unclustered.db"
    db = open(fileName, 'rb')
    dheader = DHeader(db)
    page = BTreePage(2, dheader, db)
    print(hex(page.type))

    key = 181162
    rowid, record = TableTreeSearch(2, key, dheader, db)
    print(rowid, record)