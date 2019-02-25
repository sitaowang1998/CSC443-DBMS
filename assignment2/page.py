import os

from record import Record

writeCount = 0
readCount = 0

class Page:
    """
    Page provides functions to read and write a page in the database file.
    """

    @staticmethod
    def readPage(db, pSize, pNum=None):
        if pNum != None:
            db.seek(pNum * pSize)
        global readCount
        readCount = readCount + 1
        return db.read(pSize)
    
    @staticmethod
    def writePage(db, data, pSize, pNum=None):
        if pNum != None:
            db.seek(pNum * pSize)
        global writeCount
        writeCount = writeCount + 1
        db.write(data)
    
    @staticmethod
    def clearCount():
        global readCount, writeCount
        readCount = 0
        writeCount = 0
    
    @staticmethod
    def getWriteCount():
        global writeCount
        return writeCount
    
    @staticmethod
    def getReadCount():
        global readCount
        return readCount

class RecordPage:
    """
    RecordPage represents a heap page of records and provide methods to
    read and write records.
    """

    @staticmethod
    def readReocrdPage(db, pSize, pNum=None):
        """
        Return a list of Record in the page.
        """
        data = Page.readPage(db, pSize, pNum)
        records = []
        record_size = Record.getSize()
        for i in range(int(len(data) / record_size)):
            record = Record(data[record_size * i : record_size * (i + 1)])
            if not record.isEmtpy():
                records.append(record)
            else:
                return records
        
        return records

    @staticmethod
    def writeRecordPage(db, records, pSize, pNum=None):
        data = bytearray()
        for r in records:
            data.extend(r.data)
        size = pSize - len(data)
        # If records too long to fit in one page, truncate the data
        if size < 0:
            print("Truncate data")
            data = data[:pSize]
        # If records too short to fill the whole page, fill with ascii 0
        elif size > 0:
            data.extend(bytes(size))
            print("extend data")
        Page.writePage(db, data, pSize, pNum)
    