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

pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init()
pygame.mixer.init()
#screen=pygame.display.set_mode((400,400),0,32) 

isSleeping = True
currSleepSound = 0

print("Initializing")
sleeping1 = pygame.mixer.Sound('Sounds/sleep/sleeping1.wav')
sleeping1.set_volume(1.0)
sleeping2 = pygame.mixer.Sound('Sounds/sleep/sleeping2.wav')
sleeping2.set_volume(1.0)
sleeping1.play()
count = 0

while isSleeping:
  pygame.time.delay(1000)
  print("isSleeping Loop: ")
  print(count)
  if currSleepSound == 0:
    print("currSleepSound == 0")
    sleepChannel = sleeping1.play()
    currSleepSound = 1
  elif currSleepSound == 1:
    print("currSleepSound == 1")
    if sleepChannel.get_busy == False:
      print("sleepChannel.get_busy == False")
      currSleepSound = 2
      sleepChannel = sleeping2.play()
  else:
    print("else")
    if sleepChannel.get_busy == False:
      currSleepSound = 1
      sleepChannel = sleeping1.play()

  if(count > 3):
    isSleeping = False
    sleepChannel.fadeout(1000)
  else:
    count += 1