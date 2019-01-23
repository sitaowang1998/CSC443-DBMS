#!/bin/bash

# script may accept one command line argument as the name of csv file
if test "$#" -gt 1; then
	echo "Illegal number of parameters"
elif test "$#" -eq 1; then
	filename=$1
else
	filename="500000 Records.csv"
fi


