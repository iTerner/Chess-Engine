import random


def find_random_move(valid_moves):
    """
    The function choose a random move for the AI
    """
    return valid_moves[random.randint(0, len(valid_moves) - 1)]
