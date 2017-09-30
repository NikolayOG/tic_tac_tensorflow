import tensorflow as tf
from envs.tic_tac_toe import TicTacToeEnv


class ValueModel:
    def __init__(self, hidden_dim=1000):
        fv_size = TicTacToeEnv.get_feature_vector_size()

        self.feature_vector_ = tf.placeholder(tf.float32, shape=[None, fv_size], name='feature_vector_')
        self.keep_prob_ = tf.placeholder(tf.float32, name='keep_prob_')

        with tf.variable_scope('layer_1'):
            W_1 = tf.get_variable('W_1',
                                  shape=[fv_size, hidden_dim],
                                  initializer=tf.contrib.layers.xavier_initializer())
            hidden_1 = tf.nn.relu(tf.matmul(self.feature_vector_, W_1), name='hidden_1')

        with tf.variable_scope('layer_2'):
            W_2 = tf.get_variable('W_2', shape=[hidden_dim, 1],
                                  initializer=tf.contrib.layers.xavier_initializer())
            self.value = tf.tanh(tf.matmul(hidden_1, W_2), name='value')

        self.trainable_variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                                     scope=tf.get_variable_scope().name)

    def value_function(self, sess):
        def f(fv):
            value = sess.run(self.value, feed_dict={self.feature_vector_: fv})
            return value
        return f

