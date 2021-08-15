"""
The main driver file. It will be responsible for handling user input and displaying the current
GameState object
"""

import pygame
from game_state import GameState
from const import WIDTH, HEIGHT, SQUARE_SIZE, DIMENSIONS, IMAGES
from move import Move
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
    win.fill(pygame.Color("grey"))
    for row in range(DIMENSIONS):
        for col in range(row % 2, DIMENSIONS, 2):
            pygame.draw.rect(win, pygame.Color("WHITE"), (row * SQUARE_SIZE,
                                                          col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


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


def draw_game_state(win: pygame.display, gs: GameState) -> None:
    """
    The function responsible for all the graphics within a current game state
    """
    # draw squares on the board
    draw_board(win)
    # add in piece highlight or move suggestions

    # draw pieces on the board
    draw_pieces(win, gs.board)


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    win.fill(pygame.Color("white"))
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made

    run = True
    # no square is selected, keep track of the last click of the user (row, col)
    selected_square = ()
    # keep track of player clicks (two tuples: [(6, 4), (5, 4)])
    player_clicks = []
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_row_col_from_mouse(pygame.mouse.get_pos())
                # check if the user clicked the same square twice
                if selected_square == (row, col):
                    selected_square = ()  # deselect
                    player_clicks = []  # reset player clicks
                else:
                    selected_square = (row, col)
                    # append for both first and second click
                    player_clicks.append(selected_square)

                if len(player_clicks) == 2:
                    # after the second click, make the move
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                        selected_square = ()  # reset user clicks
                        player_clicks = []
                    else:
                        player_clicks = [selected_square]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:  # undo when 'u' is pressed
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(win, gs)
        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    main()
