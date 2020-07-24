# Author: Emanuele Bolognesi

import pygame, sys
import utils
import config
from classes import *

pygame.init()
pygame.font.init()

w = config.DISPLAY_WIDTH
h = config.DISPLAY_HEIGHT
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption(config.APP_NAME)

menuImage = pygame.image.load("images/menu_t.jpg")

# colors
backgroundColor = (255, 255, 102)
buttonColor = (153, 76, 0)
buttonColorBright = (204, 102, 0)

# create tiles
for y in range(0, screen.get_height(), Tile.WIDTH):
    for x in range(0, screen.get_width(), Tile.HEIGHT):
        Tile(x, y)

# starting menu
while True:
    screen.blit(menuImage, (0, 0))

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
                utils.play_game(screen)

    utils.text_display(screen, config.APP_NAME, w / 2, h / 5, 80)
    # utils.text_display(screen,"Author: Emanuele Bolognesi",115,580,15)
    utils.create_button(screen, "Play", w / 2 - 50, h / 2 - 75, 100, 50, buttonColor, buttonColorBright, "play_game")
    utils.create_button(screen, "Keys", w / 2 - 50, h / 2, 100, 50, buttonColor, buttonColorBright, "open_keys_page")
    utils.create_button(screen, "Info", w / 2 - 50, h / 2 + 75, 100, 50, buttonColor, buttonColorBright, "open_info_page")
    utils.create_button(screen, "Quit", w / 2 - 50, h / 2 + 150, 100, 50, buttonColor, buttonColorBright, "quit")

    pygame.display.flip()

# TODO:
# bug: en passant after undo_move()
# bug: undo_move() after pawn promotion
