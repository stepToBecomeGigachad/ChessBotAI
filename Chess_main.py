# Updated Chess_main.py with scrollable history and improved scoring

import pygame as p
import Chess_engine, Chess_AI
from multiprocessing import Queue, Process
from queue import Empty
import random

import time

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
colors = [p.Color("white"), p.Color("#B58863")]
BOARD_WIDTH = WIDTH
MOVE_LOG_PANEL_WIDTH = 250

scroll_offset = 0  # Global scroll offset

def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        img = p.image.load(f'./images/{piece}.png')
        img = p.transform.scale(img, (SQ_SIZE, SQ_SIZE))
        IMAGES[piece] = img

def draw_promotion_menu(screen, color, sq_size):
    pieces = ['Q', 'R', 'B', 'N']
    menu_rects = []
    menu_x = WIDTH // 2 - sq_size // 2
    menu_y = HEIGHT // 2 - 2 * sq_size
    for i, piece in enumerate(pieces):
        rect = p.Rect(menu_x, menu_y + i * sq_size, sq_size, sq_size)
        p.draw.rect(screen, p.Color("lightgray"), rect)
        p.draw.rect(screen, p.Color("black"), rect, 2)
        img = IMAGES[color + piece]
        screen.blit(img, rect)
        menu_rects.append((rect, color + piece))
    p.display.update()
    return menu_rects

def draw_main_menu(screen):
    # Màu sắc
    BG_COLOR = (245, 247, 250)
    TITLE_COLOR = (30, 30, 30)
    BUTTON_COLOR = (100, 149, 237)
    BUTTON_HOVER = (123, 175, 255)
    BUTTON_TEXT = (255, 255, 255)
    SHADOW_COLOR = (180, 180, 180)

    screen.fill(BG_COLOR)

    # Font chữ
    title_font = p.font.SysFont("Arial", 64, bold=True)
    button_font = p.font.SysFont("Arial", 36, bold=True)

    # Vẽ tiêu đề với bóng đổ
    title_text = title_font.render("Chess Game", True, TITLE_COLOR)
    title_shadow = title_font.render("Chess Game", True, SHADOW_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title_text, title_rect)

    # Thông số nút
    button_width = 320
    button_height = 70
    button_radius = 18
    button_gap = 32

    # Tính toán vị trí nút để căn giữa dọc
    total_height = button_height * 2 + button_gap
    start_y = HEIGHT // 2 - total_height // 2 + 40  # +40 để cân đối với tiêu đề phía trên
    center_x = WIDTH // 2

    # Tạo nút
    pvp_button = p.Rect(center_x - button_width // 2, start_y, button_width, button_height)
    pvc_button = p.Rect(center_x - button_width // 2, start_y + button_height + button_gap, button_width, button_height)

    # Hiệu ứng hover
    mouse_pos = p.mouse.get_pos()
    pvp_col = BUTTON_HOVER if pvp_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pvc_col = BUTTON_HOVER if pvc_button.collidepoint(mouse_pos) else BUTTON_COLOR

    # Vẽ bóng đổ cho nút
    p.draw.rect(screen, SHADOW_COLOR, pvp_button.move(3, 3), border_radius=button_radius)
    p.draw.rect(screen, SHADOW_COLOR, pvc_button.move(3, 3), border_radius=button_radius)

    # Vẽ nút bo góc
    p.draw.rect(screen, pvp_col, pvp_button, border_radius=button_radius)
    p.draw.rect(screen, pvc_col, pvc_button, border_radius=button_radius)
    p.draw.rect(screen, (60, 60, 60), pvp_button, 2, border_radius=button_radius)
    p.draw.rect(screen, (60, 60, 60), pvc_button, 2, border_radius=button_radius)

    # Vẽ text trên nút (có padding dọc)
    pvp_text = button_font.render("Player vs Player", True, BUTTON_TEXT)
    pvc_text = button_font.render("Player vs Computer", True, BUTTON_TEXT)
    pvp_text_rect = pvp_text.get_rect(center=pvp_button.center)
    pvc_text_rect = pvc_text.get_rect(center=pvc_button.center)
    screen.blit(pvp_text, pvp_text_rect)
    screen.blit(pvc_text, pvc_text_rect)

    return pvp_button, pvc_button

def draw_side_selection(screen):
    # Màu sắc
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)

    # Font chữ
    title_font = p.font.Font(None, 64)
    button_font = p.font.Font(None, 50)

    # Vẽ tiêu đề
    title_text = title_font.render("Choose Your Side", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Tạo nút chọn màu quân
    white_button = p.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 50)
    black_button = p.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50)

    # Vẽ các nút với hiệu ứng hover
    mouse_pos = p.mouse.get_pos()
    
    # White button
    white_color = LIGHT_GRAY if white_button.collidepoint(mouse_pos) else GRAY
    p.draw.rect(screen, white_color, white_button)
    p.draw.rect(screen, BLACK, white_button, 2)
    white_text = button_font.render("Play as White", True, BLACK)
    white_text_rect = white_text.get_rect(center=white_button.center)
    screen.blit(white_text, white_text_rect)

    # Black button
    black_color = LIGHT_GRAY if black_button.collidepoint(mouse_pos) else GRAY
    p.draw.rect(screen, black_color, black_button)
    p.draw.rect(screen, BLACK, black_button, 2)
    black_text = button_font.render("Play as Black", True, BLACK)
    black_text_rect = black_text.get_rect(center=black_button.center)
    screen.blit(black_text, black_text_rect)

    return white_button, black_button

def draw_popup(screen, message, button_text="OK", icon=None):
    # Tạo overlay mờ
    overlay = p.Surface((screen.get_width(), screen.get_height()), p.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    # Tạo popup box
    popup_width = 420
    popup_height = 240
    popup_x = (screen.get_width() - popup_width) // 2
    popup_y = (screen.get_height() - popup_height) // 2
    popup_rect = p.Rect(popup_x, popup_y, popup_width, popup_height)

    # Bóng đổ cho popup
    shadow_offset = 8
    shadow_rect = popup_rect.move(shadow_offset, shadow_offset)
    p.draw.rect(screen, (180, 180, 180), shadow_rect, border_radius=22)

    # Vẽ popup bo góc
    p.draw.rect(screen, (255, 255, 255), popup_rect, border_radius=22)
    p.draw.rect(screen, (60, 60, 60), popup_rect, 2, border_radius=22)

    # Vẽ icon nếu có
    icon_y = popup_y + 30
    if icon == "win":
        # Vẽ vương miện vàng đơn giản
        crown_color = (255, 215, 0)
        cx = popup_x + popup_width // 2
        cy = icon_y
        points = [
            (cx - 40, cy + 30), (cx - 30, cy), (cx - 10, cy + 20),
            (cx, cy), (cx + 10, cy + 20), (cx + 30, cy), (cx + 40, cy + 30)
        ]
        p.draw.polygon(screen, crown_color, points)
        p.draw.polygon(screen, (180, 140, 0), points, 2)
        icon_y += 40
    elif icon == "draw":
        # Vẽ icon hòa (cờ trắng đen)
        cx = popup_x + popup_width // 2
        cy = icon_y + 10
        p.draw.circle(screen, (220, 220, 220), (cx - 15, cy), 15)
        p.draw.circle(screen, (60, 60, 60), (cx + 15, cy), 15)
        icon_y += 35

    # Vẽ message
    font = p.font.SysFont("Arial", 36, bold=True)
    text = font.render(message, True, (30, 30, 30))
    text_rect = text.get_rect(center=(popup_x + popup_width//2, icon_y + 40))
    screen.blit(text, text_rect)

    # Vẽ nút nổi bật
    button_width = 140
    button_height = 48
    button_x = popup_x + (popup_width - button_width) // 2
    button_y = popup_y + popup_height - 70
    button_rect = p.Rect(button_x, button_y, button_width, button_height)

    # Hiệu ứng hover cho nút
    mouse_pos = p.mouse.get_pos()
    BUTTON_COLOR = (100, 149, 237)
    BUTTON_HOVER = (123, 175, 255)
    button_color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    p.draw.rect(screen, (180, 180, 180), button_rect.move(2, 2), border_radius=16)
    p.draw.rect(screen, button_color, button_rect, border_radius=16)
    p.draw.rect(screen, (60, 60, 60), button_rect, 2, border_radius=16)

    # Vẽ text trên nút
    button_font = p.font.SysFont("Arial", 28, bold=True)
    button_text_surface = button_font.render(button_text, True, (255, 255, 255))
    button_text_rect = button_text_surface.get_rect(center=button_rect.center)
    screen.blit(button_text_surface, button_text_rect)

    return button_rect

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Menu chỉ cần kích thước bàn cờ
    clock = p.time.Clock()

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)

    # Game states
    MAIN_MENU = 'main_menu'
    SIDE_SELECT = 'side_select'
    GAME_PLAYING = 'game_playing'
    GAME_OVER = 'game_over'

    current_state = MAIN_MENU
    is_human_vs_computer = False
    player_side = None
    player_one = False
    player_two = False
    human_turn = True
    game_over_message = ""

    # Khởi tạo các biến cho game chính
    gs = Chess_engine.GameState()
    valid_moves = gs.getValidMoves()
    moveMade = False
    game_over = False
    show_history_popup = False
    square_selected = ()
    player_clicks = []
    AI_thinking = False
    moveUndone = False
    moveFinderProcess = None

    load_images()
    running = True

    while running:
        if current_state == MAIN_MENU:
            # Đảm bảo màn hình đúng kích thước menu
            if screen.get_width() != WIDTH or screen.get_height() != HEIGHT:
                screen = p.display.set_mode((WIDTH, HEIGHT))
            screen.fill(WHITE)
            pvp_button, pvc_button = draw_main_menu(screen)
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                elif event.type == p.MOUSEBUTTONDOWN:
                    mouse_pos = p.mouse.get_pos()
                    if pvp_button.collidepoint(mouse_pos):
                        is_human_vs_computer = False
                        player_one = True
                        player_two = True
                        # Chuyển sang màn hình game (mở rộng màn hình)
                        screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
                        current_state = GAME_PLAYING
                    elif pvc_button.collidepoint(mouse_pos):
                        is_human_vs_computer = True
                        current_state = SIDE_SELECT

        elif current_state == SIDE_SELECT:
            if screen.get_width() != WIDTH or screen.get_height() != HEIGHT:
                screen = p.display.set_mode((WIDTH, HEIGHT))
            screen.fill(WHITE)
            white_button, black_button = draw_side_selection(screen)
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                elif event.type == p.MOUSEBUTTONDOWN:
                    mouse_pos = p.mouse.get_pos()
                    if white_button.collidepoint(mouse_pos):
                        player_side = 'white'
                        player_one = True
                        player_two = False
                        screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
                        current_state = GAME_PLAYING
                    elif black_button.collidepoint(mouse_pos):
                        player_side = 'black'
                        player_one = False
                        player_two = True
                        screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
                        current_state = GAME_PLAYING

        elif current_state == GAME_PLAYING:
            # Đảm bảo màn hình đúng kích thước game
            if screen.get_width() != WIDTH + MOVE_LOG_PANEL_WIDTH or screen.get_height() != HEIGHT:
                screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
            human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
            
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    if show_history_popup:
                        if e.button == 4:  # Mouse wheel up
                            scroll_offset = max(0, scroll_offset - 1)
                        elif e.button == 5:  # Mouse wheel down
                            scroll_offset += 1
                    elif not game_over and human_turn:
                        location = p.mouse.get_pos()
                        if location[0] < BOARD_WIDTH and location[1] < HEIGHT:
                            col = location[0] // SQ_SIZE
                            row = location[1] // SQ_SIZE
                            if square_selected == (row, col):
                                square_selected = ()
                                player_clicks = []
                            else:
                                square_selected = (row, col)
                                player_clicks.append(square_selected)
                            if len(player_clicks) == 2:
                                move_to_make = None
                                for valid_move in valid_moves:
                                    if player_clicks[0] == (valid_move.startRow, valid_move.startCol) and \
                                       player_clicks[1] == (valid_move.endRow, valid_move.endCol):
                                        move_to_make = valid_move
                                        break
                                if move_to_make:
                                    if move_to_make.isPawnPromotion:
                                        color = move_to_make.pieceMoved[0]
                                        menu_rects = draw_promotion_menu(screen, color, SQ_SIZE)
                                        promoting = True
                                        promoteTo = None
                                        while promoting:
                                            for ev in p.event.get():
                                                if ev.type == p.QUIT:
                                                    p.quit()
                                                    import sys
                                                    sys.exit()
                                                if ev.type == p.MOUSEBUTTONDOWN:
                                                    mouse_pos = p.mouse.get_pos()
                                                    for rect, piece in menu_rects:
                                                        if rect.collidepoint(mouse_pos):
                                                            promoteTo = piece
                                                            promoting = False
                                                            break
                                            p.time.wait(10)
                                        move_to_make.promoteTo = promoteTo
                                    move_to_make.score = Chess_AI.scoreMaterial(gs.board)
                                    gs.makeMove(move_to_make)
                                    moveMade = True
                                square_selected = ()
                                player_clicks = []
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z and not game_over:
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        game_over = False
                        if AI_thinking:
                            AI_thinking = False
                            moveFinderProcess.terminate()
                        moveUndone = False
                        player_clicks = []
                        square_selected = ()
                    if e.key == p.K_r:
                        gs = Chess_engine.GameState()
                        valid_moves = gs.getValidMoves()
                        square_selected = ()
                        player_clicks = []
                        moveMade = False
                        game_over = False
                        if AI_thinking:
                            AI_thinking = False
                            moveFinderProcess.terminate()
                        moveUndone = False
                        scroll_offset = 0
                    if game_over and e.key == p.K_h and (p.key.get_mods() & p.KMOD_CTRL):
                        show_history_popup = True
                    if show_history_popup:
                        if e.key == p.K_UP:
                            scroll_offset = max(0, scroll_offset - 1)
                        elif e.key == p.K_DOWN:
                            scroll_offset += 1
                elif e.type == p.MOUSEBUTTONDOWN and show_history_popup:
                    mouse_pos = p.mouse.get_pos()
                    back_rect = draw_history_popup(screen, gs, scroll_offset)
                    if back_rect.collidepoint(mouse_pos):
                        show_history_popup = False

            # AI move
            if not game_over and not human_turn and not moveUndone:
                if not AI_thinking:
                    AI_thinking = True
                    print("thinking ... ")
                    returnQueue = Queue()
                    moveFinderProcess = Process(target=Chess_AI.findBestMove, args=(gs, valid_moves, returnQueue))
                    moveFinderProcess.start()

                if moveFinderProcess is not None and not moveFinderProcess.is_alive():
                    print("done thinking")
                    try:
                        AI_move = returnQueue.get()
                        if AI_move is None:
                            AI_move = Chess_AI.findRandomMoves(valid_moves)
                        AI_move.score = Chess_AI.scoreMaterial(gs.board)
                        gs.makeMove(AI_move)
                        moveMade = True
                        AI_thinking = False
                    except Empty:
                        AI_move = Chess_AI.findRandomMoves(valid_moves)
                        AI_move.score = Chess_AI.scoreMaterial(gs.board)
                        gs.makeMove(AI_move)
                        moveMade = True
                        AI_thinking = False

            if moveMade:
                valid_moves = gs.getValidMoves()
                moveMade = False

            if show_history_popup:
                draw_history_popup(screen, gs, scroll_offset)
            else:
                draw_game_state(screen, gs, valid_moves, square_selected)
                if gs.checkmate:
                    game_over = True
                    game_over_message = "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
                    current_state = GAME_OVER
                elif gs.stalemate:
                    game_over = True
                    game_over_message = "Stalemate"
                    current_state = GAME_OVER

            p.display.flip()
            clock.tick(MAX_FPS)

        elif current_state == GAME_OVER:
            draw_game_state(screen, gs, valid_moves, square_selected)
            ok_button = draw_popup(screen, game_over_message, "New Game", icon="win")
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                elif event.type == p.MOUSEBUTTONDOWN:
                    if ok_button.collidepoint(p.mouse.get_pos()):
                        gs = Chess_engine.GameState()
                        valid_moves = gs.getValidMoves()
                        square_selected = ()
                        player_clicks = []
                        moveMade = False
                        game_over = False
                        if AI_thinking:
                            AI_thinking = False
                            moveFinderProcess.terminate()
                        moveUndone = False
                        scroll_offset = 0
                        current_state = MAIN_MENU

    p.quit()

def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, bold=True)
    text_surface = font.render(text, True, p.Color("Black"))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def draw_game_state(screen, gs, valid_moves, square_selected):
    draw_board(screen)
    draw_pieces(screen, gs.board)
    draw_move_history(screen, gs)
    highlight_square(screen, gs, valid_moves, square_selected)

def highlight_square(screen, gs, valid_moves, square_selected):
    if square_selected != ():
        r, c = square_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    s.fill(p.Color('yellow') if gs.board[move.endRow][move.endCol] == '--' else p.Color('red'))
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
    if len(gs.move_log) > 0:
        last_move = gs.move_log[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.startCol * SQ_SIZE, last_move.startRow * SQ_SIZE))
        screen.blit(s, (last_move.endCol * SQ_SIZE, last_move.endRow * SQ_SIZE))

def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_move_history(screen, gs):
    move_history_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color("white"), move_history_rect)
    p.draw.rect(screen, p.Color("gray"), move_history_rect, 2)
    title_font = p.font.SysFont("Arial", 20, True, False)
    title_text = title_font.render("Move History", True, p.Color("black"))
    screen.blit(title_text, (BOARD_WIDTH + 10, 10))
    p.draw.line(screen, p.Color("black"), (BOARD_WIDTH + 10, 40), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH - 10, 40), 2)
    move_texts = []
    for i in range(0, len(gs.move_log), 2):
        move_text = str(i//2 + 1) + ". "
        if i < len(gs.move_log):
            move_text += gs.move_log[i].getChessNotation()
        if i + 1 < len(gs.move_log):
            move_text += " " + gs.move_log[i + 1].getChessNotation()
        move_texts.append(move_text)
    font = p.font.SysFont("Arial", 16, True, False)
    padding = 50
    for i, text in enumerate(move_texts):
        move_rect = p.Rect(BOARD_WIDTH + 5, padding + i * 25 - 2, MOVE_LOG_PANEL_WIDTH - 10, 24)
        bg_color = p.Color("#F0F0F0") if i % 2 == 0 else p.Color("white")
        p.draw.rect(screen, bg_color, move_rect)
        text_surface = font.render(text, True, p.Color("black"))
        screen.blit(text_surface, (BOARD_WIDTH + 10, padding + i * 25))

def draw_history_popup(screen, gs, scroll_offset):
    overlay = p.Surface((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    overlay.set_alpha(230)
    overlay.fill(p.Color('white'))
    screen.blit(overlay, (0, 0))

    title_font = p.font.SysFont("Arial", 36, True, False)
    screen.blit(title_font.render("History Moves", True, p.Color("black")), (120, 30))

    header_font = p.font.SysFont("Arial", 22, True, False)
    screen.blit(header_font.render("Turn", True, p.Color("black")), (70, 100))
    screen.blit(header_font.render("Side", True, p.Color("black")), (140, 100))
    screen.blit(header_font.render("Move", True, p.Color("black")), (230, 100))
    screen.blit(header_font.render("Score", True, p.Color("black")), (400, 100))
    p.draw.line(screen, p.Color("black"), (60, 130), (520, 130), 2)

    font = p.font.SysFont("Arial", 20)
    visible_moves = gs.move_log[scroll_offset:scroll_offset+12]
    for i, move in enumerate(visible_moves):
        idx = scroll_offset + i
        turn = str(idx//2 + 1) if idx % 2 == 0 else ""
        side = "White" if idx % 2 == 0 else "Black"
        move_str = move.pieceMoved[1] + " " + move.getRankFile(move.startRow, move.startCol) + move.getRankFile(move.endRow, move.endCol)
        score = getattr(move, 'score', 0)
        row_y = 140 + i * 30
        bg_color = p.Color("#F0F0F0") if i % 2 == 0 else p.Color("#E0E0E0")
        p.draw.rect(screen, bg_color, p.Rect(60, row_y - 2, 460, 28))
        screen.blit(font.render(turn, True, p.Color("black")), (80, row_y))
        screen.blit(font.render(side, True, p.Color("#1a75ff") if side == "White" else p.Color("#d11a1a")), (140, row_y))
        screen.blit(font.render(move_str, True, p.Color("black")), (230, row_y))
        screen.blit(font.render(str(score), True, p.Color("black")), (420, row_y))

    white_score = sum(m.score for i, m in enumerate(gs.move_log) if i % 2 == 0 and hasattr(m, 'score'))
    black_score = sum(m.score for i, m in enumerate(gs.move_log) if i % 2 == 1 and hasattr(m, 'score'))
    footer_font = p.font.SysFont("Arial", 22, True)
    screen.blit(footer_font.render(f"Total White: {white_score}", True, p.Color("blue")), (60, 530))
    screen.blit(footer_font.render(f"Total Black: {black_score}", True, p.Color("red")), (300, 530))

    back_rect = p.Rect(240, 570, 120, 40)
    p.draw.rect(screen, p.Color("gray"), back_rect)
    p.draw.rect(screen, p.Color("black"), back_rect, 2)
    back_font = p.font.SysFont("Arial", 22, True)
    back_text = back_font.render("Back", True, p.Color("black"))
    screen.blit(back_text, (back_rect.x + 30, back_rect.y + 7))
    return back_rect

if __name__ == "__main__":
    main()
