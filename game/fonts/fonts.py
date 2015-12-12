#! /usr/bin/env python

import sys
import pygame
from pygame.locals import *


pygame.init()
pygame.font.init()
DISPLAYSURF = pygame.display.set_mode((400,300))
pygame.display.set_caption("Fonts!")


WHITE = (0xFF, 0xFF, 0xFF)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0x80)

fontObj = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObj = fontObj.render('Hello World!', True, GREEN, BLUE)
textRectObj = textSurfaceObj.get_rect()
textRectObj.center = (200, 150)

while True:
    DISPLAYSURF.fill(WHITE)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        pygame.display.update()
