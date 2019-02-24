import os

from record import Record

class Page:
    """
    Page provides functions to read and write a page in the database file.
    """

    @staticmethod
    def readPage(db, pNum, pSize):
        db.seek(pNum * pSize)
        return db.read(pSize)
    
    @staticmethod
    def writePage(db, pNum, pSize, data):
        db.seek(pNum * pSize)
        db.write(data)

class RecordPage:
    """
    RecordPage represents a heap page of records and provide methods to
    read and write records.
    """

    @staticmethod
    def readReocrdPage(db, pNum, pSize):
        """
        Return a list of Record in the page.
        """
        data = Page.readPage(db, pNum, pSize)
        records = []
        record_size = Record.getSize
        for i in range(len(data) / record_size):
            record = Record(data[record_size * i : record_size * (i + 1) + 1])
            if not record.isEmtpy():
                records.append(record)
            else:
                return records
        
        return records

    @staticmethod
    def writeRecordPage(db, pNum, pSize, records):
        data = bytearray()
        for r in records:
            data.extend(r.data)
        size = pSize - len(data)
        # If records too long to fit in one page, truncate the data
        if size < 0:
            print("Truncate data")
            data = data[:pSize]
        # IF records too short to fill the whole page, fill with ascii 0
        elif size > 0:
            data.extend(bytes(size))
        Page.writePage(db, pNum, pSize, data)
    