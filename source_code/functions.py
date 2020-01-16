
import pygame, sys
from classes import *
from math import *
from random import randint

# sounds
pygame.mixer.init()


def play_game(screen):
	new_game()
	chessboard = pygame.image.load("images/chessboard.png")
	global game_loop
	game_loop = True
	while game_loop:  
	    # pawn promotion
	    for piece in Piece.DICT.values():
	        if piece.type == "pawn" and piece.get_number() in (1,2,3,4,5,6,7,8,57,58,59,60,61,62,63,64):
	            piece.promotion()

	    screen.blit(chessboard,(0,0))
	    events()
	    
	    # draw tiles number
	    #Tile.draw_tiles(screen)

	    # draw pieces
	    for piece in Piece.DICT.values():
	        piece.draw_image(screen)

	    
	    # get kings
	    wking = Piece.gwk(Piece.DICT)
	    bking = Piece.gbk(Piece.DICT)

	    aux = {}
	    for piece in Piece.DICT.values():
	        aux[piece.get_number()] = piece
	    aux[0] = Auxpiece(-1,-1,"","")
	    
	    wtc = [] # white tiles controlled
	    btc = [] # white tiles controlled
	    for piece in Piece.DICT.values():
	        if piece.color == "white":
	            wtc += piece.gct(Piece.DICT)
	        elif piece.color == "black":
	            btc += piece.gct(Piece.DICT)
	    
	    # color the king with red if under check
	    if wking.check(aux) or wking.get_number() in btc:
	        pygame.draw.rect(screen,(255,0,0),(wking.x,wking.y,wking.width,wking.height),4)
	    if bking.check(aux) or bking.get_number() in wtc:
	        pygame.draw.rect(screen,(255,0,0),(bking.x,bking.y,bking.width,bking.height),4)
	    
	    # draw allowed tiles cursor
	    for piece in Piece.DICT.values():
	        if piece.selected:
	            pygame.draw.rect(screen,(52,155,66),(piece.x,piece.y,piece.width,piece.height),4)
	            for tile in Tile.LIST:
	                if piece.move(tile,Piece.DICT,False):
	                    pygame.draw.circle(screen,(52,155,66),(tile.x+75/2,tile.y+75/2),8)
	    
	    pygame.display.flip()


def button(screen,msg,x,y,w,h,ic,ac,action=None):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	global legend_loop

	if x < mouse[0] < x+w and y < mouse[1] < y+h:
		pygame.draw.rect(screen,ac,(x,y,w,h))
		if click[0] == 1 and action == "play_game":
			Sounds.click_sound.play()
			pygame.time.wait(250)
			play_game(screen)
		elif click[0] == 1 and action == "legend":
			Sounds.click_sound.play()
			pygame.time.wait(250)
			legend(screen)
		elif click[0] == 1 and action == "credits":
			Sounds.click_sound.play()
			pygame.time.wait(250)
			credits(screen)
		elif click[0] == 1 and action == "quit":
			Sounds.click_sound.play()
			pygame.time.wait(250)
			pygame.quit()
			sys.exit()
		elif click[0] == 1 and action == "back":
			Sounds.click_sound.play()
			pygame.time.wait(250)
			legend_loop = False
	else:
		pygame.draw.rect(screen,ic,(x,y,w,h))

	buttonText = pygame.font.Font("freesansbold.ttf",30)
	textSurf, textRect = functions.text_objects(msg,buttonText)
	textRect.center = (x+(w)/2,y+(h/2))
	screen.blit(textSurf,textRect)


def credits(screen):
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
				pygame.time.wait(250)
				credits_loop = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				Sounds.click_sound.play()
				pygame.time.wait(250)
				credits_loop = False

		screen.blit(Images.credits_image,(0,0))
	
		pygame.display.flip()


def legend(screen):
	legendImage = pygame.image.load("images/legend.png")
	global legend_loop
	legend_loop = True
	while legend_loop:
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
					pygame.time.wait(250)
					legend_loop = False

		screen.blit(legendImage,(0,0))
		functions.button(screen,"Back",600/2-50,80,100,50,(153,76,0),(204,102,0),"back")
		
		pygame.display.flip()



def text_objects(text, font):
	textSurface = font.render(text,True,(0,0,0))
	return textSurface, textSurface.get_rect()


def text_display(screen,text,x,y,size):
	largeText = pygame.font.Font('freesansbold.ttf',size)
	TextSurf, TextRect = text_objects(text, largeText)
	TextRect.center = (x,y)
	screen.blit(TextSurf,TextRect)


def events():
	global game_loop
	
	for event in pygame.event.get():
		# exit
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		# mouse
		if event.type == pygame.MOUSEBUTTONDOWN:
			movement()
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_SPACE:
				new_game()
			elif event.key == pygame.K_BACKSPACE:
				Sounds.click_sound.play()
				pygame.time.wait(250)
				game_loop = False
			elif event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()
			elif event.key == pygame.K_LEFT:
				undo_move()
			elif event.key == pygame.K_RIGHT:
				repeat_move()


def save_moves():
	aux_dict = {}
	for piece in Piece.DICT.values():
		if piece.type == "king":
			aux_piece = King(piece.x,piece.y,Images.king_image,piece.type,piece.color,False)
		elif piece.type == "pawn":
			aux_piece = Pawn(piece.x,piece.y,Images.pawn_image,piece.type,piece.color,False)
		elif piece.type == "knight":
			aux_piece = Knight(piece.x,piece.y,Images.knight_image,piece.type,piece.color,False)
		elif piece.type == "bishop":
			aux_piece = Bishop(piece.x,piece.y,Images.bishop_image,piece.type,piece.color,False)
		elif piece.type == "rook":
			aux_piece = Rook(piece.x,piece.y,Images.rook_image,piece.type,piece.color,False)
		elif piece.type == "queen":
			aux_piece = Queen(piece.x,piece.y,Images.queen_image,piece.type,piece.color,False)

		aux_dict[aux_piece.get_number()] = aux_piece

	Tile.moves_dict[Tile.move_count] = aux_dict
	
	# if make a different move after undo_move(), delete all moves in the "future"
	for i in Tile.moves_dict.keys():
		if i > Tile.move_count:
			del Tile.moves_dict[i]
	

def undo_move():
	try:
		aux_dict = {}
		for piece in Tile.moves_dict[Tile.move_count-1].values():
			aux_dict[piece.get_number()] = piece

		Tile.move_count -= 1
		Piece.DICT.clear()

		for piece in aux_dict.values():
			if piece.type == "king":
				aux_piece = King(piece.x,piece.y,Images.king_image,piece.type,piece.color)
			elif piece.type == "pawn":
				aux_piece = Pawn(piece.x,piece.y,Images.pawn_image,piece.type,piece.color)
			elif piece.type == "knight":
				aux_piece = Knight(piece.x,piece.y,Images.knight_image,piece.type,piece.color)
			elif piece.type == "bishop":
				aux_piece = Bishop(piece.x,piece.y,Images.bishop_image,piece.type,piece.color)
			elif piece.type == "rook":
				aux_piece = Rook(piece.x,piece.y,Images.rook_image,piece.type,piece.color)
			elif piece.type == "queen":
				aux_piece = Queen(piece.x,piece.y,Images.queen_image,piece.type,piece.color)

		if Piece.WHITE_TURN:
			Piece.WHITE_TURN = False
		else:
			Piece.WHITE_TURN = True

	except KeyError:
		new_game(False)


def repeat_move():
	try:
		aux_dict = {}
		for piece in Tile.moves_dict[Tile.move_count+1].values():
			aux_dict[piece.get_number()] = piece

		Tile.move_count += 1
		Piece.DICT.clear()

		for piece in aux_dict.values():
			if piece.type == "king":
				aux_piece = King(piece.x,piece.y,Images.king_image,piece.type,piece.color)
			elif piece.type == "pawn":
				aux_piece = Pawn(piece.x,piece.y,Images.pawn_image,piece.type,piece.color)
			elif piece.type == "knight":
				aux_piece = Knight(piece.x,piece.y,Images.knight_image,piece.type,piece.color)
			elif piece.type == "bishop":
				aux_piece = Bishop(piece.x,piece.y,Images.bishop_image,piece.type,piece.color)
			elif piece.type == "rook":
				aux_piece = Rook(piece.x,piece.y,Images.rook_image,piece.type,piece.color)
			elif piece.type == "queen":
				aux_piece = Queen(piece.x,piece.y,Images.queen_image,piece.type,piece.color)

		if Piece.WHITE_TURN:
			Piece.WHITE_TURN = False
		else:
			Piece.WHITE_TURN = True

	except KeyError:
		print("No other moves to repeat")
		return



def movement():
	Mpos = pygame.mouse.get_pos() # [x,y]
	Mx = Mpos[0]/Tile.WIDTH
	My = Mpos[1]/Tile.HEIGHT
	for tile in Tile.LIST:
		if tile.x == (Mx*Tile.WIDTH) and tile.y == (My*Tile.HEIGHT):
			for piece in Piece.DICT.values():
				# if there is a piece selected, move that piece
				if piece.selected:
					piece.selected = False

					# if the selected piece can not move, break
					if not piece.move(tile,Piece.DICT):
						break

					# remove piece from dictionary
					del Piece.DICT[piece.get_number()]

					# change piece position
					piece.x = tile.x
					piece.y = tile.y
										
					piece.initial_pos = False


					# if there is already a piece, destroy it
					if tile.number in Piece.DICT.keys():
						if Piece.get_piece(tile.number).type == "queen":
							Sounds.queen_capture_sound.play()
						else:
							male_grunt = randint(1,2)
							if male_grunt == 1:
								Sounds.capture1_sound.play()
							elif male_grunt == 2:
								Sounds.capture2_sound.play()

						del Piece.DICT[tile.number]
					else:
						Sounds.move_sound.play()

					# add piece to dictionary (it will be in the new position)
					Piece.DICT[tile.number] = piece

					Tile.move_count += 1
					save_moves()

					# change turn
					if Piece.WHITE_TURN:
						Piece.WHITE_TURN = False
						for piece in Piece.DICT.values(): # en passant capture decays
							if piece.type == "pawn" and piece.color == "black":
								if piece.double_step:
									piece.double_step = False
						black_checkmate() # check if checkmate or draw
					else:
						Piece.WHITE_TURN = True
						for piece in Piece.DICT.values(): # en passant capture decays
							if piece.type == "pawn" and piece.color == "white":
								if piece.double_step:
									piece.double_step = False
						white_checkmate() # check if checkmate or draw	
					break					
				else:
					# if there is not a piece selected, select a piece if there is one
					"""
					if piece.get_number() == tile.number:
						piece.selected = True
					else:
						piece.selected = False
					
					"""
					if piece.get_number() == tile.number:
						if Piece.WHITE_TURN and piece.color == "white":
							piece.selected = True
						elif not Piece.WHITE_TURN and piece.color == "black":
							piece.selected = True
						else:
							piece.selected = False
										
					
def white_checkmate():
	for piece in Piece.DICT.values():
		if piece.color == "white":
			for tile in Tile.LIST:
				if piece.move(tile,Piece.DICT,False):
					return
	Sounds.checkmate_sound.play()
	wking = Piece.gwk(Piece.DICT)
	if wking.check(Piece.DICT):
		wking.image = pygame.image.load("images/king_skull.png")


def black_checkmate():
	for piece in Piece.DICT.values():
		if piece.color == "black":
			for tile in Tile.LIST:
				if piece.move(tile,Piece.DICT,False):
					return
	Sounds.checkmate_sound.play()
	bking = Piece.gbk(Piece.DICT)
	if bking.check(Piece.DICT):
		bking.image = pygame.image.load("images/king_skull.png")


def new_game(restart = True):
	Piece.DICT.clear()
	Piece.WHITE_TURN = True
	Tile.move_count = 0

	if restart:
		print("new game")
		Tile.moves_dict.clear()

	create_pieces()

	
	"""
	for piece in Piece.DICT.values():
		piece.initial_pos = True
		if piece.type == "pawn":
			piece.double_step = False
		elif piece.type == "king":
			piece.castle = False
	"""

def create_pieces():

	# White
	Rook(0*Tile.WIDTH,7*Tile.HEIGHT,Images.rook_image,"rook","white")
	Knight(1*Tile.WIDTH,7*Tile.HEIGHT,Images.knight_image,"knight","white")
	Bishop(2*Tile.WIDTH,7*Tile.HEIGHT,Images.bishop_image,"bishop","white")
	Queen(3*Tile.WIDTH,7*Tile.HEIGHT,Images.queen_image,"queen","white")
	King(4*Tile.WIDTH,7*Tile.HEIGHT,Images.king_image,"king","white")
	Bishop(5*Tile.WIDTH,7*Tile.HEIGHT,Images.bishop_image,"bishop","white")
	Knight(6*Tile.WIDTH,7*Tile.HEIGHT,Images.knight_image,"knight","white")
	Rook(7*Tile.WIDTH,7*Tile.HEIGHT,Images.rook_image,"rook","white")
	for i in range(0,8):
		Pawn(i*Tile.WIDTH,6*Tile.HEIGHT,Images.pawn_image,"pawn","white")

	# Black
	Rook(0*Tile.WIDTH,0*Tile.HEIGHT,Images.rook_image,"rook","black")
	Knight(1*Tile.WIDTH,0*Tile.HEIGHT,Images.knight_image,"knight","black")
	Bishop(2*Tile.WIDTH,0*Tile.HEIGHT,Images.bishop_image,"bishop","black")
	Queen(3*Tile.WIDTH,0*Tile.HEIGHT,Images.queen_image,"queen","black")
	King(4*Tile.WIDTH,0*Tile.HEIGHT,Images.king_image,"king","black")
	Bishop(5*Tile.WIDTH,0*Tile.HEIGHT,Images.bishop_image,"bishop","black")
	Knight(6*Tile.WIDTH,0*Tile.HEIGHT,Images.knight_image,"knight","black")
	Rook(7*Tile.WIDTH,0*Tile.HEIGHT,Images.rook_image,"rook","black")
	for i in range(0,8):
		Pawn(i*Tile.WIDTH,1*Tile.HEIGHT,Images.pawn_image,"pawn","black")