#############################################################
#
#    NULL & VOID @ Maker Faire Seattle 2017
#
#    Artificially Untelligent Selfie Bot
#
#############################################################
#
# DONE: Camera capture
# DONE: Print to thermal printer
# DONE: Combine two images
# DONE: Text overlay
# DONE: Post text to Twitter
# DONE: Get a shutter button working
# DONE: Keep shooting
# DONE: Switch between Face and Camera with single button
# DONE: Get a display working
# DONE: Show an image set
# DONE: Switch between Face & Camera with toggle switch
# DONE: Custom Image processing
# DONE: Integrate PyGame Image filtering code
# DONE: Shutter sound
# DONE: IMU hooks
# DONE: Expressions: Resting
# DONE: Expressions: Printing
# DONE: Expressions: Sleeping
# DONE: Expressions: Blinks
# DONE: Post image to Twitter
# DONE: Expressions: Random wildcard every so often
# DONE: Add new sounds, new face images
# DONE: Transition between modes

# Cleanup terrible face image loading code 
# Nice to have: Make a GIF

#!/usr/bin/env python

import sys
import os
import random
from enum import Enum

from datetime import datetime
import time
from time import sleep

import cups

import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance

from gpiozero import Button
from gpiozero import LED

import pygame
import pygame.camera
import pygame.surfarray as surfarray
from pygame.locals import *

import numpy as N

from adxl345 import ADXL345

import tweepy


###############################################################
#
# CAMERA STUFF 
#
###############################################################


def captureImage():

    global captureSoundSeq

    if(captureSoundSeq == 1):
        sdInit.play()
    if(captureSoundSeq == 2):
        sdConf.play()
    if(captureSoundSeq == 3):
        sdBegin.play()

        
    captureSoundSeq = captureSoundSeq + 1
    if (captureSoundSeq > 3):
        captureSoundSeq = 1
        
    
    camera = pygame.camera.Camera(DEVICE, (800,480), "RGB")
    camera.start()
    sleep(.25)
    camGrab = camera.get_image()

    #create a new animation canvas
    animFrame = pygame.Surface(lastScreen.get_size())
    animFrame = animFrame.convert()

    # vert wipe
    currentYPosTop = 0
    destYPos = 240
    speedModifier = 7
    for xpx in range(1,100):

        currentYPosTop = currentYPosTop - ((currentYPosTop - destYPos) / speedModifier)
        if(abs( currentYPosTop - destYPos)<.1):
                break
        animFrame.blit(lastScreen,(0,0))
        pygame.draw.rect(animFrame, (0,0,0), (0,0,800,currentYPosTop))
        pygame.draw.rect(animFrame, (0,0,0), (0,480,800,-currentYPosTop))

        display.blit(animFrame, (0,0))
        pygame.display.flip()

    pygame.draw.rect(animFrame, (0,0,0), (0,0,800,480))
    lastScreen.blit(animFrame, (0,0))

   

    capture = True
    #camGrab = pygame.transform.flip(camGrab, False, True)
# ------- REVEAL CAMERA
##
##    if camera.query_image():
##        camGrab = camera.get_image()
##    camGrab = pygame.transform.flip(camGrab, True, False)

# ---------------------- Replace smiley face with cam shot



# ---------------------- Open black bars

    # vert wipe
    currentYPosTop = 241
    destYPos = 0
    BlkSpeedModifier = 6

    
    for xpx in range(1,40):
        if camera.query_image():
            camGrab = camera.get_image()
        #camGrab = pygame.transform.flip(camGrab, True, False)
        
        animFrame.blit(camGrab,(0,0))

        currentYPosTop = currentYPosTop - ((currentYPosTop - destYPos) / BlkSpeedModifier)
        if(abs( currentYPosTop - destYPos)<.1):
            currentYPosTop = 0
        else:       
            pygame.draw.rect(animFrame, (0,0,0), (0,0,800,currentYPosTop))
            pygame.draw.rect(animFrame, (0,0,0), (0,480,800,-currentYPosTop))

        display.blit(animFrame, (0,0))
        pygame.display.flip()



    while capture:
        if camera.query_image():
            captureSurface = camera.get_image()
# flipping
        captureSurface = pygame.transform.flip(captureSurface, False, True)

##        screenArray = pygame.surfarray.pixels3d( captureSurface )
##        screenArray[:,::7] = (0, 0, 0) # add horiz lines every N pixels down
##        for xpx in range(0,5):
##            vertscanline=random.randint(0,445)
##            pygame.draw.line(captureSurface, (255,255,255), (0,vertscanline), (800,vertscanline),1) #Scanlines           
##            pygame.draw.rect(captureSurface, (255,255,255), (random.randint(-800,800),random.randint(-480,480), random.randint(0,800),2)) #Mosaic1
##        thresholded = pygame.surface.Surface((800,480), 0, display)
##        pygame.transform.threshold(thresholded,captureSurface,(255,255,255),(90,170,170),(0,0,0),2, thresholded, True)
##        del screenArray
##
##        #update image in memory and reresh it to display
##
##        display.blit(thresholded, (0,0))
##        pygame.display.flip()
        
        display.blit(captureSurface, (0,0))
        pygame.display.flip()

        if shutterButton.is_pressed:
            pygame.image.save(display, ("CapturedImages/" + photoFileName))
            shutterSound.play()

            flashFrame = pygame.Surface(lastScreen.get_size())
            flashFrame = flashFrame.convert()
            pygame.draw.rect(display, (255,255,255), (0,0, 800,480))
            pygame.display.flip()
            sleep(.25)
            capture = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                appRunning = False
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    appRunning = False
                    break

    camera.stop()

    return



###############################################################
#
# IMAGE STUFF 
#
###############################################################

def processImage():

    setExpression(Expression.PROCESSING)

    # Open the captured image
    photo=Image.open("CapturedImages/" + photoFileName)

    # Reduce to actual print size before processing
    photo = photo.resize((384,230));

    # Open the banner image
    banner=Image.open(bannerFileName)

    # Create drawing layer on top of banner
    bannerPlusText = ImageDraw.Draw(banner)

    #set fonts
    #bigFont = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 25)
    #smallFont = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf', 15)

    #add text to banner
    #bannerPlusText.text((10, 10),"NULL & VOID //",  (0,0,0), font=bigFont)
    #bannerPlusText.text((250, 80),photoFileName,  (0,0,0), font=smallFont)
    bannerPlusText.rectangle((110,0,384,120), (255,255,255))
    bannerPlusText = ImageDraw.Draw(banner)

    #creates a new empty image, RGB mode, and size
    combinedImage = Image.new('RGB', (384,330))
    enh = ImageEnhance.Brightness(photo)
    photo = enh.enhance(2.1)
    photo = photo.transpose(Image.FLIP_LEFT_RIGHT)
    combinedImage.paste(photo, (0,0))
    #blankedBanner = ImageDraw.Draw.rectangle(banner)
 

    combinedImage.paste(banner, (0,220))



    combinedImage.save("ProcessedImages/" + "Print" + photoFileName)
    #combinedImage.show()
    #combinedImage = combinedImage.transpose(Image.FLIP_LEFT_RIGHT)
    #combinedImage = combinedImage.transpose(Image.FLIP_TOP_BOTTOM)

    


###############################################################
#
# TWITTER STUFF 
#
###############################################################
    
def sendTweet(postToTwitter):

    # Set message to tweet
    message = "Taken by SelfieBot"
    
    if postToTwitter == True:
        #send tweet with picture
        photo = open("ProcessedImages/" + "Print" + photoFileName, 'rb')
        api.update_with_media("ProcessedImages/" + "Print" + photoFileName, status=message)

###############################################################
#
# PRINTER STUFF 
#
###############################################################

def printSelfie(printFlag):
    global printSoundSeq
    if(printFlag != False):
        if(printSoundSeq == 1):
            printBig.play()
        if(printSoundSeq == 4):
            printKon.play()
        if(printSoundSeq == 3):
            printPoop.play()
        if(printSoundSeq == 2):
            printDot.play()
            
        printSoundSeq = printSoundSeq + 1
        if (printSoundSeq > 4):
            printSoundSeq = 1
            
        conn = cups.Connection()
        printers = conn.getPrinters()  
        imageToPrint = Image.open("ProcessedImages/" + "Print" + photoFileName)
        imageToPrint = imageToPrint.transpose(Image.ROTATE_180)
        imageToPrint.save("PrintingTemp/" + "printthis.jpg")

        conn.printFile('zj-58', "PrintingTemp/" + "printthis.jpg",'Python_Status_print' ,{})

        setExpression(Expression.PRINTGOING)

            

###############################################################
#
# EXPRESSION ENGINE - Basic faces and sounds
#
###############################################################

def setExpression(mode):
    global lastX, lastY, lastZ, nextSample, resting, lastBlinkTime, lastRestState, lookDirection, lastLookTime, lookWait, lastWildTime, wildWaitTime


    # ----------------------------------------------------- AWAKE ----------------------------

    if(mode==Expression.AWAKE) :
        imuData = adxl345.getAxes(True)
        #check the accel

        # show random looking directions at random intervals
        if(time.time() > lastLookTime +  lookWait):
            #lookDirection = lookDirection + 1
            lookWait = random.random() * 1.5
            #if(lookDirection > 3):
            #    lookDirection = 1
            lookDirection = random.randint(1,5)

            lastLookTime = time.time()



        #print ("   z = %.3fG" % ( imuData['z'] ))
        restingThreshold = .1 # motion threshold

        #goal: if bot left in same position for N seconds, switches faces
        if(time.time() > nextSample):
            imuData = adxl345.getAxes(True)
            
                
            if ( ( abs(imuData['x'] - lastX) < restingThreshold ) & ( abs(imuData['y'] - lastY) < restingThreshold ) & ( abs(imuData['z'] - lastZ) < restingThreshold ) ):
                nextSample = time.time() + exitRestWait # Faster samplerate for leaving resting mode
                resting=True
            else:
                nextSample = time.time() + enterRestWait # Long samplerate for entering resting mode
                resting=False
            lastX = imuData['x']
            lastY = imuData['y']
            lastZ = imuData['z']
                
        if(resting == True): # RESTING
            display.blit(print7,(0,0))
            lastRestState = True
        else: # AWAKE, NOT RESTING
            if (lastRestState == True): # jus woke up, Rest state is false (awake), but was just resting
                #PLAY RANDOM SOUND
                randSound = random.randint(1,5)
                if(randSound == 1):
                    miscBerp.play()
                if (randSound == 2):
                    miscHarro.play()
                if (randSound == 3):
                    miscQ.play()
                if (randSound == 4):
                    miscExit.play()
                if (randSound == 5):
                    miscEllo.play()
                    
                #display.blit(f_Oh,(0,0))
                #pygame.display.flip()
                time.sleep(1.5) #how long blink stays on-screen
                lastBlinkTime = time.time()
                lastRestState = False

            #


            if(lookDirection == 1) :
                display.blit(f_LookLeft,(0,0))
            if(lookDirection == 2) :
                display.blit(f_LookRight,(0,0))
            if(lookDirection == 3) :
                display.blit(f_LookUp,(0,0))
            if(lookDirection == 4) :
                display.blit(f_LookUp,(0,0))

            if(time.time() > lastWildTime + wildWaitTime + random.randint(0,2)) :
                randWildCard = random.randint(1,100)
                if(randWildCard > 99) :
                    display.blit(f_Sing,(0,0))
                    pygame.display.flip()
                    cantina.play()
                    time.sleep(15)
                    
                
                if( (randWildCard > 90) & (randWildCard < 99) ):
                    display.blit(f_LaughBig,(0,0))
                    pygame.display.flip()
                    laughCheeky.play()
                    time.sleep(2.5)
                    

                if( (randWildCard > 80) & (randWildCard < 91) ):
                    display.blit(f_Yawn,(0,0))
                    pygame.display.flip()
                    yawnBig.play()
                    time.sleep(2.5)
                
                if( (randWildCard > 75) & (randWildCard < 80) ):
                    display.blit(f_Wink,(0,0))
                    pygame.display.flip()
                    halbeep.play()
                    time.sleep(1)

                if( (randWildCard > 70) & (randWildCard < 75) ):
                    display.blit(f_Hmmm,(0,0))
                    pygame.display.flip()
                    haldave.play()
                    time.sleep(3)

                if( (randWildCard > 65) & (randWildCard < 70) ):
                    display.blit(f_Hmmm,(0,0))
                    pygame.display.flip()
                    halsorry.play()
                    time.sleep(3)


                if( (randWildCard > 60) & (randWildCard < 65) ):
                    display.blit(f_Oh,(0,0))
                    pygame.display.flip()
                    miscBerp.play()
                    time.sleep(1.5)
                    
##                if( (randWildCard > 55) & (randWildCard < 60) ):
##                    display.blit(f_Excited,(0,0))
##                    pygame.display.flip()
##                    thankyou.play()
##                    time.sleep(1.5)

                if( (randWildCard > 0) & (randWildCard < 55) ):
                    display.blit(f_Excited,(0,0))
                    pygame.display.flip()
                    #thankyou.play()
                    time.sleep(1.5)

                    
                lastWildTime = time.time()


            # blink logic
            if(time.time() > (lastBlinkTime + random.randint(6,8))):
                lastBlinkTime = time.time()
                display.blit(print7,(0,0))
                pygame.display.flip()
                time.sleep(.15) #how long blink stays on-screen

        pygame.display.flip()
        
        if(imuData['z'] < sleepAngle):
            botMode = BotMode.SLEEPING
            setExpression(Expression.SLEEPING)
            botMode = BotMode.FACE

        if( (imuData['y'] < laughAngle) | (imuData['y'] > -laughAngle) ):
            setExpression(Expression.LAUGHING)

        if(imuData['z'] > -sleepAngle):
            setExpression(Expression.FACEDOWN)



    # ----------------------------------------------------- PROCESSING ----------------------------

        
    if(mode==Expression.PROCESSING):
        display.blit(print1,(0,0))
        pygame.display.flip()

    # ----------------------------------------------------- PRINTING ----------------------------

    if(mode==Expression.PRINTGOING):
        t_end = time.time() + 1.5 #how long to show random processing face
        while time.time() < t_end:
           
            # Happy Printy face
            display.blit(print1,(0,0))
            pygame.display.flip()
            time.sleep(.1)
        
            display.blit(print4,(0,0))
            pygame.display.flip()
            time.sleep(.1)

        t_end = time.time() + 13 #how long to show random printing face
        while time.time() < t_end:

            printFlip = random.choice([True, False])
           
            if(printFlip):
                # Happy Printy face
                display.blit(print2,(0,0))
                pygame.display.flip()
                time.sleep(.1)
            
                display.blit(print3,(0,0))
                pygame.display.flip()
                time.sleep(.1)

            else:
                # Squinchy face
                display.blit(print1,(0,0))
                pygame.display.flip()
                time.sleep(.1)

                display.blit(print4,(0,0))
                pygame.display.flip()
                time.sleep(.1)
        lastBlinkTime = time.time()
        lastWildTime = time.time()

    # ----------------------------------------------------- LAUGHING ----------------------------
    
    if(mode==Expression.LAUGHING):
            laughQuirk.play()
            t_end = time.time() + 2 #how long to show rlaugb flipper
            while time.time() < t_end:
           
                # Happy Printy face
                display.blit(print1,(0,0))
                pygame.display.flip()
                time.sleep(.1)
            
                display.blit(print4,(0,0))
                pygame.display.flip()
                time.sleep(.1)


    # ----------------------------------------------------- FACEDOWN ----------------------------

    if(mode==Expression.FACEDOWN):

        isFaceDown = True
        # yawn sound
        #yawnTired.play()
        
        # yawn face
        #display.blit(f_Oh,(0,0))
        #pygame.display.flip()
        #time.sleep(1)
        
        while isFaceDown:
           
            sdInit.play()
            display.blit(f_Hmmm,(0,0))
            pygame.display.flip()
            time.sleep(2)


            #check the accel
            imuData = adxl345.getAxes(True)
            #print ("   x = %.3fG" % ( imuData['x'] ))
            if(imuData['z'] < -sleepAngle):
                isFaceDown = False
                lastBlinkTime = time.time()
                lastWildTime = time.time()


            #see if bot has been moved
            # if so, set flag to leave sleep loop

    # ----------------------------------------------------- SLEEPING ----------------------------

    if(mode==Expression.SLEEPING):

        isSleeping = True
        # yawn sound
        #yawnTired.play()
        
        # yawn face
        display.blit(f_Oh,(0,0))
        pygame.display.flip()
        time.sleep(1)
        
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

            #check the accel
            imuData = adxl345.getAxes(True)
            #print ("   x = %.3fG" % ( imuData['x'] ))
            if(imuData['z'] > sleepAngle):
                isSleeping = False
                lastBlinkTime = time.time()
                nextSample = time.time()

            #see if bot has been moved
            # if so, set flag to leave sleep loop
            

###############################################################
#
# Set program variables
#
###############################################################


shutterButton = Button(17)
#ResetSwitch = Button(4)

# Define some variables that you can reference by human readable name
# For example, I can set something to a value of 1 with Bot.Mode.FACE
class BotMode(Enum):
    FACE = 1
    CAMERA = 2
    SLEEPING = 3

# Set initial bot's status flag 
botMode = BotMode.CAMERA;

class Expression(Enum):
    AWAKE = 1
    PROCESSING = 2
    PRINTGOING = 3
    SLEEPING = 4
    LAUGHING = 5
    FACEDOWN = 6

# Where to save the original capture from the camera
#photoFileName =  "Selfie_"+datetime.utcnow().strftime('%Y_%m_%d_%H-%M-%S-%f')[:-3]+".jpg"
photoFileName = ""

# What file to use for banner graphic on printout
bannerFileName = "Graphics/PrintBanner.jpg"

captureSoundSeq =1
printSoundSeq = 1
adxl345 = ADXL345()

DEVICE = '/dev/video0'

# Setup for showing images with pygame
pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init()
pygame.camera.init()

display = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
#display = pygame.display.set_mode((800,480), 0)


#buffer Screen for keeping screen state in
lastScreen = pygame.Surface(display.get_size())
lastScreen = lastScreen.convert()

image1 = pygame.image.load("./FaceImages/Awake1.png")
image2 = pygame.image.load("./FaceImages/Squinchy1.png")
image3 = pygame.image.load("./FaceImages/Printing1.png")
image4 = pygame.image.load("./FaceImages/Printing2.png")
image5 = pygame.image.load("./FaceImages/Squinchy2.png")
image6 = pygame.image.load("./FaceImages/Sleeping1.png")
image7 = pygame.image.load("./FaceImages/Sleeping2.png")
image72 = pygame.image.load("./FaceImages/Sleeping3.png")
image8 = pygame.image.load("./FaceImages/Content.png")

ohFace = pygame.image.load("./FaceImages/Oh.png")
laughFaceFile = pygame.image.load("./FaceImages/Laughing.png")
hmmmFaceFile = pygame.image.load("./FaceImages/Hmmm.png")

lookLeftFaceFile = pygame.image.load("./FaceImages/LookLeft.png")
lookRightFaceFile = pygame.image.load("./FaceImages/LookRight.png")
lookUpFaceFile = pygame.image.load("./FaceImages/LookUp.png")
lookUpFaceFile2 = pygame.image.load("./FaceImages/LookUp2.png")

yawnFaceFile = pygame.image.load("./FaceImages/Yawn.png")
winkFaceFile = pygame.image.load("./FaceImages/Wink.png")

singFaceFile = pygame.image.load("./FaceImages/Sing.png")

excitedFaceFile = pygame.image.load("./FaceImages/Excited.png")

#make a new surface to put an image inside
smile1 = pygame.Surface(display.get_size())
#make it the right colorspace
smile1 = smile1.convert()
#put the image in to the surface 
smile1.blit(image1,(0,0))


f_Excited = pygame.Surface(display.get_size())
f_Excited = f_Excited.convert()
f_Excited.blit(excitedFaceFile,(0,0))

f_Oh = pygame.Surface(display.get_size())
f_Oh = f_Oh.convert()
f_Oh.blit(ohFace,(0,0))

f_LaughBig = pygame.Surface(display.get_size())
f_LaughBig = f_LaughBig.convert()
f_LaughBig.blit(laughFaceFile,(0,0))

f_Hmmm = pygame.Surface(display.get_size())
f_Hmmm = f_Hmmm.convert()
f_Hmmm.blit(hmmmFaceFile,(0,0))

f_LookLeft = pygame.Surface(display.get_size())
f_LookLeft = f_LookLeft.convert()
f_LookLeft.blit(lookLeftFaceFile,(0,0))

f_LookRight = pygame.Surface(display.get_size())
f_LookRight = f_LookRight.convert()
f_LookRight.blit(lookRightFaceFile,(0,0))


f_LookUp = pygame.Surface(display.get_size())
f_LookUp = f_LookUp.convert()
f_LookUp.blit(lookUpFaceFile,(0,0))


f_LookUp2 = pygame.Surface(display.get_size())
f_LookUp2 = f_LookUp2.convert()
f_LookUp2.blit(lookUpFaceFile2,(0,0))


f_Yawn = pygame.Surface(display.get_size())
f_Yawn = f_Yawn.convert()
f_Yawn.blit(yawnFaceFile,(0,0))


f_Wink = pygame.Surface(display.get_size())
f_Wink = f_Wink.convert()
f_Wink.blit(winkFaceFile,(0,0))


f_Sing = pygame.Surface(display.get_size())
f_Sing = f_Sing.convert()
f_Sing.blit(singFaceFile,(0,0))

# need to re-factor worst file loading code ever 

#sw=quinchy1
print1 = pygame.Surface(display.get_size())
print1 = print1.convert()
print1.blit(image2,(0,0))

print2 = pygame.Surface(display.get_size())
print2 = print2.convert()
print2.blit(image3,(0,0))

print3 = pygame.Surface(display.get_size())
print3 = print3.convert()
print3.blit(image4,(0,0))

#sq 2
print4 = pygame.Surface(display.get_size())
print4 = print4.convert()
print4.blit(image5,(0,0))

print5 = pygame.Surface(display.get_size())
print5 = print5.convert()
print5.blit(image6,(0,0))

print6 = pygame.Surface(display.get_size())
print6 = print6.convert()
print6.blit(image7,(0,0))

print62 = pygame.Surface(display.get_size())
print62 = print62.convert()
print62.blit(image72,(0,0))

print7 = pygame.Surface(display.get_size())
print7 = print7.convert()
print7.blit(image8,(0,0))




# Setup Twitter credentials and create the twitter object with them
CONSUMER_KEY = 'GESEJlzQ1SdVDPkL1WMqCDduy'
CONSUMER_SECRET = 'xHlIHMIAhCsTLvvD3RW0R6rQFg4lQZYJVBpmDV3gbz1SWjSQ3U'
ACCESS_KEY = '893582727118585856-cEHuNoe0tv7gA7GPNlKFPQIbgQFkYeu'
ACCESS_SECRET = 'sW5zuktRrrv6Enll48N4gN5wLr018KCw0zxDph5lXMNNd'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET) # Twitter requires all requests to use OAuth for authentication
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET) 
api = tweepy.API(auth)


# ------------ AUDIO FILES ---------------------------------- 

shutterSound = pygame.mixer.Sound('Sounds/shutter.wav')
shutterSound.set_volume(0.7)

## ---------------------------------------------------------------------------------

printBig = pygame.mixer.Sound('Sounds/Printing/bigPoopPrint.wav')
printBig.set_volume(1.0)

printDot = pygame.mixer.Sound('Sounds/Printing/DotMatPrint.wav')
printDot.set_volume(1.0)

printKon = pygame.mixer.Sound('Sounds/Printing/KonataPrint.wav')
printKon.set_volume(1.0)

printPoop = pygame.mixer.Sound('Sounds/Printing/PoopPrint.wav')
printPoop.set_volume(1.0)

## ---------------------------------------------------------------------------------

laughBig = pygame.mixer.Sound('Sounds/Laughs/bigLaugh.wav')
laughBig.set_volume(1.0)

laughCheeky = pygame.mixer.Sound('Sounds/Laughs/cheekyLaugh.wav')
laughCheeky.set_volume(1.0)

laughQuirk = pygame.mixer.Sound('Sounds/Laughs/quirkyLaugh.wav')
laughQuirk.set_volume(1.0)

## ---------------------------------------------------------------------------------

bored = pygame.mixer.Sound('Sounds/misc/bored.wav')
bored.set_volume(1.0)

cantina = pygame.mixer.Sound('Sounds/cantinaband.wav')
cantina.set_volume(1.0)

halbeep = pygame.mixer.Sound('Sounds/samples/halbeep.wav')
halbeep.set_volume(1.0)

haldave = pygame.mixer.Sound('Sounds/samples/haldave.wav')
haldave.set_volume(1.0)

halsorry = pygame.mixer.Sound('Sounds/samples/halsorry.wav')
halsorry.set_volume(1.0)

#omg = pygame.mixer.Sound('Sounds/samples/omg.mp3')
#omg.set_volume(1.0)

#thankyou = pygame.mixer.Sound('Sounds/samples/thankyou.wav')
#thankyou.set_volume(1.0)


## ---------------------------------------------------------------------------------

miscBerp = pygame.mixer.Sound('Sounds/Wake-up/berp.wav')
miscBerp.set_volume(1.0)

miscEllo = pygame.mixer.Sound('Sounds/Wake-up/ello.wav')
miscEllo.set_volume(1.0)

miscExit = pygame.mixer.Sound('Sounds/Wake-up/exit-wake.wav')
miscExit.set_volume(1.0)

miscHarro = pygame.mixer.Sound('Sounds/Wake-up/harro.wav')
miscHarro.set_volume(1.0)

miscQ = pygame.mixer.Sound('Sounds/Wake-up/harroQ.wav')
miscQ.set_volume(1.0)

## ---------------------------------------------------------------------------------

yawnBig = pygame.mixer.Sound('Sounds/yawns/bigYawn.wav')
yawnBig.set_volume(1.0)

yawnTired = pygame.mixer.Sound('Sounds/yawns/tiredYawn.wav')
yawnTired.set_volume(1.0)

## ---------------------------------------------------------------------------------

sdInit = pygame.mixer.Sound('Sounds/SelfDestruct/SD_initiated.wav')
sdInit.set_volume(1.0)

sdBegin = pygame.mixer.Sound('Sounds/SelfDestruct/SD_begin.wav')
sdBegin.set_volume(1.0)

sdConf = pygame.mixer.Sound('Sounds/SelfDestruct/SD_confirmed.wav')
sdConf.set_volume(1.0)

sdKid = pygame.mixer.Sound('Sounds/SelfDestruct/SD_kidding.wav')
sdKid.set_volume(1.0)

sleepAngle = -.9
laughAngle = -.6

enterRestWait = 10
exitRestWait = .1

lookDirection=1
lastLookTime = time.time()
lookWait = 0

lastWildTime = time.time()
wildWaitTime = 6

imuData = adxl345.getAxes(True)
lastX = 0.01
lastY = 0.01
lastZ = 0.01


nextSample = time.time()
resting=False

lastBlinkTime = time.time()
lastRestState = False

appRunning = True

while appRunning == True:
    try:


            
        # Switch to camera mode if face is showing, and someone presses button
        if (botMode == BotMode.FACE) & shutterButton.is_pressed:
            botMode = BotMode.CAMERA
        else:
            botMode = BotMode.FACE
            
        if (botMode == BotMode.FACE):
            setExpression(Expression.AWAKE)
        else:
            photoFileName =  "Selfie_"+datetime.utcnow().strftime('%Y_%m_%d_%H-%M-%S-%f')[:-3]+".jpg"
            #push last screen contents to buffer Surface
            lastScreen.blit(display,(0,0))

            captureImage()

            #shows face while printing
            processImage()
            sendTweet(False)
            printSelfie(True)
            
            botMode = BotMode.FACE
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                appRunning = False
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    appRunning = False
                    break


    except KeyboardInterrupt:

        pygame.quit()
        break
