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
        while page.type == 0x05:
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
        while page.type == 0x05:
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


class IndexTreeScanner:
    """
    An iterator of all the records of a table B tree with inorder traversing.
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
        while page.type == 0x02:
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
        # If at a leaf and there is records left in the leaf, return it
        if self.current_page.type == 0x0a and self.current_index < self.current_page.cell_num:
                return Record(self.current_page.read_cell(self.db, self.current_index).cell.payload)
        # If Reading a record from interior and there is a right pointer, traverse to the leaf
        if self.current_page.type == 0x02 and self.current_index <= self.current_page.cell_num:
            self.path.append((self.current_page.page_no, self.current_index))
            if self.current_index < self.current_page.cell_num:
                page_no = self.current_page.read_cell(db, self.current_index).cell.page_no
            elif self.current_index == self.current_page.cell_num:
                page_no = self.current_page.rightmost_pointer
            page = BTreePage(page_no, self.dheader, self.db)
            while page.type == 0x02:
                self.path.append((page_no, 0))
                page_no = page.read_cell(self.db, 0).cell.page_no
                page = BTreePage(page_no, self.dheader, self.db)
            self.current_page = page
            self.current_index = 0
            return Record(self.current_page.read_cell(self.db, self.current_index).cell.payload)
        
        # Trace up the path to find a interior that is not pointing to rightmost index
        page_no, index = self.path.pop()
        page = BTreePage(page_no, self.dheader, self.db)
        while page.cell_num <= index:
            # If path is empty, i.e. whole tree is traversed, raise StopIteration
            if len(self.path) == 0:
                raise StopIteration
            page_no, index = self.path.pop()
            page = BTreePage(page_no, self.dheader, self.db)
        self.current_page = page
        self.current_index = index
        return Record(self.current_page.read_cell(self.db, self.current_index).cell.payload)

                
            

# main for testing
if __name__ == "__main__":
    fileName = "clustered.db"
    db = open(fileName, 'rb')
    dheader = DHeader(db)
    firstPage = FirstPage(dheader, db)
    r = Record(firstPage.read_cell(db, 0).cell.payload)
    print(r.record)
    page = BTreePage(2, dheader, db)
    print(hex(page.type))
    scanner = IndexTreeScanner(dheader, 2, db)
    count = 0
    for r in scanner:
        count = count + 1
        # print(r.record)
    print(count)
    