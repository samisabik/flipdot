from pyflipdot.pyflipdot import HanoverController
from pyflipdot.sign import HanoverSign
from serial import Serial
from lightstreamer.client import *
import time

import PIL

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np


disp_h = 7
disp_w = 84

sub = Subscription("MERGE",["NODE3000005"],["Value","TimeStamp"])

class SubListener(SubscriptionListener):
    def onItemUpdate(self, update):
        data = "ISSPee " + update.getValue("Value") + "%"
        print (data)
        arr = char_to_pixels(data, path='nes-arcade-font-2-1-monospaced.ttf', fontsize=7)
        pad_lenght = disp_w - arr.shape[1]
        output = np.pad(arr, ((0, 0), (0, pad_lenght)), 'constant', constant_values=0)
        controller.draw_image(output)

def char_to_pixels(text, path, fontsize):
    font = PIL.ImageFont.truetype(path, fontsize) 
    left, top, right, bottom = font.getbbox(text)
    w, h = right - left, bottom - top
    h *= 2
    image = PIL.Image.new('L', (w, h), 1)  
    draw = PIL.ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    arr = arr[(arr != 0).any(axis=1)]
    return arr



ser = Serial('/dev/ttyUSB0')
controller = HanoverController(ser)

sign = HanoverSign(address=2, width=disp_w, height=disp_h)
controller.add_sign('prototypical', sign)

image = sign.create_image()

sub.addListener(SubListener())

client = LightstreamerClient("https://push.lightstreamer.com","ISSLIVE")
client.subscribe(sub)
client.connect()

while True:
    time.sleep(1)
