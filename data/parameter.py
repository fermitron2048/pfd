import collections
import time
import numpy as np
import math
import statistics
from datetime import tzinfo, timedelta, datetime

# Perform linear regression on the values in the x and y lists
def linReg(x, y):
    numpoints = np.size(x) 
    xmean, ymean = np.mean(x), np.mean(y) 
    xyss = np.sum(y * x) - numpoints * ymean * xmean 
    xxss = np.sum(x * x) - numpoints * xmean * xmean 
    m = xyss / xxss
    b = ymean - m * xmean
    return(m, b) 

class Parameter(object):
    """ Base class for generic parameter types """
    values = None
    lastUpdate = 0 # Time of last update (in seconds since epoch)
    
    # Specify how many values to include in the moving average 
    def __init__(self,average):
        """ Specify the number of values to use for the moving averaqe """
        self.values = collections.deque('', average)
        
    def __append(self,value):
        self.values.append(value)
        self.lastUpdate = time.time()
        
    @property
    def value(self):
        if len(self.values) == 0:
            return 0
        else:
            return sum(self.values) / len(self.values)

    @value.setter
    def value(self,value):
        """ Add a new value """
        if math.isnan(value):
            return
        self.__append(value)
    
    def latestValue(self):
        """ Returns the most recent value added """
        if len(self.values) > 0:
            return self.values[-1]
        else:
            return 0

class Pressure(Parameter):
    """ Class for instantiating atmospheric pressure values and performing common calculations """
    elevcomp = 0
    heightAboveGround = 0
    __vertspeed = None
    __altitude = None
    calibrated = False
    calibratedElevation = -9999

    def __init__(self,average,height):
        """ Specify the number of values to use for the moving averaqe, and the height of the sensor above ground """
        super().__init__(average)
        self.heightAboveGround = height
        self.__altitude = collections.deque('', average)
        self.__vertspeed = Parameter(10)

    def __calculateVerticalSpeed(self):
        if len(self.__altitude) < 10:
            return
        m, b = linReg(np.array(range(10)),np.array(list(self.__altitude))) # TODO: Find a way to optimize this
        self.__vertspeed.value = 60 * len(self.__altitude) * m

    def __calculateAltitude(self):
        if self.elevcomp == 0:
            return
        self.__altitude.append(44330.0 * (1.0 - (self.value / self.elevcomp) ** 0.1903) * 3.28084)

    def appendAsInHg(self,value):
        """ Add pressure value in InHg """
        hPa = value * 3386.38866666667 / 100.0
        self.appendAsHPa(hPa)

    # Default units are hPa
    def appendAsHPa(self,value):
        """ Add pressure value in hPa """
        if value != 0:
            self.values.append(value)
            self.lastUpdate = time.time()
            self.__calculateAltitude()
            self.__calculateVerticalSpeed()
            if self.calibrated == False:
                self.calibrateElevation(self.calibratedElevation)

    @property
    def value(self):
        """ Return average pressure value as hPa """
        return super().value
        
    @value.setter
    def value(self,value):
        """ Add pressure value in InHg """
        self.appendAsInHg(value)
        
    @property
    def slp(self):
        """ Returns Sea Level Pressure based on calibration """
        return self.elevcomp

    @slp.setter
    def slp(self,slp):
        self.elevcomp = slp
        
    def calibrateElevation(self,elevation):
        """ Calibrates Sea Level Pressure based on the current elevation (ground level) """
        if len(self.values) == self.values.maxlen:
            self.elevcomp = self.value / ((1.0 - ((elevation + self.heightAboveGround) * 0.3048 / 44330.0)) ** 5.255)
            self.calibrated = True
        else:
            self.calibratedElevation = elevation

    # Returns elevation at ground-level
    @property
    def elevation(self):
        """ Returns current elevation (height of ground above MSL) """
        return self.altitude - self.heightAboveGround

    @property
    def altitude(self):
        """ Returns current altitude (elevation plus height of sensor above ground) """
        if self.__altitude:
            return sum(self.__altitude) / len(self.__altitude)
        else:
            return -9999
    
    @property
    def verticalspeed(self):
        """ Returns current vertical speed (rate of increase / decrease in altitude) """
        return self.__vertspeed.value
    
    @verticalspeed.setter
    def verticalspeed(self,value):
        self.__vertspeed.append(value)

class Heading(Parameter):
    __GPSBearing = None
    __XValue = None
    __heading = 0
    __offset = 0
    speed = 0
    
    def __init__(self,average):
        super().__init__(average)
        self.__GPSBearing = collections.deque('', 50)
        self.__XValue = collections.deque('', 50)
    
    def addGPSBearing(self,value):
        self.__GPSBearing.append(value)
        self.__calculateOffset()

    def addXValue(self,value):
        """ X value is the azimuth angle from the accelerometer """
        self.__XValue.append(value)
        self.updateValue()
    
    def __calculateOffset(self):
        """ Calculates a new offset between GPS bearing and accelerometer bearing when accuracy is high """
        #if len(self.__XValue) > 0:
        #    print("GPSBearing: "+str(round(self.__GPSBearing[-1]))+", heading: "+str(round(self.value))+
        #          ", x: "+str(round(self.__XValue[-1]))+", stdev: "+str(round(np.std(self.__GPSBearing),5))+
        #          ", offset: "+str(self.__offset))
        if len(self.__GPSBearing) == self.__GPSBearing.maxlen and np.std(self.__GPSBearing) < 0.2 and self.speed > 7:
            self.__offset = (np.mean(self.__GPSBearing) + 360 - np.mean(self.__XValue)) % 360
            #print("new offset: "+str(self.__offset)) 

    def calibrationOffset(self, offset):
        self.__offset = offset

    def updateValue(self):
        """ Updates the parameter value when a new value from the accelerometer is added """
        if len(self.__XValue) > 0:
            # TODO: Should be calling the base __append method
            self.values.append((self.__XValue[-1] + self.__offset) % 360)
            self.lastUpdate = time.time()

    @property
    def value(self):
        if len(self.values) < 2 or statistics.stdev(self.values) < 10:
            return super().value
        else:
            v = np.array(self.values)
            return np.mean(np.concatenate([v[v>180],v[v <= 180] + 360])) % 360
 
    @property
    def offset(self):
        return self.__offset

class Time(Parameter):
    msOffset = 0.500
    hourOffset = -8

    def addTime(self,year,month,day,hour,minute,second,milliseconds):
        delta = datetime.now() - datetime(2000+int(year),int(month),int(day),int(hour),int(minute),int(second),int(milliseconds)*1000)
        self.value = delta.total_seconds()
    
    def date(self):
        """ Returns date string """
        if len(self.values) == 0:
            return "--/--/--"
        else:
            now = datetime.now() - timedelta(seconds=self.value) + timedelta(hours=self.hourOffset) + timedelta(seconds=self.msOffset)
            return now.strftime("%m/%d/%Y")

    def time(self):
        """ Returns time string """
        if len(self.values) == 0:
            return "--:--:--"
        else:
            now = datetime.now() - timedelta(seconds=self.value) + timedelta(hours=self.hourOffset) + timedelta(seconds=self.msOffset)
            return now.strftime("%H:%M:%S")
