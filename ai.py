"""
Handling the AI moves.
"""

import random
from game_state import GameState
from move import Move
from multiprocessing import Queue


PIECE_SCORE = {"K": 200, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

KNIGHT_SCORE = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

BISHOP_SCORE = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

ROOK_SCORE = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
              [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
              [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

QUEEN_SCORE = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
               [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
               [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
               [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
               [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
               [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
               [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
               [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

PAWN_SCORE = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
              [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
              [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
              [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
              [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
              [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
              [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
              [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

PIECE_POSITION_SCORE = {"wN": KNIGHT_SCORE,
                        "bN": KNIGHT_SCORE[::-1],
                        "wB": BISHOP_SCORE,
                        "bB": BISHOP_SCORE[::-1],
                        "wQ": QUEEN_SCORE,
                        "bQ": QUEEN_SCORE[::-1],
                        "wR": ROOK_SCORE,
                        "bR": ROOK_SCORE[::-1],
                        "wp": PAWN_SCORE,
                        "bp": PAWN_SCORE[::-1]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def move_sort(gs: GameState, valid_moves: list) -> list:
    """
    The function sort the moves by thier priority
    """
    # convert each move into a tuple where each field represent different type of move
    # 1: if the move contains checkmate 1, otherwise 0
    # 2: if the move contains check 1, otherwise 0
    # 3: if the move contains promotion 1, otherwise 0
    # 4: if the move contains capture 1, otherwise 0
    tmp_moves = {}
    for i in range(len(valid_moves)):
        checkmate, check, promotion, capture = 0, 0, 0, 0
        move = valid_moves[i]
        gs.make_move(move)
        if gs.inCheck:
            check = 1
        if gs.checkmate:
            checkmate = 1
        gs.undo_move()
        if move.is_pawn_promotion:
            promotion = 1
        if move.is_capture:
            capture = 1
        tmp_moves[i] = [checkmate, check, promotion, capture, move]

    # sort the dictionary by the priority
    sorted_list = sorted(tmp_moves.values(),
                         key=lambda x: (x[0], x[1]), reverse=True)
    sorted_moves = [move for _, _, _, _, move in sorted_list]
    return sorted_moves


def find_best_move(gs: GameState, valid_moves: list, return_queue: Queue) -> None:
    global next_move
    next_move = None
    # random.shuffle(valid_moves)

    # sort the moves
    sorted_moves = move_sort(gs, valid_moves)

    # add book move data base

    # find the best move
    find_move_nega_max_alpha_beta(gs, sorted_moves, DEPTH, -CHECKMATE, CHECKMATE,
                                  1 if gs.whiteToMove else -1)
    return_queue.put(next_move)


def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)
    # move ordering - implement later //TODO
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves,
                                               depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(gs):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = PIECE_POSITION_SCORE[piece][row][col]
                if piece[0] == "w":
                    score += PIECE_SCORE[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= PIECE_SCORE[piece[1]] + piece_position_score

    return score


def find_random_move(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)
