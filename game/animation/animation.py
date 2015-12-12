#! /usr/bin/env python

import sys
import os
import pygame
from pygame.locals import *

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import game_lib

'''
def load_image(image_path):

    from PIL import Image
    from PIL import ImageDraw
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode)
'''

pygame.init()

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

# set up the window
DISPLAYSURF = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('Animation')

WHITE = (255, 255, 255)

#catImg = pygame.image.load('cat.png')
catImg = game_lib.load_image('cat.png')
catx = 10
caty = 10
direction = 'right'

while True: # the main game loop
    DISPLAYSURF.fill(WHITE)

    if direction == 'right':
        catx += 5
        if catx == 280:
            direction = 'down'
    elif direction == 'down':
        caty += 5
        if caty == 220:
            direction = 'left'
    elif direction == 'left':
        catx -= 5
        if catx == 10:
            direction = 'up'
    elif direction == 'up':
        caty -= 5
        if caty == 10:
            direction = 'right'

    DISPLAYSURF.blit(catImg, (catx, caty))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)
