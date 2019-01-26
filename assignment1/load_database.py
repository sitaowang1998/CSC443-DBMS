import os
import sys
import sqlite3
import re

def find_max_length(fileName):
    """
    Find the max length of each column in a csv file.
    """
    file = open(fileName)

    # Read the first line to get the number of columns
    line = file.readline()
    columns = line.split(',')
    max_length = [0] * len(columns)

    # Scan the rest of file to find the max length
    line = file.readline()
    while line:
        counts = map(lambda item: len(item), line.split(','))
        max_length = map(max, max_length, counts)
        line = file.readline()

    file.close() 

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

        schema = schema + name + " " + attType + ","

    schema = schema[:-1] + ")"

    c.execute(schema)

    return c


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

    create_database(columns, max_length)


