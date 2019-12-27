from ui.pfdview import *
from data.parameter import *
import math

class AltitudeCalibrationView(Dialog):
    newSLP = None
    surfaceWidth = 300
    surfaceHeight = 200

    def __init__(self):
        Dialog.__init__(self,self.surfaceWidth,self.surfaceHeight)
        size = 40
        up = '\u2191'   # Unicode up arrow
        down = '\u2193' # Unicode down arrow
        xstart = 95
        xtop = 20
        xbottom = 110
        xinc = 30
        self.button100Up = Button(xstart, xtop, up, "monospace", size)
        self.button100Down = Button(xstart, xbottom, down, "monospace", size)
        self.button10Up = Button(xstart + xinc, xtop, up, "monospace", size)
        self.button10Down = Button(xstart + xinc, xbottom, down, "monospace", size)
        self.button1Up = Button(xstart + xinc*2, xtop, up, "monospace", size)
        self.button1Down = Button(xstart + xinc*2, xbottom, down, "monospace", size)
        self.buttonP1Up = Button(xstart + xinc*4, xtop, up, "monospace", size)
        self.buttonP1Down = Button(xstart + xinc*4, xbottom, down, "monospace", size)
        self.registerWidget(Widget(self.button100Up,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.button100Down,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.button10Up,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.button10Down,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.button1Up,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.button1Down,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.buttonP1Up,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.buttonP1Down,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.slpTextField = TextField(60, 60, "", "monospace", 45)
        self.altitudeTextField = TextField(139, 169, "", "monospace", 25)
        self.registerWidget(Widget(self.slpTextField,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.altitudeTextField,self.getPhysicalXYOffsetOfSurface()),self.objectID)

    def register100UpButtonRelease(self,method):
        self.button100Up.registerButtonRelease(method)

    def register100DownButtonRelease(self,method):
        self.button100Down.registerButtonRelease(method)

    def register10UpButtonRelease(self,method):
        self.button10Up.registerButtonRelease(method)

    def register10DownButtonRelease(self,method):
        self.button10Down.registerButtonRelease(method)
        
    def register1UpButtonRelease(self,method):
        self.button1Up.registerButtonRelease(method)

    def register1DownButtonRelease(self,method):
        self.button1Down.registerButtonRelease(method)

    def registerP1UpButtonRelease(self,method):
        self.buttonP1Up.registerButtonRelease(method)

    def registerP1DownButtonRelease(self,method):
        self.buttonP1Down.registerButtonRelease(method)

    def draw(self):
        super().draw()

class AltitudeCalibrationController:
    model = None
    view = None

    def __init__(self,model,view):
        self.model = model
        self.view = view

    def button100UpCallback(self):
        self.model.updateSLP(100)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def button100DownCallback(self):
        self.model.updateSLP(-100)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def button10UpCallback(self):
        self.model.updateSLP(10)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def button10DownCallback(self):
        self.model.updateSLP(-10)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def button1UpCallback(self):
        self.model.updateSLP(1)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def button1DownCallback(self):
        self.model.updateSLP(-1)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def buttonP1UpCallback(self):
        self.model.updateSLP(0.1)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def buttonP1DownCallback(self):
        self.model.updateSLP(-0.1)
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))

    def registerBarosetClosedCallback(self,method):
        self.barosetClosedCallback = method

    def okButtonCallback(self):
        self.model.oap1.slp = self.model.baroset.slp
        self.model.oap2.slp = self.model.baroset.slp
        self.view.unregisterDialog(self.view.objectID)
        self.barosetClosedCallback()

    def cancelButtonCallback(self):
        self.view.unregisterDialog(self.view.objectID)
        self.barosetClosedCallback()

    def launch(self):
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))
        self.view.register100UpButtonRelease(self.button100UpCallback)
        self.view.register100DownButtonRelease(self.button100DownCallback)
        self.view.register10UpButtonRelease(self.button10UpCallback)
        self.view.register10DownButtonRelease(self.button10DownCallback)
        self.view.register1UpButtonRelease(self.button1UpCallback)
        self.view.register1DownButtonRelease(self.button1DownCallback)
        self.view.registerP1UpButtonRelease(self.buttonP1UpCallback)
        self.view.registerP1DownButtonRelease(self.buttonP1DownCallback)
        self.view.registerOKButton(self.okButtonCallback)
        self.view.registerCancelButton(self.cancelButtonCallback)
        self.view.draw()

    def update(self):
        values = np.array([self.model.oap1.value,self.model.oap2.value])
        self.model.addPressure(values.mean())
        self.view.slpTextField.updateText(str(round(self.model.currentSLP(),1)))
        self.view.altitudeTextField.updateText(str(round(self.model.currentAltitude(),1)))
        self.view.draw()

class AltitudeCalibrationModel:
    baroset = None   # For baroset dialog
    oap1 = None
    oap2 = None

    def __init__(self,oap1,oap2):
        self.baroset = Pressure(10,4.7)
        values = np.array([oap1.value,oap2.value])
        altitudes = np.array([oap1.elevation,oap2.elevation])
        self.baroset.appendAsHPa(values.mean())
        self.baroset.calibrateElevation(altitudes.mean())
        self.oap1 = oap1
        self.oap2 = oap2

    def addPressure(self,value):
        self.baroset.appendAsHPa(value)

    def updateSLP(self,amount):
        """ Adjust the current SLP by this amount """
        self.baroset.slp = self.baroset.slp + amount
    
    def currentSLP(self):
        return self.baroset.slp

    def currentAltitude(self):
        return self.baroset.elevation
