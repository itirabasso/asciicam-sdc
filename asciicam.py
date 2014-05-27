#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time
import json
import string
import argparse
import threading
from datetime import datetime
import Image, ImageFont, ImageDraw
import termios, fcntl, struct, sys
try:
    import cv2
    import aalib
    import numpy
except:
    print("Necesitás instalar los siguientes packages:")
    print("aalib (or libaa1), python-scipy, python-open-cv (v +2.x).")
    sys.exit(1)
try: 
    import facebook
except:
    print("No pude importar python-facebook-sdk pero es opcional así que está todo piola.")
    fb = False
    

def getTerminalSize():
    '''
    Magia negra. 
    '''
    s = struct.pack("HHHH", 0, 0, 0, 0)
    fd_stdout = sys.stdout.fileno()
    x = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)
    return struct.unpack("HHHH", x)


def keyboardPoll():
    '''
    '''
    global key
    while True:
        key = ord(sys.stdin.read(1))

def screenshot():
    img = Image.new("RGBA", (terminalSize[0]*8,terminalSize[1]*15),(0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, fontsize)
    lines = string.split(ascii, "\n")
    i = 0
    for l in lines:
        draw.text((5, 15*i), l, font=font)
        i+=1
    # datetime.datetime.now()
    # outputFile = 'output/' + now.strftime("%Y-%m-%d %H:%M:%S") + '.png'
    filename = 'output/' + now.strftime("%Y-%m-%d %H:%M:%S") + '.png'
    img.save(filename)

parser = argparse.ArgumentParser(description='asciicam-sdc')
parser.add_argument('--font', '-f', default='font/clacon.ttf', help="Path a cualquier fuente truetype. Default: clacon.ttf")
parser.add_argument('--fontsize', '-s', default=20, type=int, help='Tamaño de la fuente. Default: 20')

args = parser.parse_args()

font = args.font
fontsize = args.fontsize


# 0 es para agarrar cualquier device.
cam = cv2.VideoCapture(0)
if cam.isOpened():
    rval, image = cam.read()
else:
    rval = False

terminalSize = getTerminalSize()
screen = aalib.AsciiScreen(width=terminalSize[0], height=terminalSize[1])
w = int(cam.get(3)) #CV_CAP_PROP_FRAME_WIDTH)
h = int(cam.get(4)) #CV_CAP_PROP_FRAME_HEIGHT)

frames = 0
threading.Thread(target = keyboardPoll).start()
while rval:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (screen.virtual_size))
    image = Image.fromarray(image)
    screen.put_image((0, 0), image)

    ascii = screen.render()
    # print ascii
    # print "\n"

    if key ==  81 or key == 113: # q || Q
        break
    elif key == 70 or key == 102: # f || F
        screenshot()

    key = -1
    time.sleep(0.0020)
    rval, image = cam.read()

cam.release()


if not fb: sys.exit(0) 
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

print graph.put_photo(open(filename), message="SdC", album_id="me/photos") #/290740541104463/photos")
# print graph.put_wall_post("Facebook, Tu API es una garcha.")