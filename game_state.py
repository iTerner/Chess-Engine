"""
This class is responsible for storing all the information about the current state of the chess game.
It will also be responsible for determining the valid moves at the current state. It will also keep
a move log
"""

from move import Move


class GameState:
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, "b" or "w"
        # The second character represents the type of the piece, "K", "Q", "B", "N", "R" or "P"
        # the string "--" represents an empty square
        self.board = [
            ["bR", "bN", "bB", "bK", "bQ", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wK", "wQ", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []

    def make_move(self, move: Move):
        """
        The function apply the move to the board
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        # save the move
        self.moveLog.append(move)
        # swap players
        self.whiteToMove = not self.whiteToMove
