import pygame
from classes import *


class Piece(pygame.Rect):
    aux_piece = False

    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        super().__init__(x, y, Tile.WIDTH, Tile.HEIGHT)
        self.image = pygame.image.load(image)
        self.selected = False
        if real_piece:
            GameController.piecesDict[self.get_number()] = self
        self.type = piece_type
        self.color = color
        self.initial_pos = True
        if self.type == "pawn":
            if self.color == "white" and self.get_number() not in (49, 50, 51, 52, 53, 54, 55, 56):
                self.initial_pos = False
            elif self.color == "black" and self.get_number() not in (9, 10, 11, 12, 13, 14, 15, 16):
                self.initial_pos = False

    def gct(self, allPieces):
        return []

    def draw_image(self, screen):
        if self.color == "white":
            screen.blit(Images.white_image, (self.x, self.y))
        else:
            screen.blit(Images.black_image, (self.x, self.y))
        screen.blit(self.image, (self.x, self.y))

    def get_number(self):
        return int((self.x / Tile.WIDTH) + 1 + (self.y / Tile.HEIGHT) * 8)

    def __str__(self):
        res = "Piece: " + self.type + "\nColor: " + self.color + "\nNumber: " + str(self.get_number())
        res += "\nx: " + str(self.x) + "\ny: " + str(self.y)
        return res

    @staticmethod
    def get_piece(number):
        for piece in GameController.piecesDict.values():
            if piece.get_number() == number:
                return piece

    @staticmethod
    def get_white_king(all_pieces):  # get white king
        for piece in all_pieces.values():
            if piece.type == "king" and piece.color == "white":
                return piece

    @staticmethod
    def get_black_king(all_pieces):  # get black king
        for piece in all_pieces.values():
            if piece.type == "king" and piece.color == "black":
                return piece

    @staticmethod
    def get_white_controlled_tiles(all_pieces):  # get white controlled tiles
        wct = []
        for piece in all_pieces.values():
            if piece.color == "white":
                wct += piece.gct(all_pieces)
        return wct

    @staticmethod
    def get_black_controlled_tiles(all_pieces):  # get black controlled tiles
        bct = []
        for piece in all_pieces.values():
            if piece.color == "black":
                bct += piece.gct(all_pieces)
        return bct

    @staticmethod
    def cicam(moving_piece, future_tile):  # check if check after move
        # create auxiliary dictionary
        aux_dict = {}
        for piece in GameController.piecesDict.values():
            aux_dict[piece.get_number()] = piece

        # remove moving piece from auxiliary dictionary
        del aux_dict[moving_piece.get_number()]
        if future_tile.number in aux_dict.keys():
            del aux_dict[future_tile.number]

        # create auxiliary piece in new position
        aux_piece = Auxpiece(future_tile.x, future_tile.y, moving_piece.type, moving_piece.color)

        # add auxiliary piece to auxiliary dictionary
        aux_dict[aux_piece.get_number()] = aux_piece

        wking = Piece.get_white_king(aux_dict)
        bking = Piece.get_black_king(aux_dict)

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


class King(Piece):
    castle = False

    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def check(self, all_pieces):
        pn = self.get_number()

        wct = Piece.get_white_controlled_tiles(all_pieces)
        bct = Piece.get_black_controlled_tiles(all_pieces)

        if self.color == "white" and pn in bct:
            return True
        elif self.color == "black" and pn in wct:
            return True
        else:
            return False

    def move(self, t, all_pieces, real_move=True):
        # real move is necessary to avoid undesired castle (because of allowed moves cicle)
        p = self
        pn = self.get_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()

        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        if Tile.gdbt(pn, tn) > 151:
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
        if p.initial_pos and p.color == "white" and not p.get_number() in btc:
            if tn == pn + 2 and pn + 1 not in keys and pn + 1 not in btc:
                wrook = Piece.get_piece(64)
                if wrook is None:
                    return False
                elif not wrook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, short castle
                        del GameController.piecesDict[wrook.get_number()]
                        wrook.x = 5 * Tile.WIDTH
                        GameController.piecesDict[wrook.get_number()] = wrook
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
                        del GameController.piecesDict[wrook.get_number()]
                        wrook.x = 3 * Tile.WIDTH
                        GameController.piecesDict[wrook.get_number()] = wrook
                        wrook.initial_pos = False
                    return True
        # black king castle moves
        if p.initial_pos and p.color == "black" and not p.get_number() in wtc:
            if tn == pn + 2 and pn + 1 not in keys and pn + 1 not in wtc:
                brook = Piece.get_piece(8)
                if brook is None:
                    return False
                elif not brook.initial_pos:
                    return False
                else:
                    if real_move:  # if it is a true move, short castle
                        del GameController.piecesDict[brook.get_number()]
                        brook.x = 5 * Tile.WIDTH
                        GameController.piecesDict[brook.get_number()] = brook
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
                        del GameController.piecesDict[brook.get_number()]
                        brook.x = 3 * Tile.WIDTH
                        GameController.piecesDict[brook.get_number()] = brook
                        brook.initial_pos = False
                    return True
        # standard king moves
        if tn in (pn - 8 - 1, pn - 8, pn - 8 + 1, pn + 1, pn + 8 + 1, pn + 8, pn + 8 - 1, pn - 1):
            return True
        else:
            return False

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_number()
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
        del GameController.piecesDict[self.get_number()]
        Queen(self.x, self.y, Images.queen_image, "queen", self.color)
        if self.color == "white":
            utils.black_checkmate()
        elif self.color == "black":
            utils.white_checkmate()

    def en_passant(self, tn, real_move):
        pn = self.get_number()
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
        pn = self.get_number()  # piece number
        tn = t.number  # clicked tile number

        keys = all_pieces.keys()
        if tn in keys:
            ptc = all_pieces[tn]  # piece to capture
            if p.color == ptc.color:
                if real_move and ptc != self:
                    ptc.selected = True
                return False

        if Tile.gdbt(pn, tn) > 151:
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
        pn = self.get_number()
        if self.color == "white":
            controlled_tiles = [pn - 8 - 1, pn - 8 + 1]
            if pn in Tile.EDGE_SX:
                controlled_tiles.remove(pn - 8 - 1)
            elif pn in Tile.EDGE_DX:
                controlled_tiles.remove(pn - 8 + 1)
        elif self.color == "black":
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
        pn = self.get_number()  # piece number
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

        if Tile.gdbt(pn, tn) > 170:
            return False
        elif tn in (pn - 16 - 1, pn - 16 + 1, pn + 16 - 1, pn + 16 + 1, pn - 8 - 2, pn - 8 + 2, pn + 8 - 2, pn + 8 + 2):
            return True

    def gct(self, all_pieces):  # get controlled tiles
        pn = self.get_number()
        controlled_tiles = [pn - 16 - 1, pn - 16 + 1, pn + 16 - 1, pn + 16 + 1, pn - 8 - 2, pn - 8 + 2, pn + 8 - 2,
                            pn + 8 + 2]
        ct = []
        for i in controlled_tiles:
            ct.append(i)
        for i in ct:
            distance = Tile.gdbt(pn, i)
            if i < 1 or i > 64 or distance > 170 or distance == -1:
                controlled_tiles.remove(i)
        return controlled_tiles


class Rook(Piece):
    def __init__(self, x, y, image, piece_type, color, real_piece=True):
        Piece.__init__(self, x, y, image, piece_type, color, real_piece)

    def move(self, t, all_pieces, real_move=True):
        p = self
        pn = self.get_number()  # piece number
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
        pn = self.get_number()
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
        pn = self.get_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        distance = Tile.gdbt(pn, tn)
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
        pn = self.get_number()
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
        pn = self.get_number()  # piece number
        tn = t.number
        keys = all_pieces.keys()
        distance = Tile.gdbt(pn, tn)
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
        pn = self.get_number()
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

    def get_number(self):
        return (self.x / Tile.WIDTH) + 1 + (self.y / Tile.HEIGHT) * 8

    def move(self, t, real_move=True):
        return False

    def gct(self, all_pieces):
        return []
