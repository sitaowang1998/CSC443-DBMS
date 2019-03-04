import struct
import hashlib

from record import Record
from page import Page, RecordPage
from staticHash import StaticHashTable
from extendibleHash import ExtendibleHashTable


def hashDB(inDB, indexFile, indexType, buckets, pSize, field):
    if indexType == 0:
        hashTable = StaticHashTable(indexType, pSize, buckets, field)
    elif indexType == 1:
        hashTable = ExtendibleHashTable(indexType, pSize, buckets, field)
    else:
        raise IndexError
    

    # Read the input file and construct the output file
    inFile = open(inDB, 'rb')

    pNum = 0
    records = RecordPage.readReocrdPage(inFile, pSize)
    while len(records) != 0:
        for offset in range(len(records)):
            hashTable.insert(records[offset][field], pNum, offset)
        pNum = pNum + 1
        records = RecordPage.readReocrdPage(inFile, pSize)
    
    inFile.close()
    
    hashTable.writeTable(indexFile)



if __name__ == "__main__":
    # hashDB('names.db', 'static.db', 0, 64, 1024, 0)
    hashDB('names.db', 'extendible.db', 1, 64, 1024, 0)