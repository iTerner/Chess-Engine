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
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []

    def make_move(self, move: Move):
        """
        The function apply the move to the board (this will not work for castling, en-passent and promotion)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        # save the move
        self.moveLog.append(move)
        # swap players
        self.whiteToMove = not self.whiteToMove

    def undo_move(self):
        """
        The function undo the last move
        """
        # make sure there is a move to undo
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            # switch turn
            self.whiteToMove = not self.whiteToMove

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        return self.get_all_possible_moves()  # for now we will not worry about checks

    def get_pawn_moves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_rook_moves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_knight_moves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_bishop_moves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_queen_moves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_king_moves(self, row, col, moves):
        """
        Get all the king moves for the king located at (row, col) and add these moves to the list of moves
        """
        pass

    def get_all_possible_moves(self):
        """
        All the possible moves without considering checks
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                piece = self.board[row][col][1]
                if (turn == "w" and self.whiteToMove) and (turn == "b" and not self.whiteToMove):
                    if piece == "p":
                        self.get_pawn_moves(row, col, moves)
                    elif piece == "R":
                        self.get_rook_moves(row, col, moves)

        return moves
