import sys
import math
from struct import *

# Open output file
outfile = open(sys.argv[1]+'.csv', 'wt')

# Read sensor data file and write csv file 
with open(sys.argv[1], mode='rb') as infile:
    bytes = infile.read(124)
    while bytes != "":
        record = unpack('IfffffffdddddiiiiiiIIfffff', bytes)
        print(record)
        sequence1, temperature, pressure, humidity, x, y, z, light, lat, lon, gpsAltitude, gpsSpeed, gpsBearing = record[:13]
        year, month, day, hour, minute, second, milliseconds, sequence2, oat, barotemp1, oap1, barotemp2, oap2 = record[13:]
        outfile.write(str(sequence1)+","+str(temperature)+","+str(pressure)+","+str(humidity)+","+str(x)+","+str(y)+","+str(z)+","+str(light)+","+ 
                      str(lat)+","+str(lon)+","+str(gpsAltitude)+","+str(gpsSpeed)+","+str(gpsBearing)+","+str(year)+","+
                      str(month)+","+str(day)+","+str(hour)+","+str(minute)+","+str(second)+","+str(milliseconds)+","+str(sequence2)+","+
                      str(oat)+","+str(barotemp1)+","+str(oap1)+","+str(barotemp2)+","+str(oap2)+"\n")
        bytes = infile.read(124)
    infile.close()
