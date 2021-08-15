from const import RANK2ROW, ROW2RANK, FILES2COLS, COL2FILE


class Move:
    def __init__(self, start_square, end_square, board):
        self.start_row, self.start_col = start_square[0], start_square[1]
        self.end_row, self.end_col = end_square[0], end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        # could be a piece or empty square ("--")
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * \
            100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """
        Overriding the equals method 
        """
        if isinstance(other, Move):
            if self.move_id == other.move_id:
                return True
        return False

    def get_chess_notation(self) -> str:
        """
        The function compute and return the move chess notation.
        """
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row: int, col: int) -> str:
        """
        The function compute and return the chess notation for the square
        """
        return COL2FILE[col] + ROW2RANK[row]
