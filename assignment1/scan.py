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
        self.path.append((page_no, -1))

    def __iter__(self):
        return self

    def __next__(self):
        



# main for testing
if __name__ == "__main__":
    fileName = "4096.db"
    db = open(fileName, 'rb')
    