from helper import Reader

class DHeader:
    """
    DatabaseHeader contains the information of whole database by reading the database header, i.e. the first 100 bytes of the first page.
    """

    def __init__(self, db):
        """
        Create the header object with the binary file object.
        """
        db.seek(0)

        # Check the magic header string
        if db.read(16) != bytes.fromhex("53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00"):
            raise RuntimeError("Database magic header string does not match")
        
        self.page_size = int.from_bytes(db.read(2), byteorder='big', signed=False)
    
    def get_page_size(self):
        return self.page_size

# main for testing
if __name__ == "__main__":

    db = open("4096.db", 'rb')
    dheader = DHeader(db)
    print(dheader.get_page_size())
    db.close()