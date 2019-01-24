import os
import sys

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
        max_length = map(min, max_length, counts)
        line = file.readline()

    return (columns, max_length)


# start of main
if __name__ == "__main__":
    # Check command line arguments
    # May accept one command line argument of csv file name, default "500000 Records.csv"
    fileName = "500000 Records.csv"
    if len(sys.argv) > 2:
        print("Invalid number of arguments. May accept one argument of file name.")
    elif len(sys.argv) == 2:
        fileName = sys.argv[1]
    

