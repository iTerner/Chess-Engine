"""
The main driver file. It will be responsible for handling user input and displaying the current
GameState object
"""

import pygame
from game_state import GameState
from const import WIDTH, HEIGHT, SQUARE_SIZE, DIMENSIONS, IMAGES, MOVE_LOG_PANEL_HEIGHT, MOVE_LOG_PANEL_WIDTH
from move import Move
import sys
from multiprocessing import Process, Queue
from ai import find_best_move, find_random_move
pygame.init()

MAX_FPS = 15


def get_row_col_from_mouse(pos: tuple) -> tuple:
    """
    The function returns the row and cols of the selected square
    """
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def draw_board(win: pygame.display) -> None:
    """
    draw the squares on the board
    """
    global colors
    colors = [pygame.Color("white"), pygame.Color("gray")]
    win.fill(pygame.Color("grey"))
    for row in range(DIMENSIONS):
        for col in range(row % 2, DIMENSIONS, 2):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(win, color, pygame.Rect(col * SQUARE_SIZE,
                                                     row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(win: pygame.display, board: list) -> None:
    """
    draw the pieces on the board using the current GameState.board
    """
    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            piece = board[row][col]
            # check if the piece isn't an empty square
            if piece != "--":
                win.blit(IMAGES[piece], pygame.Rect(
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_squares(win: pygame.display, gs: GameState, valid_moves: list, selected_square: tuple) -> None:
    """
    Highlight square selected and moves for piece selected.
    """
    if (len(gs.moveLog)) > 0:
        last_move = gs.moveLog[-1]
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color('green'))
        win.blit(s, (last_move.end_col * SQUARE_SIZE,
                     last_move.end_row * SQUARE_SIZE))
    if selected_square != ():
        row, col = selected_square
        if gs.board[row][col][0] == (
                'w' if gs.whiteToMove else 'b'):  # square_selected is a piece that can be moved
            # highlight selected square
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            # transparency value 0 -> transparent, 255 -> opaque
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    win.blit(s, (move.end_col * SQUARE_SIZE,
                                 move.end_row * SQUARE_SIZE))


def draw_move_log(win: pygame.display, gs: GameState, font: pygame.font) -> None:
    """
    Draws the move log.
    """
    move_log_rect = pygame.Rect(
        WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pygame.draw.rect(win, pygame.Color('black'), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, pygame.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        win.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def draw_end_game_text(win: pygame.display, text: str) -> None:
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, pygame.Color("gray"))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                          HEIGHT / 2 - text_object.get_height() / 2)
    win.blit(text_object, text_location)
    text_object = font.render(text, False, pygame.Color('black'))
    win.blit(text_object, text_location.move(2, 2))


def animateMove(move: Move, screen: pygame.display, board: list, clock: pygame.time.Clock) -> None:
    """
    Animating a move
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count,
                    move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pygame.Rect(move.end_col * SQUARE_SIZE,
                                 move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + \
                    1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = pygame.Rect(
                    move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], pygame.Rect(
            col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)


def draw_game_state(win: pygame.display, gs: GameState, valid_moves: list, selected_square: tuple) -> None:
    """
    The function responsible for all the graphics within a current game state
    """
    # draw squares on the board
    draw_board(win)
    # add in piece highlight or move suggestions
    highlight_squares(win, gs, valid_moves, selected_square)
    # draw pieces on the board
    draw_pieces(win, gs.board)


def main():
    win = pygame.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    win.fill(pygame.Color("white"))
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move

    run = True
    # no square is selected, keep track of the last click of the user (row, col)
    selected_square = ()
    # keep track of player clicks (two tuples: [(6, 4), (5, 4)])
    player_clicks = []

    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = pygame.font.SysFont("Arial", 14, False, False)

    player_one = True  # if a human is playing white, then this will be True, else False
    player_two = False  # if a human is playing white, then this will be True, else False

    while run:
        human_turn = (gs.whiteToMove and player_one) or (
            not gs.whiteToMove and player_two)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    row, col = get_row_col_from_mouse(pygame.mouse.get_pos())
                    # check if the user clicked the same square twice
                    if selected_square == (row, col) or col >= 8:
                        selected_square = ()  # deselect
                        player_clicks = []  # reset player clicks
                    else:
                        selected_square = (row, col)
                        # append for both first and second click
                        player_clicks.append(selected_square)

                    if len(player_clicks) == 2:
                        # after the second click, make the move
                        move = Move(player_clicks[0],
                                    player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_square = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [selected_square]

            # key handler
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:  # undo when 'u' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if event.key == pygame.K_r:  # reset the game when 'r' is pressed
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_square = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

            # AI move finder
            if not game_over and not human_turn and not move_undone:
                if not ai_thinking:
                    ai_thinking = True
                    return_queue = Queue()  # used to pass data between threads
                    move_finder_process = Process(
                        target=find_best_move, args=(gs, valid_moves, return_queue))
                    move_finder_process.start()
                if not move_finder_process.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None:
                        ai_move = find_random_move(valid_moves)
                    gs.make_move(ai_move)
                    move_made = True
                    animate = True
                    ai_thinking = False

        if move_made:
            if animate:
                animateMove(gs.moveLog[-1], win, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_game_state(win, gs, valid_moves, selected_square)

        if not game_over:
            draw_move_log(win, gs, move_log_font)

        if gs.checkmate:
            game_over = True
            if gs.whiteToMove:
                draw_end_game_text(win, "Black wins by checkmate")
            else:
                draw_end_game_text(win, "White wins by checkmate")

        elif gs.stalemate:
            game_over = True
            draw_end_game_text(win, "Stalemate")

        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()
