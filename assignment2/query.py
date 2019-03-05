import struct
import os

from page import RecordPage, Page
from hashing import md5Hash, HashHeader

def query(dbFile, indexFile, field, value):
    """
    Query based on the index file.
    """

    indexPageCount = 0
    dataPageCount = 0

    indexDB = open(indexFile, 'rb')
    db = open(dbFile, 'rb')

    indexType, pSize, bNum, indexField = struct.unpack('>IIII', indexDB.read(4 * 4))
    
    entryStruct = struct.Struct('>{0}sII'.format([12, 14, 18][field]))
    entryPerPage = (pSize - 4) // entryStruct.size

    def readRecord(pNum, offset):
        records = RecordPage.readReocrdPage(db, pSize, pNum)
        nonlocal dataPageCount
        dataPageCount += 1
        return records[offset]
    
    def readIndex(pNum):
        indexDB.seek(pSize * pNum)
        overflow = struct.unpack('>I', indexDB.read(4))[0]
        entries = []
        for _ in range(entryPerPage):
            key, pNum, offset = entryStruct.unpack(indexDB.read(entryStruct.size))
            entries.append((key, pNum, offset))
        nonlocal indexPageCount
        indexPageCount += 1
        return overflow, entries
    
    def readDir(index, dirStruct):
        dirPerPage = (pSize - 4) // dirStruct.size
        dirPNum = index // dirPerPage
        dirOffSet = index % dirPerPage
        indexDB.seek(pSize * (dirPNum + 1))
        indexDB.read(4)
        for _ in range(dirOffSet):
            indexDB.read(dirStruct.size)
        return dirStruct.unpack(indexDB.read(dirStruct.size))

    if indexField != field:
        # index file not on field
        raise ValueError
    
    
    if indexType == 0:
        # static hashing

        index = md5Hash(value) % bNum

        overflow, entries = readIndex(index + 1)

        for (key, pNum, offset) in entries:
            if key.strip(bytes(1)).decode() == value:
                record = readRecord(pNum, offset)
                print(record[0], record[1], record[2])

        while overflow != 0:
            overflow, entries = readIndex(overflow)

            for (key, pNum, offset) in entries:
                if key.strip(bytes(1)).decode()  == value:
                    record = readRecord(pNum, offset)
                    print(record[0], record[1], record[2])


        return indexPageCount, dataPageCount
    
    if indexType == 1:
        # extendible hashing

        index = md5Hash(value) % bNum

        (pNum, _) = readDir(index, struct.Struct('>II'))

        if pNum == 0:
            return 0, 0

        overflow, entries = readIndex(pNum)

        for (key, pNum, offset) in entries:
            if key.strip(bytes(1)).decode() == value:
                record = readRecord(pNum, offset)
                print(record[0], record[1], record[2])

        while overflow != 0:
            overflow, entries = readIndex(overflow)

            for (key, pNum, offset) in entries:
                if key.strip(bytes(1)).decode()  == value:
                    record = readRecord(pNum, offset)
                    print(record[0], record[1], record[2])
    
        return indexPageCount, dataPageCount
    
    if indexType == 2:
        # linear hashing

        nextValue = struct.unpack('>I', indexDB.read(4))[0]

        index = md5Hash(value) % bNum
        if index < nextValue:
            index = md5Hash(value) % (2 * bNum)
        
        pNum = readDir(index, struct.Struct('>I'))[0]

        if pNum == 0:
            return 0, 0

        overflow, entries = readIndex(pNum)

        for (key, pNum, offset) in entries:
            if key.strip(bytes(1)).decode() == value:
                record = readRecord(pNum, offset)
                print(record[0], record[1], record[2])

        while overflow != 0:
            overflow, entries = readIndex(overflow)

            for (key, pNum, offset) in entries:
                if key.strip(bytes(1)).decode()  == value:
                    record = readRecord(pNum, offset)
                    print(record[0], record[1], record[2])       

        return indexPageCount, dataPageCount
    

if __name__ == "__main__":
    print("Static Hashing")
    indexPageCount, dataPageCount = query('names.db', 'static.db', 0, 'Nona')
    print()
    print("nIndex:", indexPageCount, 'nData:', dataPageCount)
    print()

    print("=" * 20)

    print("Extendible Hashing")
    indexPageCount, dataPageCount = query('names.db', 'extendible.db', 0, 'Nona')
    print()
    print("nIndex:", indexPageCount, 'nData:', dataPageCount)
    print()

    print("=" * 20)

    print("Linear Hashing")
    indexPageCount, dataPageCount = query('names.db', 'linear.db', 0, 'Nona')
    print()
    print("nIndex:", indexPageCount, 'nData:', dataPageCount)
    print()

    