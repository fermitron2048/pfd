import csv
import socket
import sys
from struct import *
import time

s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def hpaToInhg(value):
    return value * 0.0295299802

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
        # Convert hPa to InHg
        row[2] = round(hpaToInhg(row[2]),3)
        row[23] = round(hpaToInhg(row[23]),3)
        row[25] = round(hpaToInhg(row[25]),3)
        row1 = row[:20]
        print(row1)
        row2 = row[20:]
        print(row2)
        data1 = pack('IfffffffdddddiiiiiiI', *row1)
        s1.sendto(data1, ("127.0.0.1", 61532))
        data2 = pack('Ifffff', *row2)
        s2.sendto(data2, ("127.0.0.1", 61533))
        time.sleep(0.1)
