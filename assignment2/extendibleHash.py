import struct
import hashlib
import os
import math
import matplotlib.pyplot as plt

from hashing import HashHeader, HashPage, HashTable, md5Hash


class ExtendibleHashBucket:
    """
    A hash bucket for extendible hash table.
    """

    def __init__(self, hashHeader):
        self.hashHeader = hashHeader
        self.depth = int(math.log(hashHeader.bNum) / math.log(2))
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

class ExtendibleHashTable(HashTable):
    """
    An extendible hash table.
    """

    def __init__(self, indexType, pSize, bNum, field):
        super().__init__(indexType, pSize, bNum, field)
        self.depth = int(math.log(bNum) / math.log(2))
        self.buckets = [ExtendibleHashBucket(self.hashHeader) for _ in range(bNum)]
    
    def insert(self, key, pNum, offset):
        index = md5Hash(key) % self.hashHeader.bNum
        
        if not self.buckets[index].insert(key, pNum, offset):
            return
        
        # Insertion leads to creation of new page
        bucket = self.buckets[index]
        
        if bucket.depth == self.depth:
            # local depth equals to global depth, need to double the buckets
            self.buckets = self.buckets * 2
            self.depth = self.depth + 1
            self.hashHeader.bNum *= 2
        
        # Split the bucket
        bucket.depth += 1
        index = index % (2 ** (bucket.depth - 1))
        newIndex = index + 2 ** (bucket.depth - 1)
        newBucket = ExtendibleHashBucket(self.hashHeader)
        newBucket.depth = bucket.depth

        # Rehash the item
        modular = 2 ** bucket.depth
        for _ in range(len(bucket.entries)):
            entry = bucket.entries.pop(0)
            key, _, _ = self.hashHeader.entryStruct.unpack(entry)
            hashIndex = md5Hash(key.strip(bytes(1)).decode()) % modular
            if hashIndex == index:
                bucket.entries.append(entry)
            elif hashIndex == newIndex:
                newBucket.entries.append(entry)
            else:
                print(index, hashIndex)
                print(modular)
                raise ValueError
            
        for i in range(self.hashHeader.bNum // modular):
            self.buckets[i * modular + index] = bucket
            self.buckets[i * modular + newIndex] = newBucket

    def writeTable(self, indexFile):
        """
        Write the extendible hash table into file with name indexFile.
        """

        overflowCount = 0
        indexCount = 0
        pageHist = []

        f = open(indexFile, 'wb')

        # Write the header
        firstPage = self.hashHeader.pack()
        firstPage += struct.pack('>I', self.depth)
        firstPage += bytes(self.hashHeader.pSize - len(firstPage))
        f.write(firstPage)

        # Write the dictionary pages with zeros
        dirStruct = struct.Struct('>II')
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
        bucketPageDict = {}
        for i in range(len(self.buckets)):
            bucket = self.buckets[i]
            
            f.seek(0, os.SEEK_END)
            pNum = f.tell() // self.hashHeader.pSize

            if len(bucket.entries) == 0:
                # no entries in the bucket, just write the depth
                seek_dir_bucket(i)
                f.write(struct.pack('>II', 0, bucket.depth))
            elif bucket in bucketPageDict:
                # bucket already written, just write the pNum and depth
                pNum = bucketPageDict[bucket]
                seek_dir_bucket(i)
                f.write(struct.pack('>II', pNum, bucket.depth))
            else:
                # write the directory
                seek_dir_bucket(i)
                f.write(struct.pack('>II', pNum, bucket.depth))

                bucketPageDict[bucket] = pNum
                indexCount += 1
                pageCount = 0

                # write the bucket
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
                pageHist.append(pageCount)

        f.close()

        print("nBucket:", len(self.buckets))
        print("nIndex:", indexCount)
        print("nOverflow:", overflowCount)
        plt.hist(pageHist, bins=10)
        plt.savefig(indexFile[:-2]+'png')
        plt.close('all')

    
    def printTable(self):
        """
        Print the extendible hash table. For debug use.
        """
        print("global depth: ", self.depth)
        print("bNum:", self.hashHeader.bNum, "pSize:", self.hashHeader.pSize)

        for i in range(len(self.buckets)):
            print()
            print("Bucket ", i)
            bucket = self.buckets[i]
            print("local depth:", bucket.depth, "entry number:", len(bucket.entries))
            print("pointer: ", bucket)
            
            for entry in bucket.entries:
                print("\t", self.hashHeader.entryStruct.unpack(entry))