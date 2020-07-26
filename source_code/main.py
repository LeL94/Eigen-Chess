# TODO:
# save game state as dictionary of piece objects and gamecontroller
# add unit tests
# bug: en passant after undo_move()
# bug: undo_move() after pawn promotion


# Author: Emanuele Bolognesi

import pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

from classes import GameController


if __name__ == '__main__':
    gc = GameController()
    gc.run()