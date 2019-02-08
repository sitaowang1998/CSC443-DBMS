import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

def TableTreeSearch(root_page_no, key, dheader, db):
    """
    Search the key in a table b tree. Return the record found or None if key not found.
    """
    page = BTreePage(root_page_no, dheader, db)


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