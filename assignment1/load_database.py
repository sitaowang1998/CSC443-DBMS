import os
import sys






# start of main
if __name__ == "__main__":
    # check command line argument
    # may accept one command line argument of csv file name, default "500000 Records.csv"
    fileName = "500000 Records.csv"
    if len(sys.argv) > 2:
        print("Invalid number of arguments. May accept one argument of file name.")
    elif len(sys.argv) == 2:
        fileName = sys.argv[1]
    
    file = open(fileName)

