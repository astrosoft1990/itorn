# -*- coding: utf-8 -*-
from PIL import Image,ImageFont,ImageDraw
import os, time, random, sys, re
import GLOBAL_CONFIG
debug_text = u'''Lorem 
ipsum 
dolor 
sit er 
elit lamet, 
consectetaur cillium 
adipisicing pecu, 
sed do 
eiusmod tempor 
incididunt ut labore et 
dolore 
magna aliqua. 
Ut enim ad minim 
veniam, quis 
nostrud 
exercitation 
ullamco laboris 
nisi 
ut aliquip 
ex ea 
commodo 
consequat. 
Duis 
aute irure
 dolor in 
reprehenderit in 
voluptate 
velit esse cillum 
dolore eu 
fugiat nulla
 pariatur. 
 Excepteur sint 
occaecat 
cupidatat 
non proident, 
sunt in 
culpa qui 
officia 
deserunt mollit 
anim id est laborum. 
Nam 
liber te 
conscient 
to factor
 tum poen legum 
odioque 
civiuda.'''

CURRENT_OS_PATH = os.path.split(os.path.realpath(__file__))[0]

def split_torn_numner(sender_card) -> str:
    torn_number = 0
    r = re.search('([0-9]{6,})', sender_card)
    if r:
        torn_number = r.group(1)
        torn_number = ''.join(torn_number.split(' '))
    return torn_number


def unique_string() -> str:
    return "%f_%d" % (time.time(), random.randint(100000, 1000000))


def text_to_image(text: str) -> str:
    im = Image.new("L", (1, 1), (255))
    dr = ImageDraw.Draw(im)
    font_path = os.path.join(CURRENT_OS_PATH, "MicrosoftYaHeiMono.ttf")
    font = ImageFont.truetype(font_path, 32)
    width, height = dr.textsize(text, font=font)
    print(width, height)
    im = im.resize((width + 10,height + 20))
    dr = ImageDraw.Draw(im)
    dr.text((5, 5), text, font=font, fill="#000000")

    filename = unique_string()+'.jpg'
    path = os.path.join(GLOBAL_CONFIG.CQ_DATA_IMAGE_PATH, filename)
    im.save(path)
    return filename


def number_to_format_str(number: float):
    number = float(number)
    negative = ''
    if number < 0:
        negative = '-'
        number = -number
    t = [pow(10, 9), pow(10, 6), pow(10, 3)]
    p = ['B', 'M', 'K']
    for i in range(len(t)):
        if number > t[i]:
            d_number = number / (t[i] * 1.0)
            number_str = ''
            if d_number == round(d_number):
                number_str = negative + "%d%s" % (d_number, p[i])
            else:
                number_str = negative + "%.3lf%s" % (d_number, p[i])
            return number_str

    number_str = ''
    if number == round(number):
        number_str = negative + "%d" % number
    else:
        number_str = negative + "%.3lf" % number
    return number_str