import struct
import hashlib
import os
import matplotlib.pyplot as plt

from hashing import HashHeader, HashPage, HashTable, md5Hash

class StaticHashPage(HashPage):
    """
    A hash page for static hash table.
    """

    def __init__(self, hashHeader):
        super().__init__(hashHeader)
        self.size = (hashHeader.pSize - 4) / hashHeader.entryStruct.size
    
    def insert(self, key, pNum, offset):
        """
        Insert a new page into bucket, may cause an increase of overflow page.
        """

        # Search for the last page in the overflow chain
        page = self
        entry = self.hashHeader.entryStruct.pack(key.encode(), pNum, offset)

        while len(page.entries) == page.size and page.overflow != None:
            page = page.overflow
        
        if len(page.entries) < page.size:
            page.entries.append(entry)
            return
        
        # The last page is full, insert a new overflow page
        newPage = StaticHashPage(self.hashHeader)
        page.overflow = newPage
        newPage.entries.append(entry)
    
class StaticHashTable(HashTable):
    """
    A static hash table.
    """

    def __init__(self, indexType, pSize, bNum, field):
        super().__init__(indexType, pSize, bNum, field)
        self.buckets = [StaticHashPage(self.hashHeader) for _ in range(bNum)]
    
    def insert(self, key, pNum, offset):
        index = md5Hash(key) % self.hashHeader.bNum
        self.buckets[index].insert(key, pNum, offset)

    def writeTable(self, indexFile):
        """
        Write the table into file named indexFile.
        """
        overflowPageCount = 0
        pageHist = []

        f = open(indexFile, 'wb')

        header = self.hashHeader
        # Write the first page with header only
        firstPage = header.pack() + bytearray(header.pSize - header.headerStruct.size)
        f.write(firstPage)


        # Write all the primary pages first
        for p in self.buckets:
            page = struct.pack('>I', 0)
            for entry in p.entries:
                page = page + entry
            page = page + bytearray(header.pSize - len(page))
            f.write(page)

        # Write all the overflow pages
        for i in range(header.bNum):
            p = self.buckets[i]

            pageCount = 1

            if p.overflow != None:
                f.seek(0, os.SEEK_END)
                pNum = int(f.tell() / header.pSize)
                # Write the page number of first overflow page into primary page
                primary_index = 1 + i
                f.seek(primary_index * header.pSize, os.SEEK_SET)
                f.write(struct.pack('>I', pNum))
                
                f.seek(0, os.SEEK_END)
                p = p.overflow
                while p != None:
                    page = struct.pack('>I', 0)
                    if p.overflow != None:
                        page = struct.pack('>I', pNum + 1)

                    for entry in p.entries:
                        page = page + entry
                    
                    page = page + bytearray(header.pSize - len(page))

                    f.write(page)
                    overflowPageCount += 1
                    pageCount += 1

                    pNum = pNum + 1
                    p = p.overflow
            
            pageHist.append(pageCount)

        # Print the info
        print("nBucket:", len(self.buckets))
        print("nIndex:", len(self.buckets))
        print("nOverflow:", overflowPageCount)
        plt.hist(pageHist, bins=10)
        plt.savefig(indexFile[:-2]+'png')

        f.close()