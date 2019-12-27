import socket
from datetime import datetime
from time import sleep
from data.parameter import *
import json
from struct import *
import os

class Model:
    # Parameters from the various buses
    sequence1 = 0
    sequence2 = 0
    temperature = Parameter(10)
    humidity = Parameter(10)
    gpsSpeed = Parameter(5)
    gpsAltitude = Parameter(1)
    gpsBearing = Parameter(1)
    obdSpeed = Parameter(1)
    light = Parameter(10)
    cabinPressure = Pressure(10,4.7)
    oat = Parameter(10)         # Outside Air Temperature
    oap1 = Pressure(10,3)       # Outside Air Pressure (sensor 1)
    oap2 = Pressure(10,3)       # Outside Air Pressure (sensor 2)
    barotemp1 = Parameter(10)   # Temperature at OAP1
    barotemp2 = Parameter(10)   # Temperature at OAP2
    x = Parameter(1)
    y = Parameter(1)
    z = Parameter(1)
    lat = Parameter(1)
    lon = Parameter(1)
    heading = Heading(5)
    simulation = False
    stateFileLoaded = False
    year = Parameter(1)
    month = Parameter(1)
    day = Parameter(1)
    hour = Parameter(1)
    minute = Parameter(1)
    second = Parameter(1)
    milliseconds = Parameter(1)
    currentTime = Time(10)
    __rxLight1 = time.time()
    __rxLight2 = time.time()

    def __init__(self,simulation):
        Model.simulation = simulation

    # Given the current known altitude in feet and relative pressure in inHg, return MSL pressure in hPa
    def altitude2mslpressure(self, altitude, relpressure):
        hPa = relpressure * 3386.38866666667 / 100.0
        return hPa / ((1.0 - (altitude * 0.3048 / 44330.0)) ** 5.255)

    def writeSensorData(self):
        if self.simulation:
            return
        sensordata = None
        now = datetime.now()
        sensorfilename = "/home/pi/data/sensordata"+now.strftime("%Y%m%d%H%M%S")+".bin"
        sensordata = open(sensorfilename,"wb")

        while True:
            sensordata.write(pack('I',self.sequence1))
            sensordata.write(pack('f',self.temperature.latestValue()))
            sensordata.write(pack('f',self.cabinPressure.latestValue()))
            sensordata.write(pack('f',self.humidity.latestValue()))
            sensordata.write(pack('f',self.x.latestValue()))
            sensordata.write(pack('f',self.y.latestValue()))
            sensordata.write(pack('f',self.z.latestValue()))
            sensordata.write(pack('f',self.light.latestValue()))
            sensordata.write(pack('d',self.lat.latestValue()))
            sensordata.write(pack('d',self.lon.latestValue()))
            sensordata.write(pack('d',self.gpsAltitude.latestValue()))
            sensordata.write(pack('d',self.gpsSpeed.latestValue()))
            sensordata.write(pack('d',self.gpsBearing.latestValue()))
            sensordata.write(pack('i',self.year.latestValue()))
            sensordata.write(pack('i',self.month.latestValue()))
            sensordata.write(pack('i',self.day.latestValue()))
            sensordata.write(pack('i',self.hour.latestValue()))
            sensordata.write(pack('i',self.minute.latestValue()))
            sensordata.write(pack('i',self.second.latestValue()))
            sensordata.write(pack('I',self.milliseconds.latestValue()))
            sensordata.write(pack('I',self.sequence2))
            sensordata.write(pack('f',self.oat.latestValue()))
            sensordata.write(pack('f',self.barotemp1.latestValue()))
            sensordata.write(pack('f',self.oap1.latestValue()))
            sensordata.write(pack('f',self.barotemp2.latestValue()))
            sensordata.write(pack('f',self.oap2.latestValue()))
            altitudes = np.array([self.oap1.elevation,self.oap2.elevation])
            sensordata.write(pack('f',altitudes.mean()))
            slps = np.array([self.oap1.slp,self.oap2.slp])
            sensordata.write(pack('f',slps.mean()))
            verticalspeeds = np.array([self.oap1.verticalspeed,self.oap2.verticalspeed])
            sensordata.write(pack('f',verticalspeeds.mean()))
            sensordata.write(pack('f',self.heading.value))
            sleep(0.1)

    def writeStateFile(self):
        start = time.time()
        if self.simulation:
            lastStateFilename = "laststate.json"
        else:
            lastStateFilename = "/home/pi/jeep/laststate.json"

        # Wait for state file to be read
        while not self.stateFileLoaded and not self.cabinPressure.value:
            sleep(0.01)

        # Write state file periodically
        while True:
            if time.time() - start >= 5:
                with open(lastStateFilename, 'w') as lastStateFile:
                    json.dump({ "lastelev": self.cabinPressure.elevation, "lastheading":self.heading.value }, lastStateFile)
                    lastStateFile.write("\n")
                    lastStateFile.flush()
                    os.fsync(lastStateFile)
                    lastStateFile.close()
                start = time.time()
            sleep(0.01)

    def readMainSensorPack(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", 61532))

        # Load calibration points
        config = ""
        configfilename = ""
        lastStateFilename = ""
        if self.simulation:
            configfilename = "jeepconfig.json"
            lastStateFilename = "laststate.json"
        else:
            configfilename = "/home/pi/jeep/jeepconfig.json"
            lastStateFilename = "/home/pi/jeep/laststate.json"
        with open(configfilename) as configfile:
            config = json.load(configfile)

        # Load last elevation
        with open(lastStateFilename) as lastStateFile:
            state = json.load(lastStateFile)
            print("Last elevation: "+str(state['lastelev']))
            self.cabinPressure.calibrateElevation(state['lastelev'])
            self.oap1.calibrateElevation(state['lastelev'])
            self.oap2.calibrateElevation(state['lastelev'])
            print("Heading offset: "+str(state['lastheading']))
            self.heading.calibrationOffset(state['lastheading'])
            lastStateFile.close()
        self.stateFileLoaded = True

        while True:
            data, addr = s.recvfrom(100)
            self.__rxLight1 = time.time()
            fields = unpack('IfffffffdddddiiiiiiI', data)
            self.year.value, self.month.value, self.day.value = fields[13:16]
            self.hour.value, self.minute.value, self.second.value, self.milliseconds.value = fields[16:]
            self.currentTime.addTime(self.year.value, self.month.value, self.day.value, 
                                     self.hour.value, self.minute.value, self.second.value, self.milliseconds.value)
            self.sequence1, self.temperature.value, self.cabinPressure.value, self.humidity.value, self.x.value, self.y.value, self.z.value = fields[:7]
            self.light.value, self.lat.value, self.lon.value, self.gpsAltitude.value, self.gpsSpeed.value, self.gpsBearing.value = fields[7:13]
            self.heading.addGPSBearing(self.gpsBearing.value)
            self.heading.addXValue(self.x.value)
            self.heading.speed = self.gpsSpeed.value
            #print "received message:", fields

            # Calibrate elevation
            for e in config['calibrationpoints']:
                if abs(e['latitude'] - self.lat.value) <= e['variance'] and abs(e['longitude'] - self.lon.value) <= e['variance']:
                    self.cabinPressure.calibrateElevation(e['elevation'])
                    self.oap1.calibrateElevation(e['elevation'])
                    self.oap2.calibrateElevation(e['elevation'])
                    print("Adjusted SLP pressure to "+str(self.cabinPressure.slp)+" at "+str(e['elevation'])+"ft elevation")

    def readOATSensorPack(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", 61533))

        while True:
            data, addr = s.recvfrom(24)
            self.__rxLight2 = time.time()
            fields = unpack('Ifffff', data)
            self.sequence2, self.oat.value, self.barotemp1.value, self.oap1.value, self.barotemp2.value, self.oap2.value = fields
            #print "received message:", fields

    @property
    def rxLight1(self):
        if time.time() - self.__rxLight1 < 0.15:
            return True
        else:
            return False

    @property
    def rxLight2(self):
        if time.time() - self.__rxLight2 < 0.15:
            return True
        else:
            return False

