from ui.pfdview import *
from data.parameter import *
import math

class MainMenuView(Dialog):
    surfaceWidth = 300
    surfaceHeight = 200

    def __init__(self):
        Dialog.__init__(self,self.surfaceWidth,self.surfaceHeight)
        size = 40
        up = '\u2191'   # Unicode up arrow
        down = '\u2193' # Unicode down arrow
        xstart = 45
        xtop = 20
        xbottom = 110
        xinc = 30
        self.menuItem1 = Button(xstart, xtop, "1", "monospace", size)
        self.menuText1 = TextField(xstart+30, xtop, "TimeZone", "monospace", size)
        self.registerWidget(Widget(self.menuItem1,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        self.registerWidget(Widget(self.menuText1,self.getPhysicalXYOffsetOfSurface()),self.objectID)

    def registerMenuItem1ButtonRelease(self,method):
        self.menuItem1.registerButtonRelease(method)

    def draw(self):
        super().draw()

class MainMenuController:
    model = None
    view = None

    def __init__(self,view):
        self.view = view

    def menuItem1Callback(self):
        pass

    def registerMainMenuClosedCallback(self,method):
        self.mainMenuClosedCallback = method

    def okButtonCallback(self):
        self.view.unregisterDialog(self.view.objectID)
        self.mainMenuClosedCallback()

    def cancelButtonCallback(self):
        self.view.unregisterDialog(self.view.objectID)
        self.mainMenuClosedCallback()

    def launch(self):
        self.view.registerMenuItem1ButtonRelease(self.menuItem1Callback)
        self.view.registerOKButton(self.okButtonCallback)
        self.view.registerCancelButton(self.cancelButtonCallback)
        self.view.draw()

    def update(self):
        self.view.draw()

