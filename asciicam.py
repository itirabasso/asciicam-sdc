import sys
import cv2
import time
import numpy 
import Image, ImageFont, ImageDraw
import aalib
import scipy

# cv2.namedWindow("frame")
cam = cv2.VideoCapture(0)

if cam.isOpened():
    rval, image = cam.read()
else:
    rval = False

screen = aalib.AsciiScreen(width=170, height=55)
w = int(cam.get(3)) #CV_CAP_PROP_FRAME_WIDTH)
h = int(cam.get(4)) #CV_CAP_PROP_FRAME_HEIGHT)
while rval:
    # cv2.imshow('frame', image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (screen.virtual_size))
    image = Image.fromarray(image, 'L')
    screen.put_image((0, 0), image)

    print screen.render()
    # print "\n"
    key = cv2.waitKey(25)
    #ESC
    if key == 27: break
    rval, image = cam.read()

cam.release()
# cv2.destroyWindow("frame")
