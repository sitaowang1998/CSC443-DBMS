import os
import sys
import sqlite3
import csv
import re

def find_max_length(fileName):
    """
    Find the max length of each column in a csv file.
    """
    with open(fileName, 'r') as f:
        reader = csv.reader(f)

        # Read the first line to get the number of columns
        columns = reader.next()
        max_length = [0] * len(columns)

        # Scan the rest of file to find the max length
        for row in reader:
            max_length = map(max, max_length, map(len, row))

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
        # EmpId has type INTEGER
        if name == "EmpID":
            attType = "INTEGER"
            if index:
                attType = attType + " PRIMARY KEY"

        schema = schema + name + " " + attType + ","

    schema = schema[:-1] + ")"

    # If need to create clustered index 
    if index and clustered:
        schema = schema + " WITHOUT ROWID"

    c.execute(schema)

    return c

def load_file(cursor, max_length, fileName):
    """
    Load the csv file into the databases.
    """

    with open(fileName, 'r') as f:
        reader = csv.reader(f)
        # Skip the first line
        reader.next()

        idSet = set()

        # Scan the file to insert to table
        for row in reader:
            empID = int(row[0])
            if empID not in idSet:
                idSet.add(empID)
                fixed_length = ['"' + row[i] + ' ' * (max_length[i] - len(row[i])) + '"' for i in range(len(row))]
                insert = "INSERT INTO Employee VALUES ("
                insert = insert +  str(empID) + ','  + ','.join(fixed_length[1:])
                insert = insert + ")"

                cursor.execute(insert)

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
    
    print("Loading 4kB without index")
    load_file(c1, max_length, fileName)
    print("Commiting 4kB without index")
    c1.connection.commit()
    print("Loading 16KB without index")
    load_file(c2, max_length, fileName)
    print("Commiting 16kB without index")
    c2.connection.commit()
    print("Loading 4kB with unclustered index")
    load_file(c3, max_length, fileName)
    print("Commiting 4kB with unclustered index")
    c3.connection.commit()
    print("Loading 4kB with clustered index")
    load_file(c4, max_length, fileName)
    print("Commiting 4kB with clustered index")
    c4.connection.commit()
    



