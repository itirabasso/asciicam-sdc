#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import json
try:
    import cv2
    import aalib
    import numpy
    import facebook
except:
    print("Necesitás los siguientes packages:")
    print("aalib (or libaa1), python-scipy, python-open-cv (v +2.x) y python-facebook-sdk (requests v1.4.2):")
    sys.exit(1)
import string
import Image, ImageFont, ImageDraw

# cv2.namedWindow("frame")
cam = cv2.VideoCapture(0)
if cam.isOpened():
    rval, image = cam.read()
else:
    rval = False

# TODO : Configurarlo.
screen = aalib.AsciiScreen(width=170, height=55)
w = int(cam.get(3)) #CV_CAP_PROP_FRAME_WIDTH)
h = int(cam.get(4)) #CV_CAP_PROP_FRAME_HEIGHT)

frames = 0
# TODO : Hay que usar ncurses para levantar el input del teclado.
# select queda descartado.
while rval: # and frames < 20:
    # cv2.imshow('frame', image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (screen.virtual_size))
    image = Image.fromarray(image)
    screen.put_image((0, 0), image)

    ascii = screen.render()
    print ascii
    print "\n"

    # # key = cv2.waitKey(20)
    # # print key
    # if key == 27: # ESC
    #     break
    # elif key == 70 or key == 102: # f || F
    #     break

    frames += 1
    time.sleep(0.0020)
    rval, image = cam.read()

cam.release()
# cv2.destroyWindow("frame")

# TODO : Configurar.
img = Image.new("RGBA", (1366,900),(0,0,0))
draw = ImageDraw.Draw(img)
# font = ImageFont.truetype("AndroidSansMono.ttf", 17)
# font = ImageFont.truetype("cour.ttf", 14)
font = ImageFont.truetype("clacon.ttf", 20)
lines = string.split(ascii, "\n")
i = 0
for l in lines:
    draw.text((5, 15*i), l, font=font)
    i+=1
img.save("output.png")


# TODO : levantarlo de un properties o similar
userToken = None

if userToken == None:
    print "Necesito un user token válido"
    sys.exit(1)

graph = facebook.GraphAPI(userToken)

# TODO : Automatizarlo
# si expira el token: 
# print graph.extend_access_token(appId, appSecret)
# sys.exit(0)

print graph.put_photo(open("output.png"), message="SdC", album_id="me/photos") #/290740541104463/photos")
# print graph.put_wall_post("Facebook, Tu API es una garcha.")