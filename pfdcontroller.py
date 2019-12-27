import pygame
import pygame.gfxdraw
from pygame.locals import *
from time import sleep
from ui.pfdview import *
from ui.panels import *
import numpy as np
from ui.dialogs.baroset import *
from ui.dialogs.mainmenu import *

class Controller:
    activeControllers = []
    done = False
    speedcount=30
    altitudecount=-70
    brightnesscount=100
    vertspeedcount=0
    bearingcount=0
    model = None
    view = None
    simulation = False
    timeLastDrawn = 0   # Seconds since screen was last drawn
    fps = 0             # Current frames per second

    def __init__(self, model, view, simulation):
        Controller.model = model
        Controller.view = view
        Controller.simulation = simulation
        self.clock = pygame.time.Clock()
        #self.view.registerButtonPressFunction(self.exitButtonPressed)
        self.view.registerBarosetOpenedCallback(self.barosetOpenedCallback)
        self.view.registerMainMenuOpenedCallback(self.mainMenuOpenedCallback)
        self.timeLastDrawn = time.time()

    # n = Original value
    # x = Original value's range min
    # y = Original value's range max
    # a = New value's range min
    # b = New value's range max
    def scaleRange(self, n, x, y, a, b):
        if n < x:
            n = x
        if n > y:
            n = y
        return (((n - x) * (b - a)) / (y - x)) + a

    def roundTo(self,x,base=5):
        return int(base * round(float(x) / base))

    def displayPFD(self):
        speed = self.model.gpsSpeed.value * 77.51 / 67.6 # Adjust for GPS vs actual speed difference
        self.view.setSpeed(speed)
        #altitudes = np.array([self.model.cabinPressure.elevation,self.model.oap1.elevation,self.model.oap2.elevation])
        altitudes = np.array([self.model.oap1.elevation,self.model.oap2.elevation])
        #altitudes = np.array([self.model.cabinPressure.elevation]) # TODO: Using only one baro for now (fix later)
        altitudes = altitudes[altitudes>=-9999]
        #slps = np.array([self.model.cabinPressure.slp,self.model.oap1.slp,self.model.oap2.slp])
        slps = np.array([self.model.oap1.slp,self.model.oap2.slp])
        #slps = np.array([self.model.cabinPressure.slp]) # TODO: Using only one baro for now (fix later)
        slps = slps[slps!=0]
        if len(altitudes) > 0 and len(slps) > 0:
            self.view.setAltitude(altitudes.mean())
            self.view.setSLP(slps.mean())
        else:
            self.view.setAltitude(0)
            self.view.setSLP(0)
        #verticalspeeds = np.array([self.model.cabinPressure.verticalspeed,self.model.oap1.verticalspeed,self.model.oap2.verticalspeed])
        verticalspeeds = np.array([self.model.oap1.verticalspeed,self.model.oap2.verticalspeed])
        #verticalspeeds = np.array([self.model.cabinPressure.verticalspeed]) # TODO: Using only one baro for now (fix later)
        verticalspeeds = verticalspeeds[verticalspeeds!=0]
        if len(verticalspeeds) > 0:
            self.view.setVertSpeed(self.roundTo(verticalspeeds.mean(),50))
        else:
            self.view.setVertSpeed(0)
        self.view.setBearing(self.model.heading.value)
        self.view.setTemperature(self.model.temperature.value)
        self.view.setHumidity(self.model.humidity.value)
        self.view.setOAT(self.model.oat.value)
        self.view.setFPS(self.fps)
        self.view.setRxLight1(self.model.rxLight1)
        self.view.setRxLight2(self.model.rxLight2)
        self.view.setDate(self.model.currentTime.date())
        self.view.setTime(self.model.currentTime.time())
        self.view.draw()

    def barosetOpenedCallback(self):
        model = AltitudeCalibrationModel(self.model.oap1,self.model.oap2)
        view = AltitudeCalibrationView()
        controller = AltitudeCalibrationController(model,view)
        controller.registerBarosetClosedCallback(self.barosetClosedCallback)
        controller.launch()
        self.activeControllers.append(controller)

    def barosetClosedCallback(self):
        if len(self.activeControllers) > 0:
            del self.activeControllers[-1]

    def mainMenuOpenedCallback(self):
        view = MainMenuView()
        controller = MainMenuController(view)
        controller.registerMainMenuClosedCallback(self.mainMenuClosedCallback)
        controller.launch()
        self.activeControllers.append(controller)

    def mainMenuClosedCallback(self):
        if len(self.activeControllers) > 0:
            del self.activeControllers[-1]

    def displayActiveViews(self):
        # Loop through each view class on PFD and display them
        while not self.done:
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                            self.done = True
            self.displayPFD()
            if len(self.activeControllers) > 0:
                self.activeControllers[-1].update()
            pygame.display.flip()
            self.clock.tick(60)
            now = time.time()
            self.fps = 1 / (now - self.timeLastDrawn)
            self.timeLastDrawn = now
            sleep(0.0001)

    def setScreenBrightness(self):
        while True:
            if not self.simulation:
                with open('/sys/devices/platform/rpi_backlight/backlight/rpi_backlight/brightness', 'w') as brightness:
                    if time.time() - self.model.light.lastUpdate < 60:
                        brightness.write(str(int(self.scaleRange(self.model.light.value, 0, 500, 14, 200))))
                    else:
                        brightness.write("50")
                    brightness.write("\n")
                brightness.close()
            sleep(0.1)

    def exitButtonPressed(self):
        self.done = True

    def setSimulation(self,simulation):
        self.simulation = simulation
