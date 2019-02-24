from multiprocessing.pool import ThreadPool

from record import Record
from page import RecordPage

def sortDB(inDB, outDB, B, pSize, field):
    """
    Sort the db file inDB and output the result into outDB. B is the number of
    buffer pages in memory, pSize is the data page size, field is the index of
    field to sort, which must be 0, 1 or 2.
    """


    inFile = open(inDB, 'rb')
    outFile = open(outDB, 'wb')

    recordsPerPage = int(pSize / Record.getSize())

    # Pass 0: sort all pages using B buffer pages
    pNum = 0
    eof = False
    while not eof:
        buffer = []
        i = 0
        # Read pages into buffer
        while i < B and not eof:
            records = RecordPage.readReocrdPage(inFile, pSize)
            if len(records) == 0:
                eof = True
            elif len(records) < recordsPerPage:
                eof = True
                buffer.append(records)
                pNum = pNum + 1
            else:
                buffer.append(records)
                pNum = pNum + 1
            i = i + 1
        # Sort each page
        p = ThreadPool(4)
        p.map(lambda index: buffer[index].sort(key=lambda r: r[field]), range(len(buffer)))
        # Write buffer pages to output file
        for page in buffer:
            RecordPage.writeRecordPage(outFile, page, pSize)



if __name__ == "__main__":
    sortDB("names.db", "sort.db", 10, 512, 0)

