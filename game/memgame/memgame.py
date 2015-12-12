#! /usr/bin/env python


import sys
import random
import pygame
from pygame.locals import *


FPS = 30 #30 FPS
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8
BOXSIZE = 40
GAPSIZE = 10
BOARDWIDTH = 10
BOARDHEIGHT = 7
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches'
XMARGIN = int((WINDOWWIDTH  - (BOARDWIDTH  * BOXSIZE + GAPSIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE + GAPSIZE)) / 2)


GRAY        = (0x7F, 0x7F, 0x7F)
NAVYBLUE    = (0x3F, 0x3F, 0x7F)
WHITE       = (0xFF, 0xFF, 0xFF)
RED         = (0xFF, 0x00, 0x00)
GREEN       = (0x00, 0xFF, 0x00)
BLUE        = (0x00, 0x00, 0xFF)
YELLOW      = (0xFF, 0xFF, 0x00)
ORANGE      = (0xFF, 0x7F, 0x00)
PURPLE      = (0xFF, 0x00, 0xFF)
CYAN        = (0x00, 0xFF, 0xFF)

BGCOLOR         = NAVYBLUE
LIGHTBGCOLOR    = GRAY
BOXCOLOR        = WHITE
HIGHLIGHTCOLOR  = BLUE


DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined"


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0
    mousey = 0
    pygame.display.set_caption("Memory Game 2000000")

    main_board = get_randomized_board()
    revealed_boxes = generate_revealed_boxes_data(False)
    #Store X and Y of the first box clicked
    first_selection = None

    DISPLAYSURF.fill(BGCOLOR)
    start_game_animation(main_board)

    while True:
        mouse_clicked = False
        #Setup the background
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(main_board, revealed_boxes)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouse_clicked = True

        boxx, boxy = get_box_at_pixel(mousex, mousey)
        if boxx != None and boxy != None:
            #Mouse is currently over a box
            if not revealed_boxes[boxx][boxy]:
                draw_highlighted_box(boxx, boxy)
            if not revealed_boxes[boxx][boxy] and mouse_clicked:
                reveal_boxes_animation(main_board, [(boxx, boxy)])
                #Mark that the box is revealed!
                revealed_boxes[boxx][boxy] = True

                if first_selection == None:
                    first_selection = (boxx, boxy)
                else:  #Check if there is a match between the two icons
                    icon1_shape, icon1_color = get_shape_and_color(main_board, first_selection[0], first_selection[1])
                    icon2_shape, icon2_color = get_shape_and_color(main_board, boxx, boxy)


                    if icon1_shape != icon2_shape or icon1_color != icon2_color:
                        #Icons don't match re-cover up both selection
                        pygame.time.wait(1000) # 1 second
                        cover_boxes_animation(main_board, [(first_selection[0], first_selection[1]), (boxx, boxy)])
                        revealed_boxes[first_selection[0]][first_selection[1]] = False
                        revealed_boxes[boxx][boxy] = False
                    elif has_won(revealed_boxes):
                        #Found Match!
                        game_won_animation(main_board)
                        pygame.time.wait(2000)

                        #Reset the board
                        main_board = get_randomized_board()
                        revealed_boxes = generate_revealed_boxes_data(False)

                        #Show the full unrevealed board for a second
                        draw_board(main_board, revealed_boxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        #Replay the start game animation
                        start_game_animation(main_board)
                    first_selection = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generate_revealed_boxes_data(val):
    revealed_boxes = []
    for i in range(BOARDWIDTH):
        revealed_boxes.append([val] * BOARDHEIGHT)
    return revealed_boxes

def get_randomized_board():
    #Get a list of every possible shape in every possible color
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape, color))

    #Randomize the order of the icons list
    random.shuffle(icons)
    #Find out how many icons are used
    num_icons_used = int(BOARDWIDTH * BOARDHEIGHT / 2)
    #Make two of each
    icons = icons[:num_icons_used] * 2
    random.shuffle(icons)


    #Create the board data structure with randomly placed icons
    board = []
    for x in range (BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            #We ate it now remove it from the base list
            del icons[0]

        board.append(column)
    return board


def split_into_groups_of(group_size, the_list):
    #Splits a list into a list of lists where the inner list have at most
    #Group size number of items

    result = []
    for i in range(0, len(the_list), group_size):
        result.append(the_list[i:i + group_size])
    return result

def left_top_coords_of_box(boxx, boxy):
    #Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def get_box_at_pixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range (BOARDHEIGHT):
            left, top = left_top_coords_of_box(boxx, boxy)
            box_rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if box_rect.collidepoint(x, y):
                return (boxx, boxy)

    return (None, None)

def draw_icon(shape, color, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)
    half = int(BOXSIZE * 0.5)

    #Get pixel coords from board coords
    left, top = left_top_coords_of_box(boxx, boxy)

    #Draw the shaped
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top+half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top+half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + 1))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))


def get_shape_and_color(board, boxx, boxy):
    #shape value for x, y spot is stored in board [x][y][0]
    #shape color for x, y spot is stored in board [x][y][1]
    return board[boxx][boxy][0], board[boxx][boxy][1]

def draw_box_covers(board, boxes, coverage):
    #Draws boxes being covered/revealed "boxes" is a list
    # of two-items lists, which have the same x and y spot of the box
    for box in boxes:
        left, top = left_top_coords_of_box(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        shape, color = get_shape_and_color(board, box[0], box[1])
        draw_icon(shape, color, box[0], box[1])
        if coverage > 0:
            #Only draw if there is a coverage on the box
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))

    pygame.display.update()
    FPSCLOCK.tick(FPS)

def reveal_boxes_animation(board, box_to_reveal):
    for coverage in range (BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        draw_box_covers(board, box_to_reveal, coverage)

def cover_boxes_animation(board, boxes_to_cover):
    for coverage in range (0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        draw_box_covers(board, boxes_to_cover, coverage)


def draw_board(board, revealed):
    #Draws all of the boxes in their covered or revealed state
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = left_top_coords_of_box(boxx, boxy)
            if not revealed[boxx][boxy]:
                #Draw a covered box
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                #Draw the revealed icon
                shape, color = get_shape_and_color(board, boxx, boxy)
                draw_icon(shape, color, boxx, boxy)

def draw_highlighted_box(boxx, boxy):
    left, top = left_top_coords_of_box(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def start_game_animation(board):
    #Randomly revela the boxes 8 at a time
    covered_boxes = generate_revealed_boxes_data(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    box_groups = split_into_groups_of(8, boxes)

    draw_board(board, covered_boxes)
    for bg in box_groups:
        reveal_boxes_animation(board, bg)
        cover_boxes_animation(board, bg)


def game_won_animation(board):
    #Flash the background color when the player has won
    covered_boxes = generate_revealed_boxes_data(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 #Swap colors
        DISPLAYSURF.fill(color1)
        draw_board(board, covered_boxes)
        pygame.display.update()
        pygame.time.wait(300)


def has_won(revealed_boxes):
    #Returns True if all the boxes have been revealed, otherwise false
    for i in revealed_boxes:
        if False in i:
            return False
    return True

if __name__ == '__main__':
    main()

