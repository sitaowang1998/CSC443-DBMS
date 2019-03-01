import struct
import hashlib

from record import Record
from page import Page, RecordPage

class HashHeader:
    """
    Header for the hash index file.
    """

    def __init__(self, indexType, pSize, bNum, field):
        self.indexType = indexType
        self.pSize = pSize
        self.bNum = bNum
        self.field = field
        self.headerStruct = struct.Struct('>IIII')
        self.keySize = [12, 14, 18][field]
        self.entryStruct = struct.Struct('>{0}sII'.format(self.keySize))
    
    def pack(self):
        return self.headerStruct.pack(self.indexType, self.pSize, self.bNum, self.field)

class HashPage:
    """
    A page of hash entries.
    """
    
    def __init__(self, hashHeader):
        self.hashHeader = hashHeader
        self.overflow = None
        self.entries = []

class HashTable:
    """
    A class for hash table.
    """

    def __init__(self, indexType, pSize, bNum, field):
        self.hashHeader = HashHeader(indexType, pSize, bNum, field)
        self.buckets = []
