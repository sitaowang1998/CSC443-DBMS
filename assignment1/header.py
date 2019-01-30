from helper import *

class DatabaseHeader():
    """
    DatabaseHeader contains the information of whole database by reading the database header, i.e. the first 100 bytes of the first page.
    """

    def __init__(self, db):
        """
        Create the header object with the binary file object.
        """
        db.seek(0)

        # Check the magic header string
        self.magic = map(ord, db.read(16))
        if self.magic != [0x53, 0x51, 0x4c, 0x69, 0x74, 0x65, 0x20, 0x66, 0x6f, 0x72, 0x6d, 0x61, 0x74, 0x20, 0x33, 0x00]:
            raise RuntimeError("Database magic header string does not match")
        
        self.page_size = read_big_endian(db, 2)
    
    def get_page_size(self):
        return self.page_size

# main for testing
if __name__ == "__main__":

    db = open("4096.db", 'rb')
    dheader = DatabaseHeader(db)