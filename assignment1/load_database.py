import os
import sys
import sqlite3
import re

def find_max_length(fileName):
    """
    Find the max length of each column in a csv file.
    """
    f = open(fileName)

    # Read the first line to get the number of columns
    line = f.readline()
    columns = line.split(',')
    max_length = [0] * len(columns)

    # Scan the rest of file to find the max length
    line = f.readline()
    while line:
        counts = map(lambda item: len(item), line.strip('\r\n').split(','))
        max_length = map(max, max_length, counts)
        line = f.readline()

    f.close() 

    return (columns, max_length)


def create_database(columns, max_length, page_size=4096, scheme="Employee", index=False, clustered=False):
    """
    Create a database with columns and max_length and set the schema.
    If index is true, create index on the first cloumn, which should be "Emp Id".
    Return the cursor.
    """
    
    dbName = str(page_size)
    if index:
        dbName = ("" if clustered else "un") + "clustered"
    dbName = dbName + ".db"

    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    # Set the page size
    c.execute("PRAGMA page_size = " + str(page_size))

    # Drop the table if exists
    c.execute("DROP TABLE IF EXISTS Employee")

    # Create the schema
    schema = "CREATE TABLE Employee ("

    regex = re.compile('[^a-zA-Z]')
    for i in range(len(columns)):
        column = columns[i]
        length = max_length[i]
        name = regex.sub("", column)

        attType = "CHAR(" + str(length)+")"
        # EmpId has INT
        if name == "EmpID":
            attType = "INT"
            if index:
                attType = attType + " PRIMARY KEY"

        schema = schema + name + " " + attType + ","

    schema = schema[:-1] + ")"

    # If need to create clustered index 
    if index and clustered:
        schema = schema + " WITHOUT ROWID"

    c.execute(schema)

    # Create index explicitly
    if index:
        c.execute("CREATE INDEX empid_index ON Employee(EmpID)")

    return c

def load_file(cursors, max_length, fileName):
    """
    Load the csv file into the databases.
    """

    f = open(fileName)
    # Skip the first line
    line = f.readline()

    # Scan the file to insert to table
    line = f.readline()
    while line:
        words = line.strip('\r\n').split(',')
        empID = int(words[0])
        fixed_length = ['"' + words[i] + ' ' * (max_length[i] - len(words[i])) + '"' for i in range(len(words))]
        insert = "INSERT INTO Employee VALUES ("
        insert = insert +  str(empID) + ','  + ','.join(fixed_length[1:])
        insert = insert + ")"

        for c in cursors:
            # Check if the empID is already in table
            c.execute("SELECT * FROM Employee WHERE EmpID = ?", (empID,))
            
            # Insert if empID not it table
            if (len(c.fetchall()) == 0):
                c.execute(insert)

        line = f.readline()

    f.close()

# start of main
if __name__ == "__main__":
    # Check command line arguments
    # May accept one command line argument of csv file name, default "500000 Records.csv"
    fileName = "500000 Records.csv"
    if len(sys.argv) > 2:
        print("Invalid number of arguments. May accept one argument of file name.")
    elif len(sys.argv) == 2:
        fileName = sys.argv[1]
    
    (columns, max_length) = find_max_length(fileName)

    # 4KB without index
    c1 = create_database(columns, max_length)
    # 16KB without index
    c2 = create_database(columns, max_length, page_size=16384)
    # 4KB with unclustered index
    c3 = create_database(columns, max_length, index=True)
    # 4KB with clustered index
    c4 = create_database(columns, max_length, index=True, clustered=True)
    
    load_file([c1, c2, c3, c4], max_length, fileName)



