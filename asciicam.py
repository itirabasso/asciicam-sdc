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
from select import select
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
    img.save(filename)
    return filename


def uploadPhoto(graph, filename, msg, albumId = None):
    target = (str(albumId) or "me") + "/photos"
    print(graph.put_photo(open(filename), message=msg, album_id=target))


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

import curses
scr = curses.initscr()

while rval:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (screen.virtual_size))
    image = Image.fromarray(image)
    screen.put_image((0, 0), image)
    ascii = screen.render()

    if select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        key = ord(sys.stdin.read(1))
    else:
        key = -1
    if key > 0:
        if key == 81 or key == 113:  # q || Q
            break
        elif key == 70 or key == 102:  # f || F
            filename = screenshot(ascii, font, fontsize, size)
            uploadPhoto(graph, filename, "Mensajin", albumId)
# Deberiamos darle tiempo para que vean al respuesta del server?

    try:
        scr.addstr(0, 0, ascii)
        scr.refresh()
    except Exception as e:
        print(e)
        curses.endwin()
        sys.exit(1)

    sleep(0.01)
    rval, image = cam.read()

cam.release()
curses.endwin()
# TODO : Automatizarlo
# si expira el token:
# print graph.extend_access_token(appId, appSecret)
# sys.exit(0)
