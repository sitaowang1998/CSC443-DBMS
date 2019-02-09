import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

class TableTreeRange:
    """
    An interator that loops thorough the records with key in the range.
    """

    def __init__(self, root_page_no, db, dheader, low, high):
        self.root_page_no = root_page_no
        self.db = db
        self.dheader = dheader
        self.low = low
        self.high = high
        # A stack of page number and index pair
        self.path = []

        # Trace down to the first record in the range
        page_no = root_page_no
        page = BTreePage(page_no, dheader, db)
        while page.type == 0x05:
            index = 0
            while index < page.cell_num and page.read_cell(db, index).cell.rowid < low:
                index = index + 1

            self.path.append((page_no, index))

            if index == page.cell_num:
                page_no = page.rightmost_pointer
            else:
                page_no = page.read_cell(db, index).cell.page_no
            page = BTreePage(page_no, dheader, db)

        # Search in the leaf to find the start
        index = 0
        while index < page.cell_num and page.read_cell(db, index).cell.rowid < low:
                index = index + 1
        if index < page.cell_num:
            self.page = page
            self.index = index
            return
        # If current leaf does not contain leaf larger or equal to low, then trace back the tree and find another leaf.
        page_no, index = self.path.pop()
        page = BTreePage(page_no, dheader, db)
        index = index + 1
        while index > page.cell_num:
            page_no, index = self.path.pop()
            page = BTreePage(page_no, dheader, db)
            index = index + 1
        
        # Trace down to leaf
        self.path.append((page_no, index))
        page = BTreePage(page_no, dheader, db)
        cell = page.read_cell(db, 0)
        while page.type == 0x05:
            self.path.append((page_no, 0))
            page_no = cell.cell.page_no
            page = BTreePage(page_no, dheader, db)
            cell = page.read_cell(db, 0)
        self.page = page
        self.index = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        cell = self.page.read_cell(self.db, self.index)
        if cell.cell.rowid > self.high:
            raise StopIteration
        value = (cell.cell.rowid, Record(cell.cell.payload))
        self.index = self.index + 1

        if self.index < self.page.cell_num:
            return value
        
        page_no, index = self.path.pop()
        page = BTreePage(page_no, self.dheader, self.db)
        index = index + 1
        while index > page.cell_num:
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
        
        self.page = page
        self.index = index
        return value
        

class IndexTreeRange:
    """
    An interator that loops thorough the records with key in the range.
    """

    def __init__(self, root_page_no, db, dheader, low, high):
        self.root_page_no = root_page_no
        self.db = db
        self.dheader = dheader
        self.low = low
        self.high = high
        self.path = []

        # Search down the tree
        page_no = root_page_no
        page = BTreePage(page_no, dheader, db)
        while page.type == 0x02:
            index = 0
            while index < page.cell_num and Record(page.read_cell(db, index).cell.payload).record[0] < low:
                index = index + 1
            
            if index == page.cell_num:
                self.path.append((page_no, index))
                page_no = page.rightmost_pointer
            elif Record(page.read_cell(db, index).cell.payload).record[0] == low:
                self.page = page
                self.index = index
                return
            else:
                self.path.append((page_no, index))
                page_no = page.read_cell(db, index).cell.page_no
            
            page = BTreePage(page_no, dheader, db)

        # Reach a leaf, search for the first element that is in range
        index = 0
        while index < page.cell_num and Record(page.read_cell(db, index).cell.payload).record[0] < low:
                index = index + 1
        if index < page.cell_num:
            self.page = page
            self.index = index
            return
        
        # If all the entries in the leaf is out of range, than search up the tree to find a new entry in interior node
        page_no, index = self.path.pop()
        page = BTreePage(page_no, dheader, db)
        index = index + 1
        while page.cell_num < index:
            page_no, index = self.path.pop()
            page = BTreePage(page_no, dheader, db)
            index = index + 1
        
        if index < page.cell_num:
            self.page = page
            self.index = index
            return
        
        # Reach the rightmost pointer in the page, search down to leaf
        while page.type == 0x02:
            self.path.append((page_no, index))
            if index == page.cell_num:
                page_no = page.rightmost_pointer
            else:
                page_no = page.read_cell(self.db, index).cell.page_no
            page = BTreePage(page_no, self.dheader, self.db)
            index = 0
        
        self.page = page
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        cell = self.page.read_cell(self.db, self.index)
        if Record(cell.cell.payload).record[0] > self.high:
            raise StopIteration
        value = (None, Record(cell.cell.payload))

        self.index = self.index + 1
        
        if self.page.type == 0x02:
            page_no = self.page.page_no
            page = self.page
            index = self.index
            while page.type == 0x02:
                self.path.append((page_no, index))
                if index == page.cell_num:
                    page_no = page.rightmost_pointer
                else:
                    page_no = page.read_cell(self.db, index).cell.page_no
                page = BTreePage(page_no, self.dheader, self.db)
                index = 0
            self.page = page
            self.index = 0

            return value

        if self.index < self.page.cell_num:
            return value

        page_no, index = self.path.pop()
        page = BTreePage(page_no, self.dheader, self.db)
        while index >= page.cell_num:
            if len(self.path) == 0:
                raise StopIteration
            page_no, index = self.path.pop()
            page = BTreePage(page_no, self.dheader, self.db)
        
        if index < page.cell_num:
            self.page = page
            self.index = index
            return value
        
        # Reach the rightmost pointer in the page, search down to leaf
        while page.type == 0x02:
            self.path.append((page_no, index))
            if index == page.cell_num:
                page_no = page.rightmost_pointer
            else:
                page_no = page.read_cell(self.db, index).cell.page_no
            page = BTreePage(page_no, self.dheader, self.db)
            index = 0
        
        self.page = page
        self.index = 0
        return value


 
# main for testing
if __name__ == "__main__":
    fileName = "clustered.db"
    print(fileName)
    db = open(fileName, 'rb')
    dheader = DHeader(db)
    page = BTreePage(2, dheader, db)
    print(hex(page.type))
    low = 171800
    high = 171899
    ranger = IndexTreeRange(2, db, dheader, low, high)
    count = 0
    for rowid, record in ranger:
        # print(rowid, record.record)
        count = count + 1
    print(count)