import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

class Scanner:
    """
    A iterator that iterate through all components in the database
    """
    def __init__(self, db):
        # Read database header and first page
        self.dheader = DHeader(db)


# main for testing
if __name__ == "__main__":
    fileName = "4096.db"
    db = open(fileName, 'rb')
    