#!/bin/bash

# Define the directory to monitor
DIR=logs/
# Enter the directory
cd $DIR

# Run tail -f on the latest file that shows up in the directory
latest_file=$(ls -lrtha | tail -n 1 | awk '{print $9}')
echo "Monitoring $latest_file..."
tail -100 $latest_file
tail -f $latest_file

