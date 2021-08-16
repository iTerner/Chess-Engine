from const import RANK2ROW, ROW2RANK, FILES2COLS, COL2FILE


class Move:
    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row, self.start_col = start_square[0], start_square[1]
        self.end_row, self.end_col = end_square[0], end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        # could be a piece or empty square ("--")
        self.piece_captured = board[self.end_row][self.end_col]

        self.move_id = self.start_row * 1000 + self.start_col * \
            100 + self.end_row * 10 + self.end_col

        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
            self.piece_moved == "bp" and self.end_row == 7)

        # enpassent move
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # castle move
        self.is_castle_move = is_castle_move

        self.is_capture = self.piece_captured != "--"

    def __eq__(self, other: object) -> bool:
        """
        Overriding the equals method 
        """
        if isinstance(other, Move):
            if self.move_id == other.move_id:
                return True
        return False

    def get_rank_file(self, row: int, col: int) -> str:
        """
        The function compute and return the chess notation for the square
        """
        return COL2FILE[col] + ROW2RANK[row]

    def get_chess_notation(self) -> str:
        """
        The function compute and return the move chess notation.
        """
        if self.is_pawn_promotion:
            return self.get_rank_file(self.end_row, self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_enpassant_move:
            return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                    self.end_col) + " e.p."
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":
                return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                        self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.get_rank_file(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.get_rank_file(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.get_rank_file(self.end_row, self.end_col)

        # TODO Disambiguating moves

    def __str__(self) -> str:
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.get_rank_file(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return COL2FILE[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square
