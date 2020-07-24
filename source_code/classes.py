import pygame
import sys
from math import *
import utils
import config


class Images:
    black_image = pygame.image.load("images/back_black.png")
    white_image = pygame.image.load("images/back_white.png")
    credits_image = pygame.image.load("images/credits.png")
    rook_image = "images/vesco.png"
    knight_image = "images/maggi.png"
    bishop_image = "images/gigi.png"
    queen_image = "images/camilla.png"
    king_image = "images/dozio.png"
    pawn_image = "images/guilizzoni.png"


pygame.mixer.init()
class Sounds:
    move_sound = pygame.mixer.Sound("sounds/move.wav")
    capture1_sound = pygame.mixer.Sound("sounds/capture1.wav")
    capture2_sound = pygame.mixer.Sound("sounds/capture2.wav")
    queen_capture_sound = pygame.mixer.Sound("sounds/queen_capture.wav")
    click_sound = pygame.mixer.Sound("sounds/mouse_click.wav")
    checkmate_sound = pygame.mixer.Sound("sounds/tada.wav")
    laugh_sound = pygame.mixer.Sound("sounds/laugh.wav")


class Tile(pygame.Rect):
    moves_dict = {}
    move_count = 0
    LIST = []
    WIDTH, HEIGHT = config.TILE_SIZE, config.TILE_SIZE
    TOT_TILES = 1
    EDGE_SX = range(1, 58, 8)
    EDGE_DX = range(8, 65, 8)

    def __init__(self, x, y):
        super().__init__(x, y, Tile.WIDTH, Tile.HEIGHT)
        self.number = Tile.TOT_TILES
        Tile.TOT_TILES += 1
        Tile.LIST.append(self)

    def text_to_screen(self, screen, size=15, color=(0, 0, 0), font_type="monospace"):
        font = pygame.font.SysFont(font_type, size)
        text = font.render(str(self.number), True, color)
        screen.blit(text, (self.x, self.y))

    @staticmethod
    def draw_tiles(screen):
        for tile in Tile.LIST:
            tile.text_to_screen(screen)

    @staticmethod
    def get_tile(number):
        for tile in Tile.LIST:
            if tile.number == number:
                return tile

    @staticmethod
    def gdbt(pn, tn):  # get distance between tiles
        t1 = Tile.get_tile(pn)
        t2 = Tile.get_tile(tn)
        if t2 is None:
            return -1
        return sqrt((t1.x - t2.x) ** 2 + (t1.y - t2.y) ** 2)


class GameController:
    isWhiteTurn = True
    piecesDict = {}

    def __init__(self):
        self.w = config.DISPLAY_WIDTH
        self.h = config.DISPLAY_HEIGHT
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(config.APP_NAME)

        # create tiles
        for y in range(0, self.screen.get_height(), Tile.WIDTH):
            for x in range(0, self.screen.get_width(), Tile.HEIGHT):
                Tile(x, y)

    def run(self):
        while True:
            self.screen.blit(config.MENU_IMAGE, (0, 0))

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
                        utils.play_game(self.screen)

            # render menu on screen
            self.display_menu()

    def display_menu(self):
        utils.display_text(self.screen, config.APP_NAME, self.w / 2, self.h / 5, 80)
        # utils.display_text(screen,"Author: Emanuele Bolognesi",115,580,15)
        utils.create_button(self.screen, "Play",
                            self.w / 2 - 50, self.h / 2 - 75, 100, 50,
                            config.BUTTON_COLOR,
                            config.BUTTON_COLOR_BRIGHT,
                            "play_game")
        utils.create_button(self.screen, "Keys",
                            self.w / 2 - 50, self.h / 2, 100, 50,
                            config.BUTTON_COLOR,
                            config.BUTTON_COLOR_BRIGHT,
                            "open_keys_page")
        utils.create_button(self.screen, "Info",
                            self.w / 2 - 50, self.h / 2 + 75, 100, 50,
                            config.BUTTON_COLOR,
                            config.BUTTON_COLOR_BRIGHT,
                            "open_info_page")
        utils.create_button(self.screen, "Quit",
                            self.w / 2 - 50, self.h / 2 + 150, 100, 50,
                            config.BUTTON_COLOR,
                            config.BUTTON_COLOR_BRIGHT,
                            "quit")
        pygame.display.flip()