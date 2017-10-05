import numpy as np
from copy import deepcopy


class TicTacToeBoard:
    def __init__(self):
        self.xs = np.zeros((3, 3))
        self.os = np.zeros((3, 3))
        self._legal_moves = np.arange(9)
        self._turn = True
        self.move_stack = []

    @property
    def turn(self):
        return self._turn

    @property
    def legal_moves(self):
        return self._legal_moves

    def push(self, move):
        row = int(move / 3)
        col = move % 3

        assert self.xs[row, col] == 0
        assert self.os[row, col] == 0
        if self.turn:
            self.xs[row, col] = 1
        else:
            self.os[row, col] = 1
        self.move_stack.append(3 * row + col)
        self._turn = not self._turn
        self._legal_moves = np.where((self.xs + self.os).reshape(9) == 0)[0]

    def is_game_over(self):
        return self.result() is not None

    def result(self):
        if any(self.xs.sum(axis=0) == 3.0) or any(self.xs.sum(axis=1) == 3.0) or self.xs[np.eye(3) == 1.0].sum() == 3.0 or self.xs[np.rot90(np.eye(3)) == 1].sum() == 3.0:
            return 1.0
        elif any(self.os.sum(axis=0) == 3.0) or any(self.os.sum(axis=1) == 3.0) or self.os[np.eye(3) == 1.0].sum() == 3.0 or self.os[np.rot90(np.eye(3)) == 1].sum() == 3.0:
            return -1.0
        elif (self.xs + self.os).sum() == 9:
            return 0.0
        else:
            return None

    def copy(self):
        return deepcopy(self)