#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time
import json
import string
import argparse
import datetime
import Image, ImageFont, ImageDraw
import termios, fcntl, struct, sys
import select
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
    fb = True

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


def screenshot(ascii, font, fontsize, terminalSize):
    img = Image.new("RGBA", (terminalSize[1]*8,terminalSize[0]*15),(0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, fontsize)
    lines = string.split(ascii, "\n")
    i = 0
    for l in lines:
        draw.text((5, 15*i), l, font=font)
        i+=1
    now = datetime.datetime.now()
    filename = 'output/' + now.strftime("%Y-%m-%d %H:%M:%S") + '.png'
    # TODO : 
    img.save(filename)
    return filename

def uploadPhoto(filename, msg, albumId=None):
    target = str(albumId) or "me"
    print graph.put_photo(open(filename), message=msg, album_id=target + "/photos") #/290740541104463/photos")
    # print graph.put_wall_post("Facebook, Tu API es una garcha.")

# Test :D
def getPageToken(graph, pageId):
    accounts = graph.get_object("me/accounts")
    if accounts:
        for acc in accounts['data']:
            if acc['id'] == pageId:
                return acc['accessToken']

    raise Exception("No sos admin de la fanpage " + str(pageId))

parser = argparse.ArgumentParser(description='asciicam-sdc')
parser.add_argument('--font', '-f', default='fonts/clacon.ttf', help="Path a cualquier fuente truetype. Default: clacon.ttf")
parser.add_argument('--fontsize', '-s', default=20, type=int, help='Tamaño de la fuente. Default: 20')
parser.add_argument('--token', '-t', default=False, help='User token')

args = parser.parse_args()

font = args.font
fontsize = args.fontsize
userToken = args.token

# 0 es para agarrar cualquier device.
cam = cv2.VideoCapture(0)
if cam.isOpened():
    rval, image = cam.read()
else:
    rval = False

terminalSize = getTerminalSize()
screen = aalib.AsciiScreen(width=terminalSize[1], height=terminalSize[0])
w = int(cam.get(3)) # CV_CAP_PROP_FRAME_WIDTH
h = int(cam.get(4)) # CV_CAP_PROP_FRAME_HEIGHT

while rval:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (screen.virtual_size))
    image = Image.fromarray(image)
    screen.put_image((0, 0), image)

    ascii = screen.render()
    print ascii + "\n"


    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        key = ord(sys.stdin.read(1))
    else:
        key = -1
    if key > 0:
        if key ==  81 or key == 113: # q || Q
            break
        elif key == 70 or key == 102: # f || F
            screenshot(ascii, font, fontsize, terminalSize)

    time.sleep(0.0020)
    rval, image = cam.read()


cam.release()

if not fb or not userToken:
    print "Necesito un user token!"
    graph = None    
else:    
    graph = facebook.GraphAPI(userToken)

# TODO : Automatizarlo
# si expira el token: 
# print graph.extend_access_token(appId, appSecret)
# sys.exit(0)

