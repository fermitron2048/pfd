from ui.pfdview import *
import math

""" 
Panels are static elements of the UI that are always onscreen (possibly behind a dialog).  They are the main displays, such as the speed tape,
altitude tape, vertical speed indicator, bearing indicator, and other status information in various areas on the screen.  The draw method is called
whenever the frame is being updated (nominally 60 frames per second).
"""

class Horizon(View):
    center = 233 # Range is 129 to 331
    
    def __init__(self):
        pass

    def orange(self):
        xleft = 262
        ybottom = 333
        xright = 472
        radius = 19
        pygame.gfxdraw.aacircle(self.screen, xleft, ybottom, radius, self.ORANGE)
        pygame.gfxdraw.filled_circle(self.screen, xleft, ybottom, radius, self.ORANGE)
        pygame.gfxdraw.aacircle(self.screen, xright, ybottom, radius, self.ORANGE)
        pygame.gfxdraw.filled_circle(self.screen, xright, ybottom, radius, self.ORANGE)
        poly1 = [[xleft-radius,self.center],[xleft-radius,ybottom],[(xright+radius),ybottom],[xright+radius,self.center]]
        pygame.gfxdraw.aapolygon(self.screen, poly1, self.ORANGE)
        pygame.gfxdraw.filled_polygon(self.screen, poly1, self.ORANGE)
        poly2 = [[xleft,ybottom+radius],[xleft,ybottom],[xright,ybottom],[xright,ybottom+radius]]
        pygame.gfxdraw.aapolygon(self.screen, poly2, self.ORANGE)
        pygame.gfxdraw.filled_polygon(self.screen, poly2, self.ORANGE)

    def blue(self):
        xleft = 262
        ytop = 129
        xright = 472
        radius = 19
        pygame.gfxdraw.aacircle(self.screen, xleft, ytop, radius, self.BLUE)
        pygame.gfxdraw.filled_circle(self.screen, xleft, ytop, radius, self.BLUE)
        pygame.gfxdraw.aacircle(self.screen, xright, ytop, radius, self.BLUE)
        pygame.gfxdraw.filled_circle(self.screen, xright, ytop, radius, self.BLUE)
        poly1 = [[xleft-radius,ytop],[xleft-radius,self.center],[xright+radius,self.center],[xright+radius,ytop]]
        pygame.gfxdraw.aapolygon(self.screen, poly1, self.BLUE)
        pygame.gfxdraw.filled_polygon(self.screen, poly1, self.BLUE)
        poly2 = [[xleft,ytop-radius],[xleft,ytop],[xright,ytop],[xright,ytop-radius]]
        pygame.gfxdraw.aapolygon(self.screen, poly2, self.BLUE)
        pygame.gfxdraw.filled_polygon(self.screen, poly2, self.BLUE)
        #pygame.draw.rect(self.screen, self.BLUE, [xleft-radius, yleft, (xright+radius)-(xleft-radius), self.center-yleft])
        #pygame.draw.rect(self.screen, self.BLUE, [xleft, yleft, xright-xleft, -radius])
            
    def centerLine(self):
        xleft = 262
        xright = 472
        radius = 19
        poly = [[xleft-radius,self.center+1],[xleft-radius,self.center],
                [xright+radius,self.center],[xright+radius,self.center+1]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        
    def centerGuide(self):
        pass
                            
    def whitePitch(self):
        pass
        
    def whitePitchNumbers(self):
        pass
        
    def whiteYaw(self):
        pass
                 
    def draw(self):
        self.orange()
        self.blue()
        self.centerLine()
        #pygame.display.update((239,106,499,355))

class SpeedTape(View):
    speed = 0

    def __init__(self):
        pass

    def background(self):
        xleft = 145
        ytop = 65
        xright = 209
        ybottom = 404
        poly = [[xleft,ytop],[xleft,ybottom],[xright,ybottom],[xright,ytop]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.GRAY)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.GRAY)
    
    def box1(self):
        poly1 = [[140,210],[190,210],[190,226],[202,235],[190,243],[190,260],[140,260]]
        pygame.gfxdraw.aapolygon(self.screen, poly1, self.BLACK)
        pygame.gfxdraw.filled_polygon(self.screen, poly1, self.BLACK)

    def box2(self):
        poly2 = [[140,211],[189,211],[189,227],[200,235],[189,242],[189,258],[140,258]]
        pygame.gfxdraw.aapolygon(self.screen, poly2, self.WHITE)
        poly3 = [[141,212],[188,212],[188,228],[199,235],[188,241],[188,257],[141,257]]
        pygame.gfxdraw.aapolygon(self.screen, poly3, self.WHITE)
        poly4 = [[197,235],[188,228],[198,235],[188,241]]
        pygame.gfxdraw.aapolygon(self.screen, poly4, self.WHITE)
        poly5 = [[144,213],[187,213],[187,229],[197,235],[187,240],[187,256],[144,256]]
        pygame.gfxdraw.aapolygon(self.screen, poly5, self.BLACK)
        poly6 = [[189,258],[141,258],[141,259],[189,259]]
        pygame.gfxdraw.aapolygon(self.screen, poly6, self.WHITE) # Fix for the bottom white line that doesn't show up
        pygame.gfxdraw.filled_polygon(self.screen, poly6, self.WHITE)
        
    def speedNumbers(self,value):
        textsurf = pygame.Surface((43, 43))
        font = pygame.font.SysFont("monospace", 25)
        font.set_bold(True)
        surf = font.render(str(self.get_digit(int(value),2)) if value >= 100 else " ", True, self.WHITE)
        textsurf.blit(surf, (0, 10))
        surf = font.render(str(self.get_digit(int(value),1)) if value >= 10 else " ", True, self.WHITE)
        textsurf.blit(surf, (13, 10))
        
        # Third digit
        value0 = self.get_digit(math.ceil(value)+1,0)
        value1 = self.get_digit(math.ceil(value),0) if value > 0 else 1
        value2 = self.get_digit(math.floor(value),0)
        value3 = self.get_digit(math.floor(value)-1,0)
        surf = font.render(str(value0), True, self.WHITE)
        offset0 = (value - math.floor(value)) * 20 - 40
        textsurf.blit(surf, (27, 10+offset0))
        surf = font.render(str(value1), True, self.WHITE)
        offset1 = (value - math.floor(value)) * 20 - 20
        textsurf.blit(surf, (27, 10+offset1))
        surf = font.render(str(value2), True, self.WHITE)
        offset2 = (value - math.floor(value)) * 20
        textsurf.blit(surf, (27, 10+offset2))
        surf = font.render(str(value3), True, self.WHITE)
        if(value >= 1):
            offset3 = (value - math.floor(value)) * 20 + 20
            textsurf.blit(surf, (27, 10+offset3))
        self.screen.blit(textsurf, (143,214))

    def whiteLines(self,speed):
        xleft = 145
        ytop = 65
        xright = 209
        xoffset = xright - xleft
        ybottom = int(404 * 200.0 / 60.0) # Tape goes from 0 to 200, and 60MPH fits on one screen
        ybottom2 = 404
        lineWidth = 12
        numberHeight = 18
        pixelsBetweenLines = 27
        xleftLetter = 157 - xleft
        tapeareasurf = pygame.Surface((xright-xleft, ybottom2-ytop))
        tapeareasurf.set_colorkey(self.GRAY)
        tapeareasurf.fill(self.GRAY)
        tapesurf = pygame.Surface((xright-xleft, ybottom-ytop))
        tapesurf.set_colorkey(self.GRAY)
        tapesurf.fill(self.GRAY)
        font = pygame.font.SysFont("monospace", 18)
        font.set_bold(True)
        counter=0
        marks = list(reversed(range(0,ybottom-ytop-10,pixelsBetweenLines+2)))
        for y in marks:
            poly = [[xoffset,y],[xoffset-lineWidth,y],[xoffset-lineWidth,y-1],[xoffset,y-1]]
            pygame.gfxdraw.aapolygon(tapesurf, poly, self.WHITE)
            pygame.gfxdraw.filled_polygon(tapesurf, poly, self.WHITE)
            if(counter % 2 == 0): # Only display even numbers
                if(counter == 0):
                    number = "  0"
                elif(counter < 100):
                    number = " " + str(counter)
                else:
                    number = str(counter) 
                surf = font.render(str(number), True, self.WHITE)
                tapesurf.blit(surf, (xleftLetter, y-numberHeight/2))
            counter+=5
        tapeareasurf.blit(tapesurf, (0,-marks[0]+(ybottom2-ytop)/2+1+(speed*marks[0]/215)))
        self.screen.blit(tapeareasurf, (xleft,ytop))

    def whiteNumbers(self):
        pass
        
    def maxSpeedBlocks(self):
        pass
        
    def draw(self):
        self.background()
        self.whiteLines(self.speed)
        self.box1()
        self.speedNumbers(self.speed)
        self.box2()
        #pygame.display.update((145,65,209,404))

class AltitudeTape(View):
    altitude = 0
    slp = 0

    def __init__(self):
        pass

    def background(self):
        xleft = 539
        ytop = 65
        xright = 603
        ybottom = 404
        poly = [[xleft,ytop],[xleft,ybottom],[xright,ybottom],[xright,ytop]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.GRAY)
    
    def box(self,altitude):
        # Outer black box
        poly1 = [[557,211],[630,211],[630,259],[557,259],[557,244],[546,235],[557,226]]
        pygame.gfxdraw.aapolygon(self.screen, poly1, self.BLACK)
        pygame.gfxdraw.filled_polygon(self.screen, poly1, self.BLACK)
        
        # White band
        poly2 = [[558,212],[629,212],[629,258],[558,258],[558,243],[547,235],[558,227],[558,212],
                 [559,213],[559,228],[549,235],[559,242],[559,257],[628,257],[628,214],[559,214]]
        pygame.gfxdraw.aapolygon(self.screen, poly2, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly2, self.WHITE)
        
        # Inner black box
        
    def altitudeDigits(self,altitude):
        textsurf = pygame.Surface((64, 43))
        font = pygame.font.SysFont("monospace", 25)
        font.set_bold(True)
        # Fist digit
        if(altitude < 10000):
            gsurf = pygame.Surface((17, 25))
            # Top ultimate
            poly = [[9,1],[12,5],[12,4],[10,1]]
            pygame.gfxdraw.aapolygon(gsurf, poly, self.GREEN)
            pygame.gfxdraw.filled_polygon(gsurf, poly, self.GREEN)
            # Top penultimate
            poly = [[5,1],[12,11],[12,10],[6,1]]
            pygame.gfxdraw.aapolygon(gsurf, poly, self.GREEN)
            pygame.gfxdraw.filled_polygon(gsurf, poly, self.GREEN)
            # Middle
            poly = [[1,1],[12,17],[12,18],[1,2]]
            pygame.gfxdraw.aapolygon(gsurf, poly, self.GREEN)
            pygame.gfxdraw.filled_polygon(gsurf, poly, self.GREEN)
            # Bottom penultimate
            poly = [[1,7],[8,18],[7,18],[1,8]]
            pygame.gfxdraw.aapolygon(gsurf, poly, self.GREEN)
            pygame.gfxdraw.filled_polygon(gsurf, poly, self.GREEN)
            # Bottom ultimate
            poly = [[1,13],[4,18],[3,18],[1,14]]
            pygame.gfxdraw.aapolygon(gsurf, poly, self.GREEN)
            pygame.gfxdraw.filled_polygon(gsurf, poly, self.GREEN)
            #textsurf.blit(gsurf, (1, 12))
            
            path = ""
            if not self.simulation:
                path = '/home/pi/jeep/'
            isurf = pygame.image.load(path+'ui/images/GreenLines.png')
            #myimage = pygame.image.tostring(isurf,'RGB')
            #print len(myimage)
            #myimagelist = unpack('i'*len(myimage), myimage)
            #print myimagelist
            isurf.convert()
            textsurf.blit(isurf, (0, 12))
        else:
            pass
        
        # Second digit
        surf = font.render(str(self.get_digit(int(altitude),3)), True, self.WHITE)
        textsurf.blit(surf, (13, 10))
        # Third digit
        font = pygame.font.SysFont("monospace", 20)
        font.set_bold(True)
        surf = font.render(str(self.get_digit(int(altitude),2)), True, self.WHITE)
        textsurf.blit(surf, (28, 13))
        
        #surf = font.render(str(altitude)+", "+self.get_digit(), True, self.WHITE)
        #self.screen.blit(surf, (28, 13))
        
        # Fourth digit
        font = pygame.font.SysFont("monospace", 18)
        font.set_bold(True)
        offset = 13
        value0 = int(self.get_digit(math.ceil(altitude/10)*10+10,1)*10)
        value1 = int(self.get_digit(math.ceil(altitude/10)*10,1)*10) if altitude > 0 else 10
        value2 = int(self.get_digit(math.floor(altitude/10)*10,1)*10)
        value3 = int(self.get_digit(math.floor(altitude/10)*10-10,1)*10)
        oaltitude = altitude / 10.0
        surf = font.render(str(value0 if value0 != 0 else "00"), True, self.WHITE)
        offset0 = (oaltitude - math.floor(oaltitude)) * 20 - 40
        textsurf.blit(surf, (42, offset+offset0))
        surf = font.render(str(value1 if value1 != 0 else "00"), True, self.WHITE)
        offset1 = (oaltitude - math.floor(oaltitude)) * 20 - 20
        textsurf.blit(surf, (42, offset+offset1))
        surf = font.render(str(value2 if value2 != 0 else "00"), True, self.WHITE)
        offset2 = (oaltitude - math.floor(oaltitude)) * 20
        textsurf.blit(surf, (42, offset+offset2))
        surf = font.render(str(value3 if value3 != 0 else "00"), True, self.WHITE)
        if(altitude >= 1):
            offset3 = (oaltitude - math.floor(oaltitude)) * 20 + 20
            textsurf.blit(surf, (42, offset+offset3))
        
        self.screen.blit(textsurf, (562,214))
                
    def whiteLines(self,altitude):
        xleft = 539
        ytop = 65
        xright = 603
        ybottom = int(404 * 10000.0 / 800.0) # Tape goes from 0 to 10000, and 800ft fits on one screen
        ybottom2 = 404
        lineWidth = 12
        xoffset = lineWidth
        numberHeight = 16
        pixelsBetweenLines = 41
        xleftLetter = 20
        tapeareasurf = pygame.Surface((xright-xleft, ybottom2-ytop))
        tapeareasurf.set_colorkey(self.GRAY)
        tapeareasurf.fill(self.GRAY)
        tapesurf = pygame.Surface((xright-xleft, ybottom-ytop))
        tapesurf.set_colorkey(self.GRAY)
        tapesurf.fill(self.GRAY)
        font = pygame.font.SysFont("monospace", 15)
        font.set_bold(True)
        counter=0
        marks = list(reversed(range(0,ybottom-ytop-10,pixelsBetweenLines+2)))
        for y in marks:
            poly = [[xoffset,y],[xoffset-lineWidth,y],[xoffset-lineWidth,y-1],[xoffset,y-1]]
            pygame.gfxdraw.aapolygon(tapesurf, poly, self.WHITE)
            pygame.gfxdraw.filled_polygon(tapesurf, poly, self.WHITE)
            if(counter/100 % 2 == 0): # Only display even hundreds
                if(counter <= 0):
                    number = "   0"
                elif(counter < 100):
                    number = "  " + str(counter)
                elif(counter < 1000):
                    number = " " + str(counter)
                else:
                    number = str(counter) 
                surf = font.render(str(number), True, self.WHITE)
                tapesurf.blit(surf, (xleftLetter, y-numberHeight/2))
            counter+=100
        tapeareasurf.blit(tapesurf, (0,-marks[0]+(ybottom2-ytop)/2+1+(altitude*marks[0]/11500)))
        self.screen.blit(tapeareasurf, (xleft,ytop))

    def whiteNumbers(self):
        pass
        
    def pressure(self,slp):
        textsurf = pygame.Surface((100, 30))
        font = pygame.font.SysFont("monospace", 17)
        font.set_bold(True)
        surf = font.render(str(round(slp,1)), True, self.GREEN)
        font2 = pygame.font.SysFont("monospace", 12)
        font2.set_bold(True)
        surf2 = font2.render("HPA", True, self.GREEN)
        textsurf.blit(surf, (0, 0))
        textsurf.blit(surf2, (70, 4))
        self.screen.blit(textsurf, (540,405))

    def draw(self):
        self.background()
        self.whiteLines(self.altitude)
        self.box(self.altitude)
        self.altitudeDigits(self.altitude)
        self.pressure(self.slp)
        #pygame.display.update((539,65,603,404))

class VertSpeed(View):
    vertspeed = 0

    def __init__(self):
        pass

    def background(self):
        poly = [[621,117],[640,117],[664,172],[664,298],[640,353],[621,353],[621,276],[633,269],[633,202],[621,194]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.GRAY)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.GRAY)
    
    def needle(self,vert):
        needlesurf = pygame.Surface((32, 236))
        needlesurf.set_colorkey(self.GRAY)
        needlesurf.fill(self.GRAY)
        refpixel=115
        basepixel = refpixel
        font = pygame.font.SysFont("monospace", 18)
        font.set_bold(True)
        if(vert > 0):
            a1000 = 50
            a2000 = 33
            a6000 = 26
            if(vert >= 100):
                surf = font.render(str(int(math.fabs(vert))), True, self.WHITE)
                self.screen.blit(surf, (622, 95))
            if(vert <= 1000):
                #print("1000, %s" % self.pixelscale(vert, 0.01, 1000, a1000))
                refpixel = refpixel - self.pixelscale(vert, 0.01, 1000, a1000)
            elif(vert <= 2000):
                #print("2000, %s" % self.pixelscale(vert, 1000, 2000, a2000))
                refpixel = refpixel - a1000 - self.pixelscale(vert, 1000.01, 2000, a2000)
            elif(vert <= 6000):
                #print("6000, %s" % self.pixelscale(vert, 2000, 6000, a6000))
                refpixel = refpixel - a1000 - a2000 - self.pixelscale(vert, 2000.01, 6000, a6000)
            else:
                refpixel = refpixel - a1000 - a2000 - a6000
        elif(vert < 0):
            a1000 = 51
            a2000 = 33
            a6000 = 27
            if(vert <= -100):
                surf = font.render(str(int(math.fabs(vert))), True, self.WHITE)
                self.screen.blit(surf, (622, 360))
            if(vert >= -1000):
                #print("-1000, %s" % self.pixelscale(math.fabs(vert), 0.01, 1000, a1000))
                refpixel = refpixel + self.pixelscale(math.fabs(vert), 0.01, 1000, a1000)
            elif(vert >= -2000):
                #print("-2000, %s" % self.pixelscale(math.fabs(vert), 1000, 2000, a2000))
                refpixel = refpixel + a1000 + self.pixelscale(math.fabs(vert), 1000.01, 2000, a2000)
            elif(vert >= -6000):
                #print("-6000, %s" % self.pixelscale(math.fabs(vert), 2000, 6000, a6000))
                refpixel = refpixel + a1000 + a2000 + self.pixelscale(math.fabs(vert), 2000.01, 6000, a6000)
            else:
                refpixel = refpixel + a1000 + a2000 + a6000
        #print("%s,%s" % (refpixel,vert))
        poly = [[67,basepixel-1],[3,refpixel-2],[2,refpixel],[3,refpixel+2],[67,basepixel+1]]
        pygame.gfxdraw.aapolygon(needlesurf, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(needlesurf, poly, self.WHITE)
        self.screen.blit(needlesurf, (633,119))
        
    def whiteLines(self):
        # Lines
        for i in [125,138,151,168,184,209,259,284,301,317,331,344]:
            poly = [[634,i],[638,i],[638,i+1],[634,i+1]]
            pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
            pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        poly = [[634,234],[648,234],[648,235],[634,235]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        
        # Numbers
        font = pygame.font.SysFont("monospace", 15)
        font.set_bold(True)
        surf = font.render('6', True, self.WHITE)
        self.screen.blit(surf, (624, 119))
        surf = font.render('2', True, self.WHITE)
        self.screen.blit(surf, (624, 145))
        surf = font.render('1', True, self.WHITE)
        self.screen.blit(surf, (624, 178))
        surf = font.render('1', True, self.WHITE)
        self.screen.blit(surf, (624, 278))
        surf = font.render('2', True, self.WHITE)
        self.screen.blit(surf, (624, 311))
        surf = font.render('6', True, self.WHITE)
        self.screen.blit(surf, (624, 338))

    def whiteNumbers(self):
        pass

    def draw(self):
        self.background()
        self.whiteLines()
        self.needle(self.vertspeed)
        #pygame.display.update((621,117,664,353))

class Bearing(View):
    xcenter = 369
    ycenter = 610
    radius = 192
    bearing = 0

    def __init__(self):
        pass

    def background(self):
        pygame.gfxdraw.aacircle(self.screen, self.xcenter, self.ycenter, self.radius, self.GRAY)
        pygame.gfxdraw.filled_circle(self.screen, self.xcenter, self.ycenter, self.radius, self.GRAY)
    
    def needle(self):
        pass
        
    def whiteLines(self,bearing):
        r = self.radius * 1.1
        numlines = 36 * 2
        for i in range(numlines):
            a = 2 * math.pi * (i+1)/numlines*1.0
            b = 0.86
            c = 0.90
            w = 0.2
            if i % 2 == 0:
                b += 0.02
            poly = [[self.xcenter+math.sin(a+math.radians(bearing-w))*(r*b),
                     self.ycenter+math.cos(a+math.radians(bearing-w))*(r*b)],
                    [self.xcenter+math.sin(a+math.radians(bearing-w))*(r*c),
                     self.ycenter+math.cos(a+math.radians(bearing-w))*(r*c)],
                    [self.xcenter+math.sin(a+math.radians(bearing+w))*(r*c),
                     self.ycenter+math.cos(a+math.radians(bearing+w))*(r*c)],
                    [self.xcenter+math.sin(a+math.radians(bearing+w))*(r*b),
                     self.ycenter+math.cos(a+math.radians(bearing+w))*(r*b)]]
            pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
            pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        
    def whiteNumbers(self,bearing):
        r = self.radius * 1.1
        height = 0.77
        numvalues = 36
        for i in range(numvalues):
            a = 2 * math.pi * (i)/numvalues*1.0
            font = None
            if i % 3 == 0:
                font = pygame.font.SysFont("monospace", 20)
                font.set_bold(True)
            else:
                font = pygame.font.SysFont("monospace", 15)
            label = font.render(str(i), True, self.WHITE)
            surf = pygame.transform.rotozoom(label, (numvalues-i)*10+bearing, 1)
            self.screen.blit(surf, (self.xcenter-12+math.sin(a-math.radians(bearing+0))*(r*height),
                                   self.ycenter-math.cos(a-math.radians(bearing+0))*(r*height)-20))

    def bearingReading(self,bearing):
        textsurf = pygame.Surface((80, 30))
        font = pygame.font.SysFont("monospace", 19)
        font.set_bold(True)
        surf = font.render(str(int(round(bearing)))+u'\N{DEGREE SIGN}'+" T", True, self.GREEN)
        text_rect = surf.get_rect()
        text_rect.right = 72
        textsurf.fill(self.GRAY)
        textsurf.blit(surf, text_rect)
        self.screen.blit(textsurf, (335,456))

    def draw(self):
        #bearing = round(bearing, 1)
        self.background()
        self.whiteNumbers(self.bearing)
        self.bearingReading(self.bearing)
        self.whiteLines(self.bearing)
        #pygame.display.update((226,416,508,479))

class Status(View):
    temperature = 0
    humidity = 0
    oat = 0

    def __init__(self):
        pass

    def background(self):
        xleft = 222
        ytop = 9
        xright = 521
        ybottom = 36
        poly = [[xleft,ytop],[xleft,ybottom],[xright,ybottom],[xright,ytop]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.GRAY)
    
    def whiteLines(self):
        poly = [[326,9],[327,9],[327,36],[326,36]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        poly = [[421,9],[422,9],[422,36],[421,36]]
        pygame.gfxdraw.aapolygon(self.screen, poly, self.WHITE)
        pygame.gfxdraw.filled_polygon(self.screen, poly, self.WHITE)
        
    def oatDisplay(self, oat):
        textsurf = pygame.Surface((100, 30))
        font = pygame.font.SysFont("monospace", 19)
        font.set_bold(True)
        surf = font.render(str(round(oat,1))+u'\N{DEGREE SIGN}', True, self.WHITE)
        textsurf.blit(surf, (0, 0))
        self.screen.blit(textsurf, (250,43))
        
    def ienvDisplay(self, temperature, humidity):
        textsurf = pygame.Surface((80, 60))
        font = pygame.font.SysFont("monospace", 19)
        font.set_bold(True)
        surf1 = font.render(str(round(temperature,1))+u'\N{DEGREE SIGN}', True, self.WHITE)
        textsurf.blit(surf1, (0, 0))
        surf2 = font.render(str(round(humidity,1))+"%", True, self.WHITE)
        textsurf.blit(surf2, (0, 20))
        self.screen.blit(textsurf, (450,43))
        
    def draw(self):
        self.background()
        self.whiteLines()
        self.oatDisplay(self.oat)
        self.ienvDisplay(self.temperature, self.humidity)

class LeftPanel(View):
    baroset = None
    fpstext = None
    fpsvalue = None
    fps = 0
    rxLight1 = False
    rxLight2 = False

    def __init__(self):
        self.baroset = Button(30, 420, "Baro Set", "monospace", 16)
        super().registerPanelWidget(Widget(self.baroset,(0,0)))
        self.fpstext = TextField(30,380, "FPS: ", "monospace", 16)
        super().registerPanelWidget(Widget(self.fpstext,(0,0)))
        self.fpsvalue = TextField(79,380, "0", "monospace", 16)
        super().registerPanelWidget(Widget(self.fpsvalue,(0,0)))
        self.rx1lighttext = TextField(43,340, "RX1", "monospace", 16)
        super().registerPanelWidget(Widget(self.rx1lighttext,(0,0)))
        self.rx2lighttext = TextField(78,340, "RX2", "monospace", 16)
        super().registerPanelWidget(Widget(self.rx2lighttext,(0,0)))
        self.rxlight1 = Light(55, 360, 12)
        super().registerPanelWidget(Widget(self.rxlight1,(0,0)))
        self.rxlight2 = Light(90, 360, 12)
        super().registerPanelWidget(Widget(self.rxlight2,(0,0)))

    def registerBarosetOpenedCallback(self,method):
        self.baroset.registerButtonRelease(method)

    def draw(self):
        self.baroset.draw(self.screen)
        self.fpstext.draw(self.screen)
        self.fpsvalue.updateText(str(round(self.fps,1)))
        self.fpsvalue.draw(self.screen)
        self.rx1lighttext.draw(self.screen)
        self.rx2lighttext.draw(self.screen)
        self.rxlight1.draw(self.screen,self.rxLight1)
        self.rxlight2.draw(self.screen,self.rxLight2)

class RightPanel(View):
    menu = None
    date = None
    time = None
    dateString = "--/--/--"
    timeString = "--:--:--"
 
    def __init__(self):
        self.menu = Button(712, 420, "Menu", "monospace", 16)
        super().registerPanelWidget(Widget(self.menu,(0,0)))
        self.date = TextField(680,360, self.dateString, "monospace", 16)
        super().registerPanelWidget(Widget(self.date,(0,0)))
        self.time = TextField(690,380, self.timeString, "monospace", 16)
        super().registerPanelWidget(Widget(self.time,(0,0)))

    def registerMainMenuOpenedCallback(self,method):
        self.menu.registerButtonRelease(method)

    def draw(self):
        self.menu.draw(self.screen)
        self.date.updateText(self.dateString)
        self.date.draw(self.screen)
        self.time.updateText(self.timeString)
        self.time.draw(self.screen)
