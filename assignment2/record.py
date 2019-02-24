
class Record:
    """
    Record class represents a record in the database file. The Record class is
    specialized for this assignment only, i.e. it hardcode the schema of the 
    record.
    """
    def __init__(self, data):
        self.data = data
    
    @staticmethod
    def getSize():
        """
        Return the size of the record, which is always 64
        """
        return 64
    
    def __getitem__(self, index):
        """
        Return the field of the record based on the index.
        """
        if index == 0:
            return self.data[:12].strip(bytearray.fromhex('00')).decode()
        elif index == 1:
            return self.data[12:26].strip(bytearray.fromhex('00')).decode()
        elif index == 2:
            return self.data[26:].strip(bytearray.fromhex('00')).decode()
        else:
            raise IndexError
    
    def isEmtpy(self):
        """
        Return True if the record is empty, i.e. the three fields are all empty
        strings, False otherwise.
        """
        return self.data == bytearray(64)
