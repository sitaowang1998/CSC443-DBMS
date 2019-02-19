
class Record:
    """
    Record class represents a record in the database file. The Record class is
    specialized for this assignment only, i.e. it hardcode the schema of the 
    record.
    """
    def __init__(self, data):
        self.firstName = data[:12].strip(bytearray.fromhex('00')).decode()
        self.lastName = data[12:26].strip(bytearray.fromhex('00')).decode()
        self.email = data[26:].strip(bytearray.fromhex('00')).decode()
    
    @staticmethod
    def getSize():
        """
        Return the size of the record, which is always 64
        """
        return 64
    
    def getField(self, index):
        """
        Return the field of the record based on the index.
        """
        if index == 0:
            return self.firstName
        elif index == 1:
            return self.lastName
        elif index == 2:
            return self.email
        else:
            raise IndexError