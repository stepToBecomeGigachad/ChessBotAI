# This is main driver file. It will be responsible for handling user input and displaying the current GameState Object


import pygame as p
from pygame.examples.moveit import HEIGHT

import Chess_engine, Chess_AI

WIDTH = HEIGHT = 512
DIMENSION = 8 # dimensions of a chess board is 8x8
SQ_SIZE = HEIGHT  //DIMENSION
MAX_FPS = 15 # Setting for animations
IMAGES ={}
colors = [p.Color("white"), p.Color("#B58863")]

# Using def for loading images from document.
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    # Creat an object for chess

    for piece in pieces: # Take piece from pieces one by one
        img = p.image.load(f'./images/{piece}.png') # Another way to access image by using 'IMAGES['piece']'
        img = p.transform.scale(img, (SQ_SIZE, SQ_SIZE)) # Drawing image.
        IMAGES[piece] = img
    return IMAGES

# The main driver for our code. This will handle user input and updating the graphics.

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Chess_engine.GameState()
    valid_moves = gs.getValidMoves()
    moveMade = False # Just a flag variable for when a move is made
    game_over = False # Flag for game over state

    load_images() #Only do this once, before the while loop
    running = True
    square_selected = () # No square is selected, keep track of the last click of the user (tuple: (r,c))
    player_clicks = [] # Keep track of player click (two tuple: [(6,4), (4,4)]
    player_one =  False
    player_two = False
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two) 
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN and not game_over and human_turn:
                location = p.mouse.get_pos() # Get (x,y) location
                col = location[0] //SQ_SIZE
                row = location[1] //SQ_SIZE
                if square_selected == (row,col): #Check if the user click the same square twice
                    square_selected = () # Deselect
                    player_clicks = [] # Clear player click
                else:
                    square_selected =(row,col)
                    player_clicks.append(square_selected) # Append for both 1st and 2nd clicks
                if len(player_clicks) == 2: # After 2 click
                    for valid_move in valid_moves:
                        if player_clicks[0] == (valid_move.startRow, valid_move.startCol) and player_clicks[1] == (valid_move.endRow, valid_move.endCol):
                            gs.makeMove(valid_move)
                            moveMade = True
                            break
                    square_selected = () #reset user click
                    player_clicks = []
            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z and not game_over: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                if e.key == p.K_r: # reset the game when 'r' is pressed
                    gs = Chess_engine.GameState()
                    valid_moves = gs.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    moveMade = False
                    game_over = False
        #AI move finder
        if  not game_over and not human_turn:
            AI_move = Chess_AI.findRandomMoves(valid_moves)    
            gs.makeMove(AI_move)
            moveMade = True

        if moveMade:
            # animated_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            moveMade = False

        draw_game_state(screen, gs, valid_moves, square_selected)
        
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")
            
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight the square selected and the possible moves for the piece
'''
def highlight_square(screen, gs, valid_moves, square_selected):
    if square_selected != ():
        r,c = square_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Transparency of the square
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            
            # highlight moves
            s.set_alpha(100)
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] == '--':  # Normal move
                        s.fill(p.Color('yellow'))
                    else:  # Capture move
                        s.fill(p.Color('red'))
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def draw_game_state(screen, gs, valid_moves, square_selected):
    draw_board(screen) # draw squares on the board
    highlight_square(screen, gs, valid_moves, square_selected)
    draw_pieces(screen,gs.board) # draw pieces on top of those squares

def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    #Hiển thị hàng và cột
    font = p.font.SysFont("Arial", 18, bold=True)
    # Hiển thị các chữ cái A-H ở phía dưới bàn cờ
    for c in range(DIMENSION):
        bg_color = colors[(7 + c) % 2]  # Xác định màu ô ở hàng cuối (hàng số 1)
        text_color = p.Color("white") if bg_color == p.Color("#B58863") else p.Color("#B58863")
        label = font.render(chr(97 + c), True, text_color)  # Chữ a-h
        screen.blit(label, (c * SQ_SIZE + SQ_SIZE -9, HEIGHT - 18))  # Góc dưới phải mỗi ô

        # Hiển thị các số 1-8 ở góc dưới bên phải mỗi ô cột bên phải
    for r in range(DIMENSION):
        bg_color = colors[(r) % 2]  # Xác định màu ô ở cột bên trái
        text_color = p.Color("white") if bg_color == p.Color("#B58863") else p.Color("#B58863")
        label = font.render(str(8 - r), True, text_color)  # Số 8-1
        screen.blit(label, (4, r * SQ_SIZE + 4))

def draw_pieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animated_move(move, screen, board, clock):
    global colors
    
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames_per_square = 10 # frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r,c =(move.startRow + dR * frame / frame_count, move.startCol + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #erase the piece moved from  its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw the piece moved to its ending square
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], end_square)  
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()      
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, bold=True)
    text_surface = font.render(text, True, p.Color("Black"))
    text_rect = text_surface.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(text_surface, text_rect)
    

if __name__ == "__main__":
    main()
