# Python Chess Engine

## Table of contents

- [General info](#general-info)
- [Technologies](#technologies)
- [TODO](#todo)
- [Instructions](#instructions)
- [Further development ideas](#further-development-ideas)

## General info

This repository contains a fully functioning GUI chess game with AI with the option of playing against the AI, another player, or AI vs AI.

## Technologies

- Python 3.6 +
- pygame

## TODO

- [ ] Using numpy arrays instead of 2d lists.
- [ ] Stalemate on 3 repeated moves or 50 moves without capture/pawn advancement.
- [ ] Menu to select player vs player/computer.
- [ ] Allow dragging pieces.
- [ ] Resolve ambiguating moves (notation).

## Instructions

1. Clone this repository.
2. Install all the packages in the `requirement.txt` file `pip install -r requirements.txt`.
3. Select whether you want to play versus computer, against another player locally, or watch the game of engine playing against itself by setting appropriate flags in lines 192 and 193 of `main.py`.
4. Run `main.py`.
5. Enjoy the game!

#### Sic:

- Press `u` to undo a move.
- Press `r` to reset the game.

## Further development ideas

1. Ordering the moves (ex. looking at checks and/or captures) should make the engine much quicker (because of the alpha-beta pruning), currently did the basic sort.
2. Keeping track of all the possible moves in a given position, so that after a move is made the engine doesn't have to recalculate all the moves.
3. Evaluating kings placement on the board (separate in middle game and in the late game).
4. Book of openings.
