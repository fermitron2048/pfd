from ui.pfdview import *
from ui.panels import *

class PFDView(View):
    horizon = None
    speedTape = None
    altitudeTape = None
    vertSpeed = None
    bearing = None
    status = None
    leftPanel = None

    def __init__(self,simulation):
        super().__init__(simulation)
        self.horizon = Horizon()
        self.speedTape = SpeedTape()
        self.altitudeTape = AltitudeTape()
        self.vertSpeed = VertSpeed()
        self.bearing = Bearing()
        self.status = Status()
        self.leftPanel = LeftPanel()
        self.rightPanel = RightPanel()

    def registerBarosetOpenedCallback(self,method):
        self.leftPanel.registerBarosetOpenedCallback(method)

    def registerMainMenuOpenedCallback(self,method):
        self.rightPanel.registerMainMenuOpenedCallback(method)

    def draw(self):
        super().blankOut()
        self.horizon.draw()
        self.speedTape.draw()
        self.altitudeTape.draw()
        self.vertSpeed.draw()
        self.bearing.draw()
        self.status.draw()
        self.leftPanel.draw()
        self.rightPanel.draw()

    def setSpeed(self,speed):
        self.speedTape.speed = speed

    def setAltitude(self,altitude):
        self.altitudeTape.altitude = altitude

    def setSLP(self,slp):
        self.altitudeTape.slp = slp

    def setVertSpeed(self,vertspeed):
        self.vertSpeed.vertspeed = vertspeed

    def setBearing(self,bearing):
        self.bearing.bearing = bearing

    def setTemperature(self,temperature):
        self.status.temperature = temperature

    def setHumidity(self,humidity):
        self.status.humidity = humidity

    def setOAT(self,oat):
        self.status.oat = oat

    def setFPS(self,fps):
        self.leftPanel.fps = fps

    def setRxLight1(self,status):
        self.leftPanel.rxLight1 = status

    def setRxLight2(self,status):
        self.leftPanel.rxLight2 = status

    def setDate(self,date):
        self.rightPanel.dateString = date

    def setTime(self,time):
        self.rightPanel.timeString = time

        #print pygame.transform.get_smoothscale_backend()
        #subprocess.check_call(['echo', str(brightnesscount), '> /sys/class/backlight/rpi_backlight/brightness'])
        #with open('/sys/class/backlight/rpi_backlight/brightness', 'w') as f:
        #    f.write(str(int(brightnesscount)))
