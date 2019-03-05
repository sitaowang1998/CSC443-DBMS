import struct
import hashlib
import os
import math

from hashing import HashHeader, HashPage, HashTable, md5Hash

class LinearHashBucket:
    """
    A hash bucket for linear hash table.
    """

    def __init__(self, hashHeader):
        self.hashHeader = hashHeader
        self.entries = []
        self.entryPerPage = int((hashHeader.pSize - 4) / hashHeader.entryStruct.size)
    
    def insert(self, key, pNum, offset):
        """
        Insert a record into the bucket.
        Return True if insertion leads to a new page, False otherwise.
        """
        self.entries.append(self.hashHeader.entryStruct.pack(key.encode(), pNum, offset))

        if len(self.entries) % self.entryPerPage == 0:
            return True
        
        return False

class LinearHashTable(HashTable):
    """
    A linear hash table.
    """

    def __init__(self, indexType, pSize, bNum, field):
        super().__init__(indexType, pSize, bNum, field)
        self.level = int(math.log(bNum) / math.log(2))
        self.buckets = [LinearHashBucket(self.hashHeader) for _ in range(bNum)]
        self.next = 0
    
    def insert(self, key, pNum, offset):
        index = md5Hash(key) % self.hashHeader.bNum

        if index < self.next:
            index = md5Hash(key) % (2 * self.hashHeader.bNum)
        
        if not self.buckets[index].insert(key, pNum, offset):
            return

        # Insertion leads to increase of new overflow page
        if self.next == self.hashHeader.bNum:
            # if all buckets are splited, create a new level
            self.next = 0
            self.level += 1
            self.hashHeader.bNum *= 2

        bucket = self.buckets[self.next]
        newBucket = LinearHashBucket(self.hashHeader)

        # Rehash all the elements
        for _ in range(len(bucket.entries)):
            entry = bucket.entries.pop(0)
            key, _, _ = self.hashHeader.entryStruct.unpack(entry)

            index = md5Hash(key.strip(bytes(1)).decode()) % (2 ** (self.level + 1))
            if index == self.next:
                bucket.entries.append(entry)
            elif index == self.next + self.hashHeader.bNum:
                newBucket.entries.append(entry)
            else:
                print(index, self.next, self.hashHeader.bNum)
                raise ValueError

        self.buckets.append(newBucket)
        self.next += 1
        if len(self.buckets) != self.hashHeader.bNum + self.next:
            raise IndexError
    

    def writeTable(self, indexFile):
        """
        Write the linear hash table into indexFile.
        """
        overflowCount = 0
        indexCount = 0
        pageHist = {}

        f = open(indexFile, 'wb')

        # Write the first page
        firstPage = self.hashHeader.pack()
        firstPage += struct.pack('>I', self.next)
        firstPage += bytes(self.hashHeader.pSize - len(firstPage))
        f.write(firstPage)

        # Write the dictionary pages with zeros
        dirStruct = struct.Struct('>I')
        pointerPerPage = (self.hashHeader.pSize - 4) // dirStruct.size
        numDirPage = len(self.buckets) // pointerPerPage
        if len(self.buckets) % pointerPerPage > 0:
            numDirPage += 1
        pNum = 1
        for i in range(numDirPage):
            if i < numDirPage - 1:
                dirPage = struct.pack('>I', pNum + 1)
            else:
                dirPage = struct.pack('>I', 0)
            dirPage += bytes(self.hashHeader.pSize - len(dirPage))
            f.write(dirPage)
            pNum += 1
        
        def seek_dir_bucket(bucketNumber):
            """
            Seek the file pointer to the given bucket.
            """
            pageNum = bucketNumber // pointerPerPage + 1
            offset = bucketNumber % pointerPerPage
            f.seek(pageNum * self.hashHeader.pSize + 4 + offset * dirStruct.size)

        entryPerPage = (self.hashHeader.pSize - 4) // self.hashHeader.entryStruct.size
        for i in range(len(self.buckets)):
            bucket = self.buckets[i]

            f.seek(0, os.SEEK_END)
            pNum = f.tell() // self.hashHeader.pSize

            if len(bucket.entries) == 0:
                seek_dir_bucket(i)
                f.write(dirStruct.pack(0))
                continue
            else:
                seek_dir_bucket(i)
                f.write(dirStruct.pack(pNum))

            indexCount += 1
            pageCount = 0

            # Write the buckets
            f.seek(0, os.SEEK_END)
            entryPage =[]
            for j in range(len(bucket.entries)):
                entryPage.append(bucket.entries[j])
                
                # If the entryPage is full, wirte the page
                if len(entryPage) == entryPerPage or j == len(bucket.entries) - 1:
                    if j == len(bucket.entries) - 1:
                        data = struct.pack('>I', 0)
                    else:
                        data = struct.pack('>I', pNum + 1)
                    
                    for entry in entryPage:
                        data += entry
                    
                    data += bytes(self.hashHeader.pSize - len(data))
                    f.write(data)
                    pageCount += 1

                    entryPage = []
                    pNum += 1

            overflowCount += pageCount - 1
            if pageCount in pageHist:
                pageHist[pageCount] += 1
            else:
                pageHist[pageCount] = 1

        f.close()

        print("nBucket:", len(self.buckets))
        print("nIndex:", indexCount)
        print("nOverflow:", overflowCount)
        # Print histogram
        values =  list(pageHist.keys())
        values.sort()
        pageMin, pageMax = values[0], values[-1]
        step = (pageMax - pageMin) // 10
        i = 0
        count = 0
        for value in values:
            if value <= pageMin + (i + 1) * step or i >= 9:
                count += pageHist[value]
            else:
                print(pageMin + i * step, 'to', str(pageMin + (i + 1) * step)+':',  count)
                count = 0
                i += 1
                count += pageHist[value]
        print(pageMin + i * step, 'to', str(pageMax)+':', count)

    def printTable(self):
        """
        Print the linear hash table. For debug use.
        """
        print("level:", self.level, "next:", self.next)
        print("bNum:", self.hashHeader.bNum, "pSize:", self.hashHeader.pSize)

        for i in range(len(self.buckets)):
            print()
            print("Bucket:", i)
            bucket = self.buckets[i]
            print("entry number:", len(bucket.entries))
            print("pointer: ", bucket)
            
            # for entry in bucket.entries:
            #     print("\t", self.hashHeader.entryStruct.unpack(entry))
        
        
        