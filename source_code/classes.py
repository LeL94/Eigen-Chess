import pygame
import sys
from math import *
import config
from random import randint


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


class Sounds:
    move_sound = pygame.mixer.Sound("sounds/move.wav")
    capture1_sound = pygame.mixer.Sound("sounds/capture1.wav")
    capture2_sound = pygame.mixer.Sound("sounds/capture2.wav")
    queen_capture_sound = pygame.mixer.Sound("sounds/queen_capture.wav")
    click_sound = pygame.mixer.Sound("sounds/mouse_click.wav")
    checkmate_sound = pygame.mixer.Sound("sounds/tada.wav")
    laugh_sound = pygame.mixer.Sound("sounds/laugh.wav")


class Tile(pygame.Rect):
    LIST = []
    WIDTH, HEIGHT = config.TILE_SIZE, config.TILE_SIZE
    TOT_TILES = 1
    EDGE_SX = range(1, 58, 8)
    EDGE_DX = range(8, 65, 8)

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
    def get_distance_between_tiles(pn, tn):
        t1 = Tile.get_tile(pn)
        t2 = Tile.get_tile(tn)
        if t2 is None:
            return -1
        return sqrt((t1.x - t2.x) ** 2 + (t1.y - t2.y) ** 2)

    @staticmethod
    def get_tile_number_from_coord(x, y):
        return int(x + y * 8 + 1)

    def __init__(self, x, y):
        super().__init__(x, y, Tile.WIDTH, Tile.HEIGHT)
        self.number = Tile.TOT_TILES
        Tile.TOT_TILES += 1
        Tile.LIST.append(self)

    def text_to_screen(self, screen, size=15, color=(0, 0, 0), font_type="monospace"):
        font = pygame.font.SysFont(font_type, size)
        text = font.render(str(self.number), True, color)
        screen.blit(text, (self.x, self.y))


class GameController:
    isWhiteTurn = True
    piecesDict = {}

    # to undo/redo moves
    moves_dict = {}
    move_count = 0

    @staticmethod
    def get_white_king(piecesDict):  # get white king
        for piece in piecesDict.values():
            if piece.type == "king" and piece.color == "white":
                return piece

    @staticmethod
    def get_black_king(piecesDict):  # get black king
        for piece in piecesDict.values():
            if piece.type == "king" and piece.color == "black":
                return piece

    @staticmethod
    def get_white_controlled_tiles(piecesDict):  # get white controlled tiles
        wct = []
        for piece in piecesDict.values():
            if piece.color == "white":
                wct += piece.gct(piecesDict)
        return wct

    @staticmethod
    def get_black_controlled_tiles(piecesDict):  # get black controlled tiles
        bct = []
        for piece in piecesDict.values():
            if piece.color == "black":
                bct += piece.gct(piecesDict)
        return bct

    @staticmethod
    def check_if_white_checkmate():
        for piece in GameController.piecesDict.values():
            if piece.color == "white":
                for tile in Tile.LIST:
                    if piece.move(tile, GameController.piecesDict, False):
                        return
        Sounds.checkmate_sound.play()
        wking = GameController.get_white_king(GameController.piecesDict)
        if wking.check(GameController.piecesDict):
            wking.image = pygame.image.load("images/king_skull.png")

    @staticmethod
    def check_if_black_checkmate():
        for piece in GameController.piecesDict.values():
            if piece.color == "black":
                for tile in Tile.LIST:
                    if piece.move(tile, GameController.piecesDict, False):
                        return
        Sounds.checkmate_sound.play()
        bking = GameController.get_black_king(GameController.piecesDict)
        if bking.check(GameController.piecesDict):
            bking.image = pygame.image.load("images/king_skull.png")

    def __init__(self):
        self.w = config.DISPLAY_WIDTH
        self.h = config.DISPLAY_HEIGHT
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(config.APP_NAME)

        self.game_loop = False
        self.keys_page_loop = False

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
                        pygame.time.wait(config.GUI_DELAY)
                        self.play_game()
            # render menu on screen
            self.display_menu()

    def display_menu(self):
        self.display_text(self.w / 2, self.h / 5, config.APP_NAME, 80)
        # utils.display_text(115,580,screen,"Author: Emanuele Bolognesi",15)
        self.create_button(self.w / 2 - config.BUTTON_WIDTH / 2, self.h / 2 - 75, "Play", "play_game")
        self.create_button(self.w / 2 - config.BUTTON_WIDTH / 2, self.h / 2, "Keys", "open_keys_page")
        self.create_button(self.w / 2 - config.BUTTON_WIDTH / 2, self.h / 2 + 75, "Info", "open_info_page")
        self.create_button(self.w / 2 - config.BUTTON_WIDTH / 2, self.h / 2 + 150, "Quit", "quit")
        pygame.display.flip()

    def play_game(self):
        self.new_game()
        chessboard = pygame.image.load("images/chessboard.png")
        self.game_loop = True
        while self.game_loop:
            # check pawn promotion
            for piece in GameController.piecesDict.values():
                # TODO check in Pawn move method
                if piece.type == "pawn" and piece.get_tile_number() in config.PROMOTION_TILES:
                    piece.promotion()

            self.screen.blit(chessboard, (0, 0))
            self.listen_events()

            # draw pieces
            for piece in GameController.piecesDict.values():
                piece.draw_image(self.screen)

            # get kings
            wking = GameController.get_white_king(GameController.piecesDict)
            bking = GameController.get_black_king(GameController.piecesDict)

            aux = {}
            for piece in GameController.piecesDict.values():
                aux[piece.get_tile_number()] = piece
            aux[0] = Auxpiece(-1, -1, "", "")

            wtc = []  # white tiles controlled
            btc = []  # white tiles controlled
            for piece in GameController.piecesDict.values():
                if piece.color == "white":
                    wtc += piece.gct(GameController.piecesDict)
                elif piece.color == "black":
                    btc += piece.gct(GameController.piecesDict)

            # color the king with red if under check
            if wking.check(aux) or wking.get_tile_number() in btc:
                pygame.draw.rect(self.screen, config.CHECK_COLOR, (wking.x, wking.y, wking.width, wking.height), 4)
            if bking.check(aux) or bking.get_tile_number() in wtc:
                pygame.draw.rect(self.screen, config.CHECK_COLOR, (bking.x, bking.y, bking.width, bking.height), 4)

            # draw allowed tiles cursor
            for piece in GameController.piecesDict.values():
                if piece.selected:
                    pygame.draw.rect(self.screen, config.ALLOWED_TILE_COLOR,
                                     (piece.x, piece.y, piece.width, piece.height), 4)
                    for tile in Tile.LIST:
                        if piece.move(tile, GameController.piecesDict, False):
                            pygame.draw.circle(self.screen, config.ALLOWED_TILE_COLOR,
                                               (tile.x + int(config.TILE_SIZE / 2), tile.y + int(config.TILE_SIZE / 2)), 8)

            pygame.display.flip()

    def create_button(self, x, y, text, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        w, h = config.BUTTON_WIDTH, config.BUTTON_HEIGHT
        ic, ac = config.BUTTON_COLOR, config.BUTTON_COLOR_BRIGHT

        if x < mouse[0] < x + w and y < mouse[1] < y + h:
            pygame.draw.rect(self.screen, ac, (x, y, w, h))
            if click[0] == 1:
                if action == "play_game":
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    self.play_game()
                elif action == "open_keys_page":
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    self.open_keys_page()
                elif action == "open_info_page":
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    self.open_info_page()
                elif action == "quit":
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    pygame.quit()
                    sys.exit()
                elif action == "back":
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    self.keys_page_loop = False
        else:
            pygame.draw.rect(self.screen, ic, (x, y, w, h))

        textSurf, textRect = self.text_objects(text, 30)
        textRect.center = (x + w / 2, y + h / 2)
        self.screen.blit(textSurf, textRect)

    def open_info_page(self):
        credits_loop = True
        while credits_loop:
            for event in pygame.event.get():
                # exit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # mouse
                elif event.type == pygame.KEYUP:
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    credits_loop = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    credits_loop = False

            self.screen.blit(Images.credits_image, (0, 0))

            pygame.display.flip()

    def open_keys_page(self):
        legendImage = pygame.image.load("images/legend.png")
        self.keys_page_loop = True
        while self.keys_page_loop:
            for event in pygame.event.get():
                # exit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # mouse
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_BACKSPACE:
                        Sounds.click_sound.play()
                        pygame.time.wait(config.GUI_DELAY)
                        self.keys_page_loop = False

            self.screen.blit(legendImage, (0, 0))
            self.create_button(self.w / 2 - config.BUTTON_WIDTH / 2, 80, "Back", "back")

            pygame.display.flip()

    def text_objects(self, text, fontSize):
        font = pygame.font.Font("freesansbold.ttf", fontSize)
        textSurface = font.render(text, True, (0, 0, 0))
        return textSurface, textSurface.get_rect()

    def display_text(self, x, y, text, fontSize):
        TextSurf, TextRect = self.text_objects(text, fontSize)
        TextRect.center = (x, y)
        self.screen.blit(TextSurf, TextRect)

    def listen_events(self):
        for event in pygame.event.get():
            # exit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.move_piece()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.new_game()
                elif event.key == pygame.K_BACKSPACE:
                    Sounds.click_sound.play()
                    pygame.time.wait(config.GUI_DELAY)
                    self.game_loop = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_LEFT:
                    self.undo_move()
                elif event.key == pygame.K_RIGHT:
                    self.repeat_move()

    def move_piece(self):
        Mpos = pygame.mouse.get_pos()  # [x,y]
        Mx = floor(Mpos[0] / Tile.WIDTH)
        My = floor(Mpos[1] / Tile.HEIGHT)
        clickedTileNumber = Tile.get_tile_number_from_coord(Mx, My)
        tile = Tile.get_tile(clickedTileNumber)

        for piece in GameController.piecesDict.values():
            # if there is a piece selected, move that piece
            if piece.selected:
                piece.selected = False

                # if the selected piece can not move, return
                if not piece.move(tile, GameController.piecesDict):
                    return

                # remove piece from dictionary
                del GameController.piecesDict[piece.get_tile_number()]

                # change piece position
                piece.x, piece.y = tile.x, tile.y
                piece.initial_pos = False

                # if there is already a piece, destroy it
                if tile.number in GameController.piecesDict.keys():
                    if Piece.get_piece(tile.number).type == "queen":
                        Sounds.queen_capture_sound.play()
                    else:
                        male_grunt = randint(1, 2)
                        if male_grunt == 1:
                            Sounds.capture1_sound.play()
                        elif male_grunt == 2:
                            Sounds.capture2_sound.play()

                    del GameController.piecesDict[tile.number]
                else:
                    Sounds.move_sound.play()

                # add piece to dictionary (it will be in the new position)
                GameController.piecesDict[tile.number] = piece

                GameController.move_count += 1
                self.save_moves()

                # change turn
                if GameController.isWhiteTurn:
                    GameController.isWhiteTurn = False
                    for piece in GameController.piecesDict.values():  # en passant capture decays
                        if piece.type == "pawn" and piece.color == "black":
                            if piece.double_step:
                                piece.double_step = False
                    GameController.check_if_black_checkmate()  # check if checkmate or draw
                else:
                    GameController.isWhiteTurn = True
                    for piece in GameController.piecesDict.values():  # en passant capture decays
                        if piece.type == "pawn" and piece.color == "white":
                            if piece.double_step:
                                piece.double_step = False
                    GameController.check_if_white_checkmate()  # check if checkmate or draw
                return
            else:
                # if there is not a piece selected, select a piece if there is one
                if piece.get_tile_number() == tile.number:
                    if GameController.isWhiteTurn and piece.color == "white":
                        piece.selected = True
                    elif not GameController.isWhiteTurn and piece.color == "black":
                        piece.selected = True
                    else:
                        piece.selected = False
                    return

    def save_moves(self):
        aux_dict = {}
        for piece in GameController.piecesDict.values():
            if piece.type == "king":
                aux_piece = King(piece.x, piece.y, Images.king_image, piece.type, piece.color, False)
            elif piece.type == "pawn":
                aux_piece = Pawn(piece.x, piece.y, Images.pawn_image, piece.type, piece.color, False)
            elif piece.type == "knight":
                aux_piece = Knight(piece.x, piece.y, Images.knight_image, piece.type, piece.color, False)
            elif piece.type == "bishop":
                aux_piece = Bishop(piece.x, piece.y, Images.bishop_image, piece.type, piece.color, False)
            elif piece.type == "rook":
                aux_piece = Rook(piece.x, piece.y, Images.rook_image, piece.type, piece.color, False)
            elif piece.type == "queen":
                aux_piece = Queen(piece.x, piece.y, Images.queen_image, piece.type, piece.color, False)
            else:
                aux_piece = None
                raise RuntimeError
            aux_dict[aux_piece.get_tile_number()] = aux_piece

        GameController.moves_dict[GameController.move_count] = aux_dict

        # if make a different move after undo_move(), delete all moves in the "future"
        for i in GameController.moves_dict.keys():
            if i > GameController.move_count:
                del GameController.moves_dict[i]

    def undo_move(self):
        try:
            aux_dict = {}
            for piece in GameController.moves_dict[GameController.move_count - 1].values():
                aux_dict[piece.get_tile_number()] = piece

            GameController.move_count -= 1
            GameController.piecesDict.clear()

            for piece in aux_dict.values():
                if piece.type == "king":
                    King(piece.x, piece.y, Images.king_image, piece.type, piece.color)
                elif piece.type == "pawn":
                    Pawn(piece.x, piece.y, Images.pawn_image, piece.type, piece.color)
                elif piece.type == "knight":
                    Knight(piece.x, piece.y, Images.knight_image, piece.type, piece.color)
                elif piece.type == "bishop":
                    Bishop(piece.x, piece.y, Images.bishop_image, piece.type, piece.color)
                elif piece.type == "rook":
                    Rook(piece.x, piece.y, Images.rook_image, piece.type, piece.color)
                elif piece.type == "queen":
                    Queen(piece.x, piece.y, Images.queen_image, piece.type, piece.color)

            GameController.isWhiteTurn = not GameController.isWhiteTurn

        except KeyError:
            self.new_game(False)

    def repeat_move(self):
        try:
            aux_dict = {}
            for piece in GameController.moves_dict[GameController.move_count + 1].values():
                aux_dict[piece.get_tile_number()] = piece

            GameController.move_count += 1
            GameController.piecesDict.clear()

            for piece in aux_dict.values():
                if piece.type == "king":
                    King(piece.x, piece.y, Images.king_image, piece.type, piece.color)
                elif piece.type == "pawn":
                    Pawn(piece.x, piece.y, Images.pawn_image, piece.type, piece.color)
                elif piece.type == "knight":
                    Knight(piece.x, piece.y, Images.knight_image, piece.type, piece.color)
                elif piece.type == "bishop":
                    Bishop(piece.x, piece.y, Images.bishop_image, piece.type, piece.color)
                elif piece.type == "rook":
                    Rook(piece.x, piece.y, Images.rook_image, piece.type, piece.color)
                elif piece.type == "queen":
                    Queen(piece.x, piece.y, Images.queen_image, piece.type, piece.color)

            GameController.isWhiteTurn = not GameController.isWhiteTurn

        except KeyError:
            print("No other moves to repeat")
            return

    def new_game(self, restart=True):
        GameController.piecesDict.clear()
        GameController.isWhiteTurn = True
        GameController.move_count = 0

        if restart:
            print("new game")
            GameController.moves_dict.clear()

        self.create_pieces()

    def create_pieces(self):
        # Pawn(0, 1 * Tile.HEIGHT, Images.pawn_image, "pawn", "white")
        # Pawn(0, 6 * Tile.HEIGHT, Images.pawn_image, "pawn", "black")
        #
        # King(4 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.king_image, "king", "white")
        # King(4 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.king_image, "king", "black")
        # return

        # White
        Rook(0 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.rook_image, "rook", "white")
        Knight(1 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.knight_image, "knight", "white")
        Bishop(2 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.bishop_image, "bishop", "white")
        Queen(3 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.queen_image, "queen", "white")
        King(4 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.king_image, "king", "white")
        Bishop(5 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.bishop_image, "bishop", "white")
        Knight(6 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.knight_image, "knight", "white")
        Rook(7 * Tile.WIDTH, 7 * Tile.HEIGHT, Images.rook_image, "rook", "white")
        for i in range(0, 8):
            Pawn(i * Tile.WIDTH, 6 * Tile.HEIGHT, Images.pawn_image, "pawn", "white")

        # Black
        Rook(0 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.rook_image, "rook", "black")
        Knight(1 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.knight_image, "knight", "black")
        Bishop(2 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.bishop_image, "bishop", "black")
        Queen(3 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.queen_image, "queen", "black")
        King(4 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.king_image, "king", "black")
        Bishop(5 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.bishop_image, "bishop", "black")
        Knight(6 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.knight_image, "knight", "black")
        Rook(7 * Tile.WIDTH, 0 * Tile.HEIGHT, Images.rook_image, "rook", "black")
        for i in range(0, 8):
            Pawn(i * Tile.WIDTH, 1 * Tile.HEIGHT, Images.pawn_image, "pawn", "black")


class Piece(pygame.Rect):
    aux_piece = False

    @staticmethod
    def get_piece(number):
        for piece in GameController.piecesDict.values():
            if piece.get_tile_number() == number:
                return piece

    @staticmethod
    def cicam(moving_piece, future_tile):  # check if check after move
        # create auxiliary dictionary
        aux_dict = {}
        for piece in GameController.piecesDict.values():
            aux_dict[piece.get_tile_number()] = piece

        # remove moving piece from auxiliary dictionary
        del aux_dict[moving_piece.get_tile_number()]
        if future_tile.number in aux_dict.keys():
            del aux_dict[future_tile.number]

        # create auxiliary piece in new position
        aux_piece = Auxpiece(future_tile.x, future_tile.y, moving_piece.type, moving_piece.color)

        # add auxiliary piece to auxiliary dictionary
        aux_dict[aux_piece.get_tile_number()] = aux_piece

        wking = GameController.get_white_king(aux_dict)
        bking = GameController.get_black_king(aux_dict)

        # if king under check, return True
        if moving_piece.color == "white":
            if wking.check(aux_dict):
                return True
            else:
                return False
        elif moving_piece.color == "black":
            if bking.check(aux_dict):
                return True
            else:
                return False

    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        super().__init__(x, y, Tile.WIDTH, Tile.HEIGHT)
        self.image = pygame.image.load(image)
        self.selected = False
        if real_piece:
            GameController.piecesDict[self.get_tile_number()] = self
        self.type = piece_type
        self.color = color
        self.initial_pos = True
        if self.type == "pawn":
            if self.color == "white" and self.get_tile_number() not in (49, 50, 51, 52, 53, 54, 55, 56):
                self.initial_pos = False
            elif self.color == "black" and self.get_tile_number() not in (9, 10, 11, 12, 13, 14, 15, 16):
                self.initial_pos = False

    def gct(self, allPieces):
        return []

    def draw_image(self, screen):
        if self.color == "white":
            screen.blit(Images.white_image, (self.x, self.y))
        else:
            screen.blit(Images.black_image, (self.x, self.y))
        screen.blit(self.image, (self.x, self.y))

    def get_tile_number(self):
        return Tile.get_tile_number_from_coord(self.x/Tile.WIDTH, self.y/Tile.HEIGHT)

    def __str__(self):
        res = "Piece: " + self.type + "\nColor: " + self.color + "\nNumber: " + str(self.get_tile_number())
        res += "\nx: " + str(self.x) + "\ny: " + str(self.y)
        return res


class King(Piece):
    castle = False

    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def check(self, all_pieces):
        pn = self.get_tile_number()

        wct = GameController.get_white_controlled_tiles(all_pieces)
        bct = GameController.get_black_controlled_tiles(all_pieces)

        if self.color == "white" and pn in bct:
            return True
        elif self.color == "black" and pn in wct:
            return True
        else:
            return False

    def move(self, t, all_pieces, real_move=True):
        # real move is necessary to avoid undesired castle (because of allowed moves cicle)
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()

        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        if Tile.get_distance_between_tiles(pn, tn) > 151:
            return False

        # check if check after move
        if Piece.cicam(p, t):
            return False

        # the king can't move on tiles controlled by opposite color
        wtc = []  # white tiles controlled
        btc = []  # white tiles controlled
        for piece in all_pieces.values():
            if piece.color == "white":
                wtc += piece.gct(all_pieces)
            elif piece.color == "black":
                btc += piece.gct(all_pieces)
        if p.color == "white" and tn in btc:
            return False
        elif p.color == "black" and tn in wtc:
            return False

        # white king castle moves
        if p.initial_pos and p.color == "white" and not p.get_tile_number() in btc:
            if tn == pn + 2 and pn + 1 not in keys and pn + 1 not in btc:
                wrook = Piece.get_piece(64)
                if wrook is None:
                    return False
                elif not wrook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, short castle
                        del GameController.piecesDict[wrook.get_tile_number()]
                        wrook.x = 5 * Tile.WIDTH
                        GameController.piecesDict[wrook.get_tile_number()] = wrook
                        wrook.initial_pos = False
                    return True
            elif tn == pn - 2 and pn - 1 not in keys and pn - 3 not in keys and pn - 1 not in btc:
                wrook = Piece.get_piece(57)
                if wrook is None:
                    return False
                elif not wrook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, long castle
                        del GameController.piecesDict[wrook.get_tile_number()]
                        wrook.x = 3 * Tile.WIDTH
                        GameController.piecesDict[wrook.get_tile_number()] = wrook
                        wrook.initial_pos = False
                    return True
        # black king castle moves
        if p.initial_pos and p.color == "black" and not p.get_tile_number() in wtc:
            if tn == pn + 2 and pn + 1 not in keys and pn + 1 not in wtc:
                brook = Piece.get_piece(8)
                if brook is None:
                    return False
                elif not brook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, short castle
                        del GameController.piecesDict[brook.get_tile_number()]
                        brook.x = 5 * Tile.WIDTH
                        GameController.piecesDict[brook.get_tile_number()] = brook
                        brook.initial_pos = False
                    return True
            elif tn == pn - 2 and pn - 1 not in keys and pn - 3 not in keys and pn - 1 not in wtc:
                brook = Piece.get_piece(1)
                if brook is None:
                    return False
                elif not brook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, long castle
                        del GameController.piecesDict[brook.get_tile_number()]
                        brook.x = 3 * Tile.WIDTH
                        GameController.piecesDict[brook.get_tile_number()] = brook
                        brook.initial_pos = False
                    return True
        # standard king moves
        if tn in (pn - 8 - 1, pn - 8, pn - 8 + 1, pn + 1, pn + 8 + 1, pn + 8, pn + 8 - 1, pn - 1):
            return True
        else:
            return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        controlled_tiles = [pn - 8 - 1, pn - 8, pn - 8 + 1, pn + 1, pn + 8 + 1, pn + 8, pn + 8 - 1, pn - 1]
        if pn in Tile.EDGE_SX:
            controlled_tiles.remove(pn - 8 - 1)
            controlled_tiles.remove(pn + 8 - 1)
            controlled_tiles.remove(pn - 1)
        elif pn in Tile.EDGE_DX:
            controlled_tiles.remove(pn - 8 + 1)
            controlled_tiles.remove(pn + 8 + 1)
            controlled_tiles.remove(pn + 1)
        ct = []
        for i in controlled_tiles:
            ct.append(i)
        for i in ct:
            if i < 1 or i > 64:
                controlled_tiles.remove(i)
        return controlled_tiles


class Pawn(Piece):
    double_step = False

    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def promotion(self):
        del GameController.piecesDict[self.get_tile_number()]
        Queen(self.x, self.y, Images.queen_image, "queen", self.color)
        if self.color == "white":
            GameController.check_if_black_checkmate()
        elif self.color == "black":
            GameController.check_if_white_checkmate()

    def en_passant(self, tn, real_move):
        pn = self.get_tile_number()
        if self.color == "white":
            if pn == 25:
                try:
                    if Piece.get_piece(26).double_step and tn == 18:
                        if real_move:
                            Sounds.laugh_sound.play()
                            del GameController.piecesDict[26]
                        return True
                except:
                    pass
            elif pn == 32:
                try:
                    if Piece.get_piece(31).double_step and tn == 23:
                        if real_move:
                            Sounds.laugh_sound.play()
                            del GameController.piecesDict[31]
                        return True
                except:
                    pass
            elif pn in (26, 27, 28, 29, 30, 31):
                for number in (26, 27, 28, 29, 30, 31):
                    try:
                        if Piece.get_piece(number - 1).double_step and tn == number - 1 - 8:
                            if real_move:
                                Sounds.laugh_sound.play()
                                del GameController.piecesDict[number - 1]
                            return True
                    except:
                        pass
                    try:
                        if Piece.get_piece(number + 1).double_step and tn == number + 1 - 8:
                            if real_move:
                                Sounds.laugh_sound.play()
                                del GameController.piecesDict[number + 1]
                            return True
                    except:
                        pass
        elif self.color == "black":
            if pn == 33:
                try:
                    if Piece.get_piece(34).double_step and tn == 42:
                        if real_move:
                            Sounds.laugh_sound.play()
                            del GameController.piecesDict[34]
                        return True
                except:
                    pass
            elif pn == 40:
                try:
                    if Piece.get_piece(39).double_step and tn == 47:
                        if real_move:
                            Sounds.laugh_sound.play()
                            del GameController.piecesDict[39]
                        return True
                except:
                    pass
            elif pn in (34, 35, 36, 37, 38, 39):
                for number in (34, 35, 36, 37, 38, 39):
                    try:
                        if Piece.get_piece(number - 1).double_step and tn == number - 1 + 8:
                            if real_move:
                                Sounds.laugh_sound.play()
                                del GameController.piecesDict[number - 1]
                            return True
                    except:
                        pass
                    try:
                        if Piece.get_piece(number + 1).double_step and tn == number + 1 + 8:
                            if real_move:
                                Sounds.laugh_sound.play()
                                del GameController.piecesDict[number + 1]
                            return True
                    except:
                        pass
        return False

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number  # clicked tile number

        keys = all_pieces.keys()
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        if Tile.get_distance_between_tiles(pn, tn) > 151:
            return False

        # check if check after move
        if Piece.cicam(p, t):
            return False

        if self.en_passant(tn, real_move):
            return True

        # allowed moves
        if p.color == "white":
            if p.initial_pos and (tn == pn - 16) and (tn not in keys):
                tow = pn - 8
                if tow not in keys:
                    self.double_step = True
                    return True
            elif (tn == pn - 8) and (tn not in keys):
                return True
            elif tn in (pn - 8 + 1, pn - 8 - 1) and (tn in keys):
                return True
            else:
                return False
        elif p.color == "black":
            if p.initial_pos and (tn == pn + 16) and (tn not in keys):
                tow = pn + 8
                if tow not in keys:
                    self.double_step = True
                    return True
            elif (tn == pn + 8) and (tn not in keys):
                return True
            elif tn in (pn + 8 - 1, pn + 8 + 1) and (tn in keys):
                return True
            else:
                return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        if self.color == "white":
            controlled_tiles = [pn - 8 - 1, pn - 8 + 1]
            if pn in Tile.EDGE_SX:
                controlled_tiles.remove(pn - 8 - 1)
            elif pn in Tile.EDGE_DX:
                controlled_tiles.remove(pn - 8 + 1)
        else:
            controlled_tiles = [pn + 8 - 1, pn + 8 + 1]
            if pn in Tile.EDGE_SX:
                controlled_tiles.remove(pn + 8 - 1)
            elif pn in Tile.EDGE_DX:
                controlled_tiles.remove(pn + 8 + 1)
        return controlled_tiles


class Knight(Piece):
    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False
        # check if check after move
        if Piece.cicam(p, t):
            return False

        if Tile.get_distance_between_tiles(pn, tn) > 170:
            return False
        elif tn in (pn - 16 - 1, pn - 16 + 1, pn + 16 - 1, pn + 16 + 1, pn - 8 - 2, pn - 8 + 2, pn + 8 - 2, pn + 8 + 2):
            return True

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        controlled_tiles = [pn - 16 - 1, pn - 16 + 1, pn + 16 - 1, pn + 16 + 1, pn - 8 - 2, pn - 8 + 2, pn + 8 - 2,
                            pn + 8 + 2]
        ct = []
        for i in controlled_tiles:
            ct.append(i)
        for i in ct:
            distance = Tile.get_distance_between_tiles(pn, i)
            if i < 1 or i > 64 or distance > 170 or distance == -1:
                controlled_tiles.remove(i)
        return controlled_tiles


class Rook(Piece):
    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        # check if check after move
        if Piece.cicam(p, t):
            return False

        if abs(pn - tn) % 8 == 0:
            # tiles on way
            if tn < pn:
                tow = range(pn - 8, tn, -8)
            elif tn > pn:
                tow = range(pn + 8, tn, 8)
            else:
                tow = []
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        # horizontal movement
        elif t.y == p.y:
            # tiles on way
            if tn < pn:
                tow = range(pn - 1, tn, -1)
            elif tn > pn:
                tow = range(pn + 1, tn, 1)
            else:
                tow = []
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        else:
            return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        ct1 = range(pn - 8, 0, -8)
        for tile in ct1:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct1 = range(pn - 8, tile - 8, -8)
                break
        ct2 = range(pn + 8, 65, 8)
        for tile in ct2:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct2 = range(pn + 8, tile + 8, 8)
                break
        ct3 = range(pn - 1, 0, -1)
        for tile in ct3:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct3 = range(pn - 1, tile - 1, -1)
                break
        ct4 = range(pn + 1, 65, 1)
        for tile in ct4:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct4 = range(pn + 1, tile + 1, 1)
                break
        controlled_tiles = list(ct1) + list(ct2) + list(ct3) + list(ct4)
        ct = []
        for i in controlled_tiles:
            ct.append(i)
        for i in ct:
            tile = Tile.get_tile(i)
            if tile.y != self.y and (abs(i - pn)) % 8 != 0:
                controlled_tiles.remove(i)
        return controlled_tiles


class Bishop(Piece):
    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        distance = Tile.get_distance_between_tiles(pn, tn)
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        # check if check after move
        if Piece.cicam(p, t):
            return False

        # anti-diagonal movement
        if abs(tn - pn) % 7 == 0:
            if tn < pn:
                tow = range(pn - 7, tn, -7)
            elif tn > pn:
                tow = range(pn + 7, tn, 7)
            else:
                tow = []
            allowed_distance = (len(tow) + 1) * sqrt(2) * Tile.WIDTH
            if distance != allowed_distance:
                return False
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        # diagonal movement
        elif abs(tn - pn) % 9 == 0:
            if tn < pn:
                tow = range(pn - 9, tn, -9)
            elif tn > pn:
                tow = range(pn + 9, tn, 9)
            else:
                tow = []
            allowed_distance = (len(tow) + 1) * sqrt(2) * Tile.WIDTH
            if distance != allowed_distance:
                return False
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        else:
            return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        ct1 = range(pn - 7, 0, -7)
        for tile in ct1:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct1 = range(pn - 7, tile - 7, -7)
                break
        ct2 = range(pn + 7, 65, 7)
        for tile in ct2:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct2 = range(pn + 7, tile + 7, 7)
                break
        ct3 = range(pn - 9, 0, -9)
        for tile in ct3:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct3 = range(pn - 9, tile - 9, -9)
                break
        ct4 = range(pn + 9, 65, 9)
        for tile in ct4:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct4 = range(pn + 9, tile + 9, 9)
                break
        controlled_tiles = list(ct1) + list(ct2) + list(ct3) + list(ct4)
        ct = []
        for i in controlled_tiles:
            ct.append(i)
        for i in ct:
            tile = Tile.get_tile(i)
            if abs(tile.x - self.x) != abs(tile.y - self.y):
                controlled_tiles.remove(i)
        return controlled_tiles


class Queen(Piece):
    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_tile_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        distance = Tile.get_distance_between_tiles(pn, tn)
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        # check if check after move
        if Piece.cicam(p, t):
            return False

        # vertical movement
        if abs(pn - tn) % 8 == 0:
            # tiles on way
            if tn < pn:
                tow = range(pn - 8, tn, -8)
            elif tn > pn:
                tow = range(pn + 8, tn, 8)
            else:
                tow = []
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        # horizontal movement
        elif t.y == p.y:
            # tiles on way
            if tn < pn:
                tow = range(pn - 1, tn, -1)
            elif tn > pn:
                tow = range(pn + 1, tn, 1)
            else:
                tow = []
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        # anti-diagonal movement
        elif abs(tn - pn) % 7 == 0:
            if tn < pn:
                tow = range(pn - 7, tn, -7)
            elif tn > pn:
                tow = range(pn + 7, tn, 7)
            else:
                tow = []
            allowed_distance = (len(tow) + 1) * sqrt(2) * Tile.WIDTH
            if distance != allowed_distance:
                return False
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        # diagonal movement
        elif abs(tn - pn) % 9 == 0:
            if tn < pn:
                tow = range(pn - 9, tn, -9)
            elif tn > pn:
                tow = range(pn + 9, tn, 9)
            else:
                tow = []
            allowed_distance = (len(tow) + 1) * sqrt(2) * Tile.WIDTH
            if distance != allowed_distance:
                return False
            # if there is a piece on the way, return false
            for tile in tow:
                if tile in keys:
                    return False
            return True
        else:
            return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_tile_number()
        ct1 = range(pn - 8, 0, -8)
        for tile in ct1:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct1 = range(pn - 8, tile - 8, -8)
                break
        ct2 = range(pn + 8, 65, 8)
        for tile in ct2:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct2 = range(pn + 8, tile + 8, 8)
                break
        ct3 = range(pn - 1, 0, -1)
        for tile in ct3:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct3 = range(pn - 1, tile - 1, -1)
                break
        ct4 = range(pn + 1, 65, 1)
        for tile in ct4:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct4 = range(pn + 1, tile + 1, 1)
                break
        ct5 = range(pn - 7, 0, -7)
        for tile in ct5:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct5 = range(pn - 7, tile - 7, -7)
                break
        ct6 = range(pn + 7, 65, 7)
        for tile in ct6:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct6 = range(pn + 7, tile + 7, 7)
                break
        ct7 = range(pn - 9, 0, -9)
        for tile in ct7:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct7 = range(pn - 9, tile - 9, -9)
                break
        ct8 = range(pn + 9, 65, 9)
        for tile in ct8:
            if tile in all_pieces.keys() and not (
                    all_pieces[tile].type == "king" and all_pieces[tile].color != self.color):
                ct8 = range(pn + 9, tile + 9, 9)
                break
        controlled_tiles1 = list(ct1) + list(ct2) + list(ct3) + list(ct4)
        ct = []
        for i in controlled_tiles1:
            ct.append(i)
        for i in ct:
            tile = Tile.get_tile(i)
            if tile.y != self.y and (abs(i - pn)) % 8 != 0:
                controlled_tiles1.remove(i)

        controlled_tiles2 = list(ct5) + list(ct6) + list(ct7) + list(ct8)
        ct = []
        for i in controlled_tiles2:
            ct.append(i)
        for i in ct:
            tile = Tile.get_tile(i)
            if abs(tile.x - self.x) != abs(tile.y - self.y):
                controlled_tiles2.remove(i)

        controlled_tiles = controlled_tiles1 + controlled_tiles2
        return controlled_tiles


class Auxpiece(pygame.Rect):
    aux_piece = True

    def __init__(self, x, y, piece_type, color):
        super().__init__(x, y, Tile.WIDTH, Tile.HEIGHT)
        self.type = piece_type
        self.color = color

    def check(self, all_pieces):
        return False

    def get_tile_number(self):
        return Tile.get_tile_number_from_coord(self.x/Tile.WIDTH, self.y/Tile.HEIGHT)

    def move(self, t, real_move=True):
        return False

    def gct(self, all_pieces):
        return []
