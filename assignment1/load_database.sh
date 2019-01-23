#!/bin/bash

# script may accept one command line argument as the name of csv file
if test "$#" -gt 1; then
	echo "Illegal number of parameters"
	exit 1
elif test "$#" -eq 1; then
	filename="$1"
else
	filename="500000 Records.csv"
fi

# find the max length for each column
# assume that empID is the first column
# read the first line to check the number of columns
read -r line < "$filename"

