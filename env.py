import numpy as np
import tensorflow as tf
from collections import Counter
from agents.random_agent import RandomAgent
from board import TicTacToeBoard


class TicTacToeEnv:
    def __init__(self):
        self.board = TicTacToeBoard()
        self.feature_vector_size = 28
        
        self.sess = None
        with tf.name_scope('random_agent_test_results'):
            self.x_wins_ = tf.placeholder(tf.int32, name='x_wins_')
            self.x_wins = tf.Variable(0, name="x_wins", trainable=False)

            self.x_draws_ = tf.placeholder(tf.int32, name='x_draws_')
            self.x_draws = tf.Variable(0, name="x_draws", trainable=False)

            self.x_losses_ = tf.placeholder(tf.int32, name='x_losses_')
            self.x_losses = tf.Variable(0, name="x_losses", trainable=False)

            self.o_wins_ = tf.placeholder(tf.int32, name='o_wins_')
            self.o_wins = tf.Variable(0, name="o_wins", trainable=False)

            self.o_draws_ = tf.placeholder(tf.int32, name='o_draws_')
            self.o_draws = tf.Variable(0, name="o_draws", trainable=False)

            self.o_losses_ = tf.placeholder(tf.int32, name='o_losses_')
            self.o_losses = tf.Variable(0, name="o_losses", trainable=False)

            self.update_x_wins = tf.assign(self.x_wins, self.x_wins_)
            self.update_x_draws = tf.assign(self.x_draws, self.x_draws_)
            self.update_x_losses = tf.assign(self.x_losses, self.x_losses_)

            self.update_o_wins = tf.assign(self.o_wins, self.o_wins_)
            self.update_o_draws = tf.assign(self.o_draws, self.o_draws_)
            self.update_o_losses = tf.assign(self.o_losses, self.o_losses_)

            self.update_random_agent_test_results = tf.group(*[self.update_x_wins,
                                                               self.update_x_draws,
                                                               self.update_x_losses,
                                                               self.update_o_wins,
                                                               self.update_o_draws,
                                                               self.update_o_losses])
            self.random_agent_test_s = [self.x_wins_,
                                        self.x_draws_,
                                        self.x_losses_,
                                        self.o_wins_,
                                        self.o_draws_,
                                        self.o_losses_]

            tf.summary.scalar("x_wins", self.x_wins)
            tf.summary.scalar("x_draws", self.x_draws)
            tf.summary.scalar("x_losses", self.x_losses)

            tf.summary.scalar("o_wins", self.o_wins)
            tf.summary.scalar("o_draws", self.o_draws)
            tf.summary.scalar("o_losses", self.o_losses)

    def reset(self):
        self.board = TicTacToeBoard()

    def random_position(self):
        self.reset()
        move = np.random.randint(0, 18)
        legal_moves = self.get_legal_moves()
        if move in legal_moves:  # use starting position for moves greater than 8
            self.make_move(move)

    def get_reward(self, board=None):
        if board is None:
            board = self.board
        return board.result()

    def make_move(self, move):
        assert move in self.get_legal_moves()
        self.board.push(move)

    def get_legal_moves(self, board=None):
        if board is None:
            board = self.board
        return board.legal_moves

    def make_feature_vector(self, board):
        fv_size = self.feature_vector_size
        fv = np.zeros((1, fv_size))
        fv[0, :9] = board.xs.reshape(9)
        fv[0, 9:18] = board.os.reshape(9)
        fv[0, 18:27] = ((board.xs + board.os).reshape(9) == 0)
        fv[0, -1] = float(board.turn)
        return fv

    def _print(self, board=None):
        if board is None:
            board = self.board
        s = ''
        for i in range(3):
            s += ' '
            for j in range(3):
                if board.xs[i, j] == 1:
                    s += 'X'
                elif board.os[i, j] == 1:
                    s += 'O'
                else:
                    s += ' '
                if j < 2:
                    s += '|'
            s += '\n'
            if i < 2:
                s += '-------\n'
        print(s)

    def play(self, players, verbose=False):
        while self.get_reward() is None:
            if verbose:
                self._print()
            player = players[int(self.board.turn)]
            move = player.get_move(self)
            self.make_move(move)

        reward = self.get_reward()
        if verbose:
            self._print()
            if reward == 1:
                print("X won!")
            elif reward == -1:
                print("O won!")
            else:
                print("draw")
        return self.get_reward()

    def play_random(self, get_move_function, side):

        self.reset()
        random_agent = RandomAgent()
        if side:
            move_functions = [random_agent.get_move, get_move_function]  # True == 1 == 'X'
        else:
            move_functions = [get_move_function, random_agent.get_move]

        while self.get_reward() is None:
            move_function = move_functions[int(self.board.turn)]
            move = move_function(self)
            self.make_move(move)

        reward = self.get_reward()

        return reward

    def random_agent_test(self, get_move_function):
        x_counter = Counter()
        for _ in range(100):
            self.reset()
            reward = self.play_random(get_move_function, True)
            x_counter.update([reward])

        o_counter = Counter()
        for _ in range(100):
            self.reset()
            reward = self.play_random(get_move_function, False)
            o_counter.update([reward])

        results = [x_counter[1], x_counter[0], x_counter[-1],
                   o_counter[-1], o_counter[0], o_counter[1]]

        self.sess.run(self.update_random_agent_test_results, feed_dict={random_agent_test_: result
                                                                        for random_agent_test_, result in zip(self.random_agent_test_s, results)})
        return results