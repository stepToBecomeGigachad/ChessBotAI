# This is main driver file. It will be responsible for handling user input and displaying the current GameState Object


import pygame as p
from pygame.examples.moveit import HEIGHT

from Chess import Chess_engine

WIDTH = HEIGHT = 512
DIMENSION = 8 # dimensions of a chess board is 8x8
SQ_SIZE = HEIGHT  //DIMENSION
MAX_FPS = 15 # Setting for animations
IMAGES ={}

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

    load_images() #Only do this once, before the while loop
    running = True
    square_selected = () # No square is selected, keep track of the last click of the user (tuple: (r,c))
    player_clicks = [] # Keep track of player click (two tuple: [(6,4), (4,4)]
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    move = Chess_engine.Move(player_clicks[0],player_clicks[1],gs.board)
                    print(move.getChessNotation())
                    if move in valid_moves:
                        gs.makeMove(move)
                        moveMade = True
                    square_selected = () #reset user click
                    player_clicks = []
            # Key handle
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            valid_moves = gs.getValidMoves()
            moveMade = False

        draw_game_state(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen,gs):
    draw_board(screen) # draw squares on the board
    draw_pieces(screen,gs.board) # draw pieces on top of those squares

def draw_board(screen):
    colors = [p.Color("white"), p.Color("#B58863")]
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

if __name__ == "__main__":
    main()
