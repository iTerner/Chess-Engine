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
        self.moveFunctions = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves
        }

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
        if self.whiteToMove:  # white pawn moves
            if self.board[row - 1][col] == "--":  # one square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                # 2 2 square pawn advance
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # capturing left
                if self.board[row - 1][col - 1][0] == "b":  # there is enemy piece
                    moves.append(
                        Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # capturing right
                if self.board[row - 1][col + 1][0] == "b":  # there is enemy piece
                    moves.append(
                        Move((row, col), (row - 1, col + 1), self.board))

        else:  # black pawn moves
            if self.board[row + 1][col] == "--":  # one square pawn advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                # 2 2 square pawn advance
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # capturing left
                if self.board[row + 1][col - 1][0] == "w":  # there is enemy piece
                    moves.append(
                        Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # capturing right
                if self.board[row + 1][col + 1][0] == "w":  # there is enemy piece
                    moves.append(
                        Move((row, col), (row + 1, col + 1), self.board))

        # pawn promotion

    def get_rook_moves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at (row, col) and add these moves to the list of moves
        """
        dir = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty piece vaild
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # same color piece, not valid
                        break
                else:
                    # off board not valid
                    break

    def get_knight_moves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at (row, col) and add these moves to the list of moves
        """
        dir = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, -1))
        ally_color = "w" if self.whiteToMove else "b"
        for d in dir:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # not an ally piece (empty or enemy piece)
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at (row, col) and add these moves to the list of moves
        """
        dir = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty piece vaild
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece valid
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # same color piece, not valid
                        break
                else:
                    # off board not valid
                    break

    def get_queen_moves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at (row, col) and add these moves to the list of moves
        """
        # the queen moves like the rook and the bishop combined
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        """
        Get all the king moves for the king located at (row, col) and add these moves to the list of moves
        """
        dir = ((-1, 1), (-1, 0), (-1, -1), (0, 1),
               (0, -1), (1, 1), (1, 0), (1, -1))
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + dir[i][0]
            end_col = col + dir[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # not an ally piece (empty or enemy piece)
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_all_possible_moves(self):
        """
        All the possible moves without considering checks
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                piece = self.board[row][col][1]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    # call the function based on the piece type
                    self.moveFunctions[piece](row, col, moves)

        return moves
