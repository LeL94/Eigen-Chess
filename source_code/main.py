# TODO:
# add unit tests
# bug: en passant after undo_move()
# bug: undo_move() after pawn promotion


# Author: Emanuele Bolognesi

import pygame, sys
import utils
import config
from classes import GameController


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()

    gc = GameController()
    gc.run()