"""
This class is responsible for storing all the information about the current state of the chess game.
It will also be responsible for determining the valid moves at the current state. It will also keep
a move log
"""

from move import Move
from castle_right import CastleRights


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

        # game results
        self.checkmate = False
        self.stalemate = False

        # king locations
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)

        # checks
        self.inCheck = False
        self.pins = []  # pieces that have pin
        self.check = []  # piece that attack the oppenent king

        # enpassant
        self.enpassant_possible = ()  # cordinates for the square where en-passent is possible
        self.enpassant_possible_log = [self.enpassant_possible]

        # castling
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def make_move(self, move: Move) -> None:
        """
        The function apply the move to the board (this will not work for castling, en-passent and promotion)
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        # save the move
        self.moveLog.append(move)
        # swap players
        self.whiteToMove = not self.whiteToMove
        # update king's location if moved
        if move.piece_moved == "wK":
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # promoted_piece = input("Promote to Q, R, B or N: ")
            # self.board[move.end_row][move.end_col] = f"{move.piece_moved[0]}{promoted_piece}"
            self.board[move.end_row][move.end_col] = f"{move.piece_moved[0]}Q"

        # enpassant move
        if move.is_enpassant_move:
            # capturing the pawn
            self.board[move.start_row][move.end_col] = "--"

        # update enpassant_possible variable
        # only on 2 square pawn promote
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = (
                (move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king-side castle move
                # moves the rook to its new square
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]
                # erase old rook
                self.board[move.end_row][move.end_col +
                                         1] = "--"
            else:  # queen-side castle move
                # moves the rook to its new square
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]
                # erase old rook
                self.board[move.end_row][move.end_col -
                                         2] = "--"

        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castling rights - whenever it is a rook or king move
        self.update_castling_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    def undo_move(self) -> None:
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
            # update king's location if needed
            if move.piece_moved == "wK":
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_loc = (move.start_row, move.start_col)

            # undo enpassant move
            if move.is_enpassant_move:
                # leave landing square empty
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # undo castle rights
            # get rid of the new castle rights from the move we are undoing
            self.castle_rights_log.pop
            # set the current castle rights to the last one in the list
            self.current_castling_rights = self.castle_rights_log[-1]
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side castle
                    self.board[move.end_row][move.end_col +
                                             1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side castle
                    self.board[move.end_row][move.end_col -
                                             2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            # update results
            self.checkmate = False
            self.stalemate = False

    def update_castling_rights(self, move: Move) -> None:
        """
        The function updates the castling rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False

    def in_check(self) -> bool:
        """
        The function determines if the current player is in check
        """
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, row: int, col: int) -> bool:
        """
        The function determines if the enemy player can attack the square (row, col)
        """
        self.whiteToMove = not self.whiteToMove
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opp_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def check_for_pins_and_checks(self) -> tuple:
        """
        The function returns if the player is in check, a list of pins and a list of checks
        """
        pins = []  # squares where the allied pinned piece is and the direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row, start_col = self.white_king_loc[0], self.white_king_loc[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row, start_col = self.black_king_loc[0], self.black_king_loc[1]

        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row, end_col = start_row + d[0] * i, start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # second allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 possibilities here
                        # 1.) orthogonally away from the king and piece is a rook
                        # 2.) diagonally away from the king and the piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and the piece is the queen
                        # 5.) any direction 1 square away and piece is a king (this is necessary to
                        # prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and piece_type == "R") or (4 <= j <= 7 and piece_type == "B") \
                                or (i == 1 and piece_type == "p" and ((enemy_color == "w" and 6 <= j <= 7)
                                                                      or (enemy_color == "b" and 4 <= j <= 5))) or (piece_type == "Q") \
                                or (i == 1 and piece_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking, so pin
                                pins.append(possible_pin)
                                break
                        else:  # the enemy piece don't apply check
                            break
                else:
                    break  # off board

        # look for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, -1))
        for m in knight_moves:
            end_row, end_col = start_row + m[0], start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight
                    inCheck = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return inCheck, pins, checks

    def get_valid_moves(self) -> list:
        """
        All moves considering checks
        """
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)

        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row, king_col = self.white_king_loc[0], self.white_king_loc[1]
        else:
            king_row, king_col = self.black_king_loc[0], self.black_king_loc[1]

        if self.inCheck:
            if len(self.checks) == 1:  # there is only 1 check, block or move the king
                moves = self.get_all_possible_moves()
                # to block a check you must move a piece into one of the squares between
                # the enemy piece and king
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                # enemy piece causing the check
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that the piece can move to
                # if knight, must capture or move king, other piece can block
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(8):
                        valid_square = (
                            king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        # once you get to piece end checks
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    # move doesn't move king so it must be block or capture
                    if moves[i].piece_moved[1] != "K":
                        # move doesn't block check or capture piece
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in checks so all moves are fine
            moves = self.get_all_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(
                    self.white_king_loc[0], self.white_king_loc[1], moves)
            else:
                self.get_castle_moves(
                    self.black_king_loc[0], self.black_king_loc[1], moves)

        if len(moves) == 0:  # either a checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True

        # update the current castling rights
        self.current_castling_rights = temp_castle_rights
        return moves

    def get_all_possible_moves(self) -> list:
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

    def get_pawn_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the pawn moves for the pawn located at (row, col) and add these moves to the list of moves
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_loc
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_loc

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(
                    Move((row, col), (row + move_amount, col), self.board))
                # 2 square pawn advance
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":
                    moves.append(
                        Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(
                        Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            # some piece beside en-passant pawn blocks
                            if self.board[row][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move(
                            (row, col), (row + move_amount, col - 1), self.board, is_enpassant_move=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(
                        Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            # some piece beside en-passant pawn blocks
                            if self.board[row][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move(
                            (row, col), (row + move_amount, col + 1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the rook moves for the rook located at (row, col) and add these moves to the list of moves
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from rook moves, only remove it on bishop
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        dir = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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

    def get_knight_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the knight moves for the knight located at (row, col) and add these moves to the list of moves
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        dir = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
               (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for d in dir:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    # not an ally piece (empty or enemy piece)
                    if end_piece[0] != ally_color:
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the bishop moves for the bishop located at (row, col) and add these moves to the list of moves
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        dir = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in dir:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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

    def get_queen_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the queen moves for the queen located at (row, col) and add these moves to the list of moves
        """
        # the queen moves like the rook and the bishop combined
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row: int, col: int, moves: list) -> None:
        """
        Get all the king moves for the king located at (row, col) and add these moves to the list of moves
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row, end_col = row + row_moves[i], col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece, empty or enemy
                    # place king on end square and look for checks
                    if ally_color == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    inCheck, pins, checks = self.check_for_pins_and_checks()
                    if not inCheck:
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)

    def get_castle_moves(self, row: int, col: int, moves: list) -> None:
        """
        The function generates all the valid castle moves for the king at (row, col) and adds them 
        to the list of moves
        """
        if self.square_under_attack(row, col):
            return  # can't castlr while in check
        if (self.whiteToMove and self.current_castling_rights.wks) or (
                not self.whiteToMove and self.current_castling_rights.bks):
            self.get_king_side_castle_moves(row, col, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (
                not self.whiteToMove and self.current_castling_rights.bqs):
            self.get_queen_side_castle_moves(row, col, moves)

    def get_king_side_castle_moves(self, row: int, col: int, moves: list) -> None:
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2),
                                  self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, row: int, col: int, moves: list) -> None:
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2),
                                  self.board, is_castle_move=True))
