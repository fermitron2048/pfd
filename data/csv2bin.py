import csv
import socket
import sys
from struct import *
import time

if len(sys.argv) < 3:
    print("Usage: csv2bin.py <csvfile> <binfile>")
    exit(1)

outfile = open(sys.argv[2], mode='wb')

with open(sys.argv[1]) as infile:
    reader = csv.reader(infile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        row[0] = int(row[0])                # Convert sequence number
        for i in range(1,13):
            row[i] = round(float(row[i]),6) # Convert acclerometer, light, gps, etc.
        for i in range(13,20):
            row[i] = int(row[i])            # Convert time
        row[20] = int(row[20])              # Convert sequence number
        for i in range(21,26):
            row[i] = round(float(row[i]),5) # Convert oat/oap
        row1 = row[:20]
        print(row1)
        row2 = row[20:]
        print(row2)
        data1 = pack('IfffffffdddddiiiiiiI', *row1)
        data2 = pack('Ifffff', *row2)
        outfile.write(data1)
        outfile.write(data2)
outfile.flush()
outfile.close()
