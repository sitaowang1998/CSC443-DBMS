import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

class TableTreeScanner:
    """
    An iterator of all the records of a table B tree.
    """
    def __init__(self, dheader, root_page_no, db):
        self.dheader = dheader
        self.root_page_no = root_page_no
        self.db = db

        # A stack that store pair of page number and the current index of pointer
        self.path = []
        # Initialize the path to point to start
        page_no = root_page_no
        page = BTreePage(root_page_no, dheader, db)
        cell = page.read_cell(db, 0)
        while page.type != 0x0d:
            self.path.append((page_no, 0))
            page_no = cell.cell.page_no
            page = BTreePage(page_no, dheader, db)
            cell = page.read_cell(db, 0)
        self.current_page = page
        self.current_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.current_index = self.current_index + 1
        # If the leaf page has another cell, read it and return
        if self.current_index < self.current_page.cell_num:
            return Record(self.current_page.read_cell(self.db, self.current_index).cell.payload)
        

        page_no, index = self.path.pop()
        page = BTreePage(page_no, self.dheader, self.db)
        index = index + 1

        # Trace up the path to find the first node that has next child
        while page.cell_num < index:
            # If path is empty, i.e. whole tree is traversed, raise StopIteration
            if len(self.path) == 0:
                raise StopIteration
            page_no, index = self.path.pop()
            page = BTreePage(page_no, self.dheader, self.db)
            index = index + 1
        
        # Build the rest of path by reading to leaf
        while page.type != 0x0d:
            self.path.append((page_no, index))
            if index == page.cell_num:
                page_no = page.rightmost_pointer
            else:
                page_no = page.read_cell(self.db, index).cell.page_no
            page = BTreePage(page_no, self.dheader, self.db)
            index = 0
        
        # Read the first cell of leaf and return
        self.current_page = page
        self.current_index = 0
        return Record(page.read_cell(self.db, 0).cell.payload)


# main for testing
if __name__ == "__main__":
    fileName = "4096.db"
    db = open(fileName, 'rb')
    dheader = DHeader(db)
    scanner = TableTreeScanner(dheader, 2, db)
    count = 0
    for r in scanner:
        count = count + 1
    print(count)

    