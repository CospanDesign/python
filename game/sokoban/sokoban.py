#! /usr/bin/bash

import sys
import random
import copy
import os
import pygame
from pygame.local import *


FPS = 30
WINWIDTH = 800
WINHEIGHT = 600
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)


TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED = 5

OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE  =   (0x00, 0x9F, 0xFF)
WHITE       =   (0xFF, 0xFF, 0xFF)

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE


UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"


def main():
    global FPSCLOCK
    global DISPLAYSURF
    global IMAGESDICT
    global TILEMAPPING
    global OUTSIDEDECOMAPPING
    global BASICFONT
    global PLAYERIMAGES
    global current_image


    pygame.init()
    FPSCLOCK = pygame.time.Clock()


    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption("Star Pusher Guy")
    BASICFONT = pygame.font.Font("freesansbold.ttf", 18)

    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('princess.png'),
                  'boy': pygame.image.load('boy.png'),
                  'catgirl': pygame.image.load('catgirl.png'),
                  'horngirl': pygame.image.load('horngirl.png'),
                  'pinkgirl': pygame.image.load('pinkgirl.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}


    TILEMAPPING         = { "x": IMAGESDICT["corner"],
                            "#": IMAGESDICT["wall"],
                            "o": IMAGESDICT["inside floor"],
                            " ": IMAGESDICT["outside floor"]}
    OUTSIDEDECOMAPPING = {  "1": IMAGESDICT["rock"],
                            "2": IMAGESDICT["short tree"],
                            "3": IMAGESDICT["tall tree"],
                            "4": IMAGESDICT["ugly tree"]}

    PLAYERIMAGES = [IMAGESDICT["princess"],
                    IMAGESDICT["boy"],
                    IMAGESDICT["catgirl"],
                    IMAGESDICT["horngirl"],
                    IMAGESDICT["pinkgirl"]]

    start_screen()

    levels = readLevelsFile("startPusherLevels.txt")
    current_level_index = 0


    while True:
        result = run_level(levels, current_level_index)
        if result in ('solved', 'next'):
            current_level_index += 1
            if current_level_index >= (levels):
                #Done!
                current_level_index = 0
        elif result == 'back':
            current_level_index -= 1
            if current_level_index < 0:
                current_level_index = len(levels) - 1
        elif result == "reset":
            pass



def run_level(levels, level_num):
    global current_image
    level_obj = levels[level_num]
    map_obj = decorate_map(level_obj['mapObj'], level_obj['startState']['player'])
    game_state_obj = copy.deepcopy(level_obj['startState'])
    map_needs_redraw = True
    level_surf = BASICFONT.render("Level %s of %s" % (level_num + 1, len(levels,)), 1, TEXTCOLOR)
    level_rect = level_surf.get_rect()
    level_rect.bottomleft = (20, WINHEIGHT - 35)
    map_width = len(map_obj) * TILEWIDTH
    map_height = (len(map_obj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(map_height / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(map_height / 2)) + TILEWIDTH

    level_is_complete = False
    camera_offset_x = 0
    camera_offset_y = 0

    camera_up = False
    camera_down = False
    camera_left = False
    camera_right = False

    while True:
        player_move_to = None
        key_pressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                key_pressed = True
                if event.key == K_LEFT:
                    player_move_to = LEFT
                elif event.key == K_RIGHT:
                    player_move_to = RIGHT
                elif event.key == K_UP:
                    player_move_to = UP
                elif event.key == K_DOWN:
                    player_move_to = DOWN


                #Set the camera move mode
                elif event.key == K_a:
                    camera_left = True
                elif event.key == K_d:
                    cmaera_right = True
                elif event.key == K_w:
                    camera_up = True
                elif event.key == K_s:
                    camera_down = True

                elif event.key == K_n:
                    return "next"
                elif event.key == K_b:
                    return "back"

                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    current_image += 1
                    if current_image >= len(PLAYERIMAGES):
                        current_image = 0
                    map_needs_redraw = True

            elif event.type == KEYUP:
                if event.key == K_a:
                    camera_left = False
                elif event.key == K_d:
                    camera_right = False
                elif event.key == K_w:
                    camera_up = False
                elif event.key == K_s:
                    camera_down = False

        if player_move_to != None and not level_is_complete:
            moved = make_move(map_obj, game_state_obj, player_move_to)

            if moved:
                game_state_obj['stepCounter'] += 1
                map_needs_redraw = True

            if is_level_finished(level_obj, game_state_obj):
                level_is_complete = True
                key_pressed = False

        DISPLAYSURF.fill(BGCOLOR)

        if map_needs_redraw:
            map_surf = draw_map(map_obj, game_state_obj, level_obj['goals'])
            map_needs_redraw = False

        if camera_up and camera_offset_y < MAX_CAM_Y_PAN:
            camera_offset_y += CAM_MOVE_SPEED
        elif camera_down and camera_offset_y > -MAX_CAM_Y_PAN:
            camera_offset_y -= CAM_MOVE_SPEED
        
        if camera_left and camera_offset_x < MAX_CAM_X_PAN:
            camera_offset_x += CAM_MOVE_SPEED
        elif camera_right and camera_offset_x > -MAX_CAM_X_PAN:
            camera_offset_x -= CAM_MOVE_SPEED
            
        map_surf_rect = map_surf.get_rect()
        map_surf_rect.center = (HALF_WINWIDTH + camera_offset_x, HALF_WINHEIGHT + camera_offset_y)

        DISPLAYSURF.blit(map_surf, map_surf_rect)
        DISPLAYSURF.blit(level_surf, level_rect)
        step_surf = BASICFONT.render("Steps: %s" % (game_state_obj["stepCounter"]), 1, TEXTCOLOR)
        step_rect = step_surf.get_rect()
        step_rect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(step_surf, step_rect)

        if level_is_complete:
            #Show the solved image
            solved_rect = IMAGESDICT["solved"].get_rect()
            solved_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT["solved"], solved_rect)

            if key_pressed:
                return "solved"

        pygame.display.update()
        FPSCLOCK.tick()


def is_wall(map_obj, x, y):
    if x < 0 or x >= len(map_obj) or y < 0 or y >= len(map_obj[x]):
        return False
    elif map_obj[x][y] in ('#', 'x'):
        return True
    return False

def decorate_map(map_obj, startxy):
    startx = startxy
    starty = startxy

    map_obj_copy = copy.deepcopy(map_obj)

    for x in range(len(map_obj_copy)):
        for y in range(len(map_obj_copy[0])):
            if map_obj_copy[x][y] in ('$', '.', '@', '+', '*'):
                map_obj_copy = ' '

    flood_fill(map_obj_copy, startx, starty, ' ', 'o')


