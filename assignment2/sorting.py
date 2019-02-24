from multiprocessing.pool import ThreadPool
import math
import os

from record import Record
from page import RecordPage

def sortDB(inDB, outDB, B, pSize, field):
    """
    Sort the db file inDB and output the result into outDB. B is the number of
    buffer pages in memory, pSize is the data page size, field is the index of
    field to sort, which must be 0, 1 or 2.
    """


    inFile = open(inDB, 'rb')
    outFile = open(outDB, 'w+b')
    tempFile = open('temp', 'w+b')

    recordsPerPage = int(pSize / Record.getSize())

    # Pass 0: sort all pages using B buffer pages
    totalPages = 0
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
                totalPages = totalPages + 1
            else:
                buffer.append(records)
                totalPages = totalPages + 1
            i = i + 1
        # Sort each page
        p = ThreadPool(4)
        p.map(lambda index: buffer[index].sort(key=lambda r: r[field]), range(len(buffer)))
        # Write buffer pages to output file
        for page in buffer:
            RecordPage.writeRecordPage(tempFile, page, pSize)

    inFile.close()
    print("total pages: ", totalPages)

    sortedSize = 1
    inputFile = tempFile
    outputFile = outFile
    passNum = 1
    while sortedSize < totalPages:
        passNum = passNum + 1
        inputFile.seek(0)
        outputFile.seek(0)
        for i in range(math.ceil(totalPages / ((B - 1) * sortedSize))):
            start = i * (B - 1) * sortedSize
            buffer = []
            # Read initial pages
            for j in range(B - 1):
                pNum = start + j * sortedSize
                if pNum < totalPages:
                    page = RecordPage.readReocrdPage(inputFile, pSize, pNum)                
                    buffer.append((page, pNum))
            
            target = []
            firstElements = [b[0][0][field] for b in buffer]
            while len(buffer) != 0:
                minIndex = firstElements.index(min(firstElements))
                page, pNum = buffer[minIndex]
                target.append(page.pop(0))

                # If records is empty, read next page
                if len(page) == 0:
                    pNum = pNum + 1
                    # If next page belongs to another list of sorted page, stop
                    if (pNum - start) % sortedSize == 0:
                        buffer.pop(minIndex)
                        firstElements.pop(minIndex)
                    elif pNum >= totalPages:
                        buffer.pop(minIndex)
                        firstElements.pop(minIndex)
                    else:
                        page = RecordPage.readReocrdPage(inputFile, pSize, pNum)
                        buffer[minIndex] = (page , pNum)
                        firstElements[minIndex] = page[0][field]
                else:
                    firstElements[minIndex] = page[0][field]
                
                # If target is full, write page to outputFile
                if len(target) == recordsPerPage:
                    RecordPage.writeRecordPage(outputFile, target, pSize)
                    target = []


        sortedSize = sortedSize * (B - 1)
        inputFile, outputFile = outputFile, inputFile
            
    # Clean ups
    # Undo the last change
    inputFile, outputFile = outputFile, inputFile
    inputFile.close()
    outputFile.close()
    if outputFile.name == 'temp':
        os.remove('sort.db')
        os.rename('temp', 'sort.db')
    



if __name__ == "__main__":
    sortDB("names.db", "sort.db", 10, 512, 0)

