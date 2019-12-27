from abc import ABC, abstractmethod
from time import sleep
import pygame
import pygame.gfxdraw
from pygame.locals import *

# Handling touch events on the official RPi 7" Touchscreen display
# Download python package from: https://github.com/pimoroni/python-multitouch
# cd library
# sudo python3 setup.py install
try:
    from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
except ImportError:
    print("For touch events on the RPi 7\" display, see: https://github.com/pimoroni/python-multitouch")

class View:
    # Class variables
    BLUE = (16, 140, 198)
    #BLUE = (0, 128, 255)
    #BLUE = (125, 152, 225)
    ORANGE = (148,74,24)
    ORANGEAA = (67,36,20)
    WHITE = (247,247,214)
    BLACK = (0,0,0)
    GRAY = (99,90,90)
    GREEN = (16,247,66)
    screen = None
    done = False
    is_blue = True
    x = 30
    y = 30
    Xmax = 800
    Ymax = 480
    simulation = False
    dialogWidgets = {}  # Dictionary that contain arrays of widgets for each dialog
    modality = []       # Keep track of how dialogs are nested
    panelWidgets = []
    ts = None

    def moveEvent(self,x,y):
        pygame.gfxdraw.aacircle(self.screen, x, y, 2, self.WHITE)
        pygame.gfxdraw.filled_circle(self.screen, x, y, 2, self.WHITE)

    def releasedEvent(self,x,y):
        if len(self.modality) > 0:
            # Only take touch events for the current (modal) dialog
            id = self.modality[-1]
            for i in self.dialogWidgets[id]:
                if isinstance(i.object,Button):
                    if i.isAt(x,y):
                        i.object.buttonReleaseHandler()
        else:
            # Take touch events for buttons on the panels
            for i in self.panelWidgets:
                if isinstance(i.object,Button):
                    if i.isAt(x,y):
                        i.object.buttonReleaseHandler()

    # Handler for FT5406 touchscreen
    def touch_handler(self, event, touch):
        x = touch.x
        y = touch.y
        if event == TS_PRESS:
            pass
        if event == TS_RELEASE:
            self.releasedEvent(x,y)
        if event == TS_MOVE:
            self.moveEvent(x,y)

    def __init__(self,simulation):
        pygame.init()
        View.screen = pygame.display.set_mode((self.Xmax, self.Ymax))
        pygame.mouse.set_visible(False)
        View.simulation = simulation
        if not View.simulation:
            self.ts = Touchscreen()
            for touch in self.ts.touches:
                touch.on_press = self.touch_handler
                touch.on_release = self.touch_handler
                touch.on_move = self.touch_handler
            self.ts.run()

    def blankOut(self):
        self.screen.fill((0, 0, 0))

    # Return the nth digit in a positive integer, starting from the right at index 0
    def get_digit(self, number, n):
        return number // 10**n % 10

    def pixelscale(self, number, min, max, pixels):
        #logmax = log(Vmax / Vmin, b)
        #X = Xmax * log(V / Vmin, b) / logmax
        #V = Vmin * b ** (logmax * X / Xmax)
        
        # This seems to correctly distribute the values logarithmically
        #base = 10 # Might be best to use e, but it doesn't seem to make much difference
        #offset = math.log(min,base)
        #return int(pixels * (math.log(number,base) - offset) / (math.log(max,base) - offset))
        
        # Distribute values linearly across pixels
        #print("%s,%s,%s,%s" % (number,min,max,pixels))
        pixelMin = 0
        pixel = pixelMin + ((pixels - pixelMin) / (max - min)) * (number - min)
        if(pixel < pixelMin):
            pixel = pixelMin
        if(pixel > pixels):
            pixel = pixels
        return pixel

    def touchHandler(self):
        if not self.simulation:
            return
        # Scan touchscreen events
        while True:
            for event in pygame.event.get():
                (x,y) = pygame.mouse.get_pos()
                self.moveEvent(x,y)
                if(event.type is MOUSEBUTTONDOWN):
                    pass
                    # Eventually animate the button press here
                    #self.buttonPressFunction()
                elif(event.type is MOUSEBUTTONUP):
                    self.releasedEvent(x,y)
            sleep(0.001)

    def registerWidget(self,widget,id):
        # Widgets can be Buttons, TextFields, etc.  
        # Each widget needs to implement draw()
        # ID values distinguish different dialogs (so widgets end up on the right dialogs)
        if id in self.modality:
            self.dialogWidgets[id].append(widget)
        else:
            self.modality.append(id)
            dialog = {}
            self.dialogWidgets[id] = [widget]

    def unregisterDialog(self,id):
        if id in self.modality:
            self.modality.remove(id)
            del self.dialogWidgets[id]

    def registerPanelWidget(self,widget):
        self.panelWidgets.append(widget)

    def setSimulation(self,simulation):
        self.simulation = simulation

    def draw(self):
        # Draw all of the widgets that have been registered in the most recent dialog
        for widget in self.panelWidgets:
            widget.draw(self.screen)

class Dialog(ABC,View):
    bordersize = 5 # Number of pixels making up the border (includes spacer pixels)
    dialogWidth = 0
    dialogHeight = 0
    surfaceWidth = 0
    surfaceHeight = 0
    objectID = 0
    thisObjectID = 0

    def __init__(self,width,height):
        super(ABC).__init__()
        Dialog.objectID += 1
        self.thisObjectID = Dialog.objectID
        self.surfaceWidth = width
        self.surfaceHeight = height
        self.dialogWidth = width + self.bordersize * 2
        self.dialogHeight = height + self.bordersize * 2
        # Add OK and Cancel buttons
        self.okButton = Button(0, 0, "Ok", "monospace", 25)
        self.cancelButton = Button(0, 0, "Cancel", "monospace", 25)
        buttonHeight = self.okButton.height
        buttonWidthOK = self.okButton.width
        buttonWidthCancel = self.cancelButton.width
        buttonSpacing = 7
        xok = self.dialogWidth - self.bordersize - buttonWidthOK - buttonSpacing
        yok = self.dialogHeight - self.bordersize - buttonHeight - buttonSpacing
        xcancel = self.bordersize + buttonSpacing
        ycancel = self.dialogHeight - self.bordersize - buttonHeight - buttonSpacing
        self.okButton.x = xok
        self.okButton.y = yok
        self.cancelButton.x = xcancel
        self.cancelButton.y = ycancel
        super().registerWidget(Widget(self.okButton,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        super().registerWidget(Widget(self.cancelButton,self.getPhysicalXYOffsetOfSurface()),self.objectID)
        if height < buttonHeight or width < buttonWidthOK + buttonWidthCancel:
            raise ValueError('Dialog too small')

    def registerOKButton(self,method):
        self.okButton.registerButtonRelease(method)

    def registerCancelButton(self,method):
        self.cancelButton.registerButtonRelease(method)

    def getPhysicalXYOffsetOfSurface(self):
        xoffset = (self.Xmax - self.dialogWidth) / 2
        yoffset = (self.Ymax - self.dialogHeight) / 2
        return [xoffset,yoffset]

    def draw(self):
        surface = pygame.Surface((self.surfaceWidth, self.surfaceHeight))
        for w in self.dialogWidgets[self.objectID]:
            # Draw all of the widgets that have been registered
            w.object.draw(surface)
        (width, height) = surface.get_size()
        dialog = pygame.Surface((self.dialogWidth, self.dialogHeight))
        xleft = 0
        ytop = 0
        xright = xleft + self.dialogWidth
        ybottom = ytop + self.dialogHeight
        # Make a border around the dialog surface
        poly1 = [[xleft+1,ytop+1],[xleft+1,ytop+3],[xright-1,ytop+3],[xright-1,ytop+1]]
        poly2 = [[xright-1,ytop+1],[xright-1,ybottom-1],[xright-3,ybottom-1],[xright-3,ytop+1]]
        poly3 = [[xleft+1,ybottom-1],[xleft+1,ybottom-2],[xright-1,ybottom-2],[xright-1,ybottom-1]]
        poly4 = [[xleft+1,ytop+1],[xleft+1,ybottom-1],[xleft+3,ybottom-1],[xleft+3,ytop+1]]
        pygame.gfxdraw.aapolygon(dialog, poly1, self.WHITE)
        pygame.gfxdraw.filled_polygon(dialog, poly1, self.WHITE)
        pygame.gfxdraw.aapolygon(dialog, poly2, self.WHITE)
        pygame.gfxdraw.filled_polygon(dialog, poly2, self.WHITE)
        pygame.gfxdraw.aapolygon(dialog, poly3, self.WHITE)
        pygame.gfxdraw.filled_polygon(dialog, poly3, self.WHITE)
        pygame.gfxdraw.aapolygon(dialog, poly4, self.WHITE)
        pygame.gfxdraw.filled_polygon(dialog, poly4, self.WHITE)
        # Add dialog
        dialog.blit(surface, (xleft+4, ytop+4))
        # Blit to screen
        xoffset = (self.Xmax - self.dialogWidth) / 2
        yoffset = (self.Ymax - self.dialogHeight) / 2
        self.screen.blit(dialog, (xoffset, yoffset))
        # Update mouse pointer while inside the dialog
        if self.simulation:
            (x,y) = pygame.mouse.get_pos()
            pygame.gfxdraw.aacircle(self.screen, x, y, 2, self.WHITE)
            pygame.gfxdraw.filled_circle(self.screen, x, y, 2, self.WHITE)
        return True

class Widget:
    object = None
    xoffset = 0
    yoffset = 0
    width = 0
    height = 0    

    def __init__(self,object,offset):
        self.object = object
        (xoffset,yoffset) = offset
        self.xoffset = xoffset + object.x
        self.yoffset = yoffset + object.y
        self.width = object.width
        self.height = object.height

    def isAt(self,x,y):
        """ Returns true if the specified x and y coordinates are within the area of this widget """
        if (x >= self.xoffset and x <= self.xoffset + self.width and
            y >= self.yoffset and y <= self.yoffset + self.height):
            return True
        else:
            return False

class Button:
    WHITE = (247,247,214)
    GRAY = (99,90,90)
    x = 0
    y = 0
    width = 0
    height = 0
    method = None
     
    def __init__(self,x,y,text,font,size):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.size = size
        font = pygame.font.SysFont(self.font, self.size)
        font.set_bold(True)
        (self.width, self.height) = font.size(self.text)

    def registerButtonRelease(self,method):
        self.method = method

    def buttonReleaseHandler(self):
        self.method()

    def draw(self,surface):
        font = pygame.font.SysFont(self.font, self.size)
        font.set_bold(True)
        surf = font.render(self.text, True, self.WHITE, self.GRAY)
        surface.blit(surf, (self.x, self.y))

class Light:
    WHITE = (247,247,214)
    GRAY = (99,90,90)
    BLACK = (0,0,0)
    BLUE = (97, 149, 255)
    RED = (255, 0, 0)
    GREEN = (65,180,86)
    x = 0
    y = 0
    width = 0
    height = 0
    method = None
     
    def __init__(self,x,y,size):
        self.x = x
        self.y = y
        self.size = size
        font = pygame.font.SysFont("monospace", 12)
        font.set_bold(True)
        (self.width, self.height) = font.size(" ")

    def draw(self,surface,status):
        font = pygame.font.SysFont("monospace", 12)
        font.set_bold(True)
        surf = None
        if status:
            surf = font.render(" ", True, self.GREEN, self.GREEN)
        else:
            surf = font.render(" ", True, self.RED, self.RED)
        surface.blit(surf, (self.x, self.y))

class TextField:
    WHITE = (247,247,214)
    GRAY = (99,90,90)
    text = ""
    font = "monospace"
    size = 12
    x = 0
    y = 0
    width = 0
    height = 0

    def __init__(self,x,y,text,font,size):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.size = size
        self.color = self.WHITE
        font = pygame.font.SysFont(self.font, self.size)
        font.set_bold(True)
        (self.width, self.height) = font.size(self.text)

    def updateText(self,text):
        self.text = text

    def updateFont(self,font):
        self.font = font

    def updateSize(self,size):
        self.size = size

    def updateColor(self,color):
        self.color = color

    def draw(self,surface):
        font = pygame.font.SysFont(self.font, self.size)
        font.set_bold(True)
        surf = font.render(self.text, True, self.color)
        surface.blit(surf, (self.x, self.y))

