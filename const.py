import pygame

WIDTH, HEIGHT = 512, 512
ROWS, COLS = 8, 8
DIMENSIONS = ROWS
SQUARE_SIZE = WIDTH // COLS

# LOAD IMAGES
pieces = ["wp", "wR", "wN", "wB", "wQ",
          "wK", "bp", "bR", "bN", "bB", "bK", "bQ"]
IMAGES = {}
for piece in pieces:
    IMAGES[piece] = pygame.image.load(f"images/{piece}.png")

# row, col names map
RANK2ROW = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
ROW2RANK = {v: k for k, v in RANK2ROW.items()}

FILES2COLS = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
COL2FILE = {v: k for k, v in FILES2COLS.items()}
