
# Author: Emanuele Bolognesi

import pygame, sys, functions
from classes import *


pygame.init()
pygame.font.init()

display_width = 600
display_height = 600
screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("EigenChess")

menuImage = pygame.image.load("images/menu_t.jpg")


# colors
backgroundColor = (255,255,102)
buttonColor = (153,76,0)
buttonColorBright = (204,102,0)

# create tiles
for y in range(0,screen.get_height(),Tile.WIDTH):
    for x in range(0,screen.get_width(),Tile.HEIGHT):
        Tile(x,y)


# starting menu
while True:
    screen.blit(menuImage,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_RETURN:
                Sounds.click_sound.play()
                pygame.time.wait(250)
                functions.play_game(screen)

    #screen.fill(backgroundColor)

    title = "EigenChess"
    functions.text_display(screen,title,display_width/2,display_height/5,80)
    author = "Author: Emanuele Bolognesi"
    #functions.text_display(screen,author,115,580,15)
    functions.button(screen,"Play",display_width/2-50,display_height/2-75,100,50,buttonColor,buttonColorBright,"play_game")
    functions.button(screen,"Keys",display_width/2-50,display_height/2,100,50,buttonColor,buttonColorBright,"legend")
    functions.button(screen,"Info",display_width/2-50,display_height/2+75,100,50,buttonColor,buttonColorBright,"credits")
    functions.button(screen,"Quit",display_width/2-50,display_height/2+150,100,50,buttonColor,buttonColorBright,"quit")

    pygame.display.flip()



# TODO:
# bug: en passant after undo_move()
# bug: undo_move() after pawn promotion
# credits
