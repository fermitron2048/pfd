#!/usr/bin/python3

import pygame
import pygame.gfxdraw
from pygame.locals import *
import math
import os
import signal
from subprocess import call
import threading
import subprocess
import socket
from struct import *
import collections
import numpy as np
import os.path
from os import path
import json
import time
from datetime import datetime
from time import sleep
import sys
from abc import ABC, abstractmethod
from data.parameter import *
from data.pfdmodel import *
from ui.pfdview import *
from pfdcontroller import *
from ui.panels import *
from ui.pfdmainview import *

# Determine whether or not this is a simulation
simulation = False
if not path.exists("/home/pi/Desktop"):
    simulation = True

# Instantiate MVC objects
model = Model(simulation)
view = PFDView(simulation)
controller = Controller(model, view, simulation)

# Launch threads
functions = [model.readMainSensorPack, view.touchHandler, controller.setScreenBrightness, 
             model.readOATSensorPack, model.writeSensorData, model.writeStateFile]
for function in functions:
    t = threading.Thread(target=function)
    t.daemon = True
    t.start()

# Catch SIGTERM and exit
def receiveSIGTERM(signalNumber, frame):
    raise SystemExit('Exiting on signal '+str(signalNumber))

signal.signal(signal.SIGTERM, receiveSIGTERM)

# Main thread is the Controller view caller
controller.displayActiveViews()
