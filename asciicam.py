#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys, time
from time import sleep
import json
import Image
import fcntl
import struct
import curses
import string
import termios
import argparse
import datetime
import ImageFont
import ImageDraw
import traceback
import lalala
from select import select
import thread 
try:
    import cv2
    import aalib
    import numpy
except:
    print("Necesitás instalar los siguientes packages:")
    print("aalib (or libaa1), python-scipy, python-opencv (v +2.x).")
    sys.exit(1)
try:
    import facebook
    fb = True

except:
    print("No pude importar python-facebook-sdk pero es opcional.")
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
    img = Image.new("RGBA", (terminalSize[1]*8, terminalSize[0]*16), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, fontsize)
    lines = string.split(ascii, "\n")
    i = 0
    for l in lines:
        w, h = font.getsize(l)
        draw.text((5, h*i), l, font=font)
        i += 1
    now = datetime.datetime.now()
    filename = 'output/' + now.strftime("%Y-%m-%d %H:%M:%S") + '.png'
    try:
      img.save(filename)
    except Exception as e:
      print("Deberias crear una carpeta output/ para guardar las imagenes.")
      sys.exit(1)
    return filename

def uploadPhoto(graph, filename, msg, albumId = None):
    target = (str(albumId) or "me") + "/photos"
    if fb:
      try:
        print(graph.put_photo(open(filename), message=msg, album_id=target))
      except Exception as e:
        print(str(e))

def getPageToken(graph, pageId):
    accounts = graph.get_object("me/accounts")
    if accounts:
        for acc in accounts['data']:
            if acc['id'] == pageId:
                return acc['access_token']

    raise Exception("No sos admin de la fanpage " + str(pageId))

parser = argparse.ArgumentParser(description='asciicam-sdc')
parser.add_argument(
    '--font', '-f', default='fonts/clacon.ttf',
    help='Path a cualquier fuente truetype. Default: clacon.ttf')
parser.add_argument(
    '--fontsize', '-s', default=20, type=int,
    help='Tamaño de la fuente. Default: 20')
parser.add_argument('--token', '-t', default=False)
parser.add_argument('--pageId', '-p', default=False)
parser.add_argument('--albumId', '-a')

args = parser.parse_args()

font = args.font
fontsize = args.fontsize
userToken = args.token
pageId = args.pageId
albumId = args.albumId

pageId ='150532075077861' 
albumId ='490449634419435' 

userToken = lalala.getTokenMechanize()
#print(userToken)
#sys.exit(0)
if not fb or not (userToken):
    print("Necesito un user token!")
    graph = None
else:
    # Armo un Graph un user token
    graph = facebook.GraphAPI(userToken)

    # Levanto el page token
    # Si leen la doc van a ver que dice que necesitás un extended user token pero es falso.
    try:
        pageToken = getPageToken(graph, pageId)
    except Exception as e:
        print(str(e))
        sys.exit(1)
    print("page token: " + pageToken)
    # Armo un nuevo graph con el page token!
    graph = facebook.GraphAPI(pageToken)


# 0 es para agarrar cualquier device.
cam = cv2.VideoCapture(0)
if cam.isOpened():
    rval, image = cam.read()
else:
    rval = False

tSize = getTerminalSize()

size= (tSize[0]-1, tSize[1]-1)

screen = aalib.AsciiScreen(width=size[1], height=size[0])
w = int(cam.get(3))  # CV_CAP_PROP_FRAME_WIDTH
h = int(cam.get(4))  # CV_CAP_PROP_FRAME_HEIGHT

scr = curses.initscr()
bvalue = 1
cvalue = 1
gvalue = 1.3
gvalueStep = 0.05
cvalueStep = 1

while rval:
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (screen.virtual_size))
        image = Image.fromarray(image)
        screen.put_image((0, 0), image)
        ascii = screen.render(gamma=gvalue, contrast=cvalue, brightness=bvalue)
        if select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            key = ord(sys.stdin.read(1))
        else:
            key = -1

        if key == ord('g'):
            gvalue += gvalueStep
        elif key == ord('G'):
            gvalue -= gvalueStep

        elif key == ord('b'):
            bvalue += cvalueStep
        elif key == ord('B'):
            bvalue -= cvalueStep

        elif key == ord('c'):
            cvalue += cvalueStep
        elif key == ord('C'):
            cvalue -= cvalueStep

        elif key == ord('r'):
            bvalue = 1
            cvalue = 1
            gvalue = 1.3

        elif key == ord('q') or key == ord('Q'):
            break
        elif key == ord('f') or key == ord('F'):
            filename = screenshot(ascii, font, fontsize, size)
            if fb:
                uploadPhoto(
                    graph,
                    filename,
                    "",
                    albumId
                )
    # Deberiamos darle tiempo para que vean al respuesta del server?

        msg = 'brightness=' + str(bvalue) 
        msg += ';contrast=' + str(cvalue)
        msg += ';gamma=' + str(gvalue)
        ascii = ascii[:-len(msg)]
        scr.addstr(0, 0, ascii + msg)
        scr.refresh()

        sleep(0.01)
        rval, image = cam.read()
    except Exception as e:
        curses.endwin()
        traceback.print_exc()
        print(e)
        sys.exit(1)

cam.release()
curses.endwin()
