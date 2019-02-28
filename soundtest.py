import sys
import os
import random
from enum import Enum
import subprocess

from datetime import datetime
import time
from time import sleep

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance

from gpiozero import Button
from gpiozero import LED

import pygame
import pygame.camera
import pygame.surfarray as surfarray
from pygame.locals import *

import numpy as N

while isSleeping:
    

    # Sleepy ZZzzzzzz face
    display.blit(print5,(0,0))
    pygame.display.flip()
    time.sleep(.2)

    display.blit(print6,(0,0))
    pygame.display.flip()
    time.sleep(.2)

    display.blit(print62,(0,0))
    pygame.display.flip()
    time.sleep(.2)
    
    if currSleepSound == 0:
        sleepChannel = sleeping1.play()
        currSleepSound = 1
    elif currSleepSound == 1:
        if sleepChannel.get_busy == False:
            currSleepSound = 2
            sleepChannel = sleeping2.play()
    else:
        if sleepChannel.get_busy == False:
            currSleepSound = 1
            sleepChannel = sleeping1.play()

    #check the accel
    imuData = adxl345.getAxes(True)
    #print ("   x = %.3fG" % ( imuData['x'] ))
    if(imuData['z'] > sleepAngle):
        isSleeping = False
        sleepChannel.fadeout(1000)
        lastBlinkTime = time.time()
        nextSample = time.time()
