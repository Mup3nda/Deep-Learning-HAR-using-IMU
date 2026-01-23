import json
import tensorflow.compat.v1 as tf
from tensorflow.python.ops import rnn_cell_impl
import logging
import os


tf.disable_v2_behavior()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class ModelLoader:

    def __init__(self, model_path):
        logger.info("Initialize model configuration")
        self.model_path = model_path
        self.model_config()
        self.build_graph()

    def model_config(self):
        '''Load model configuration trained LSTM models'''
        config_path = f"{self.model_path}/model_info.json"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Can't locate file: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.n_hidden = config['n_hidden']
        self.n_classes = config['n_classes']
        self.n_steps = config['n_steps']
        self.n_input = config['n_input']
        self.model_version = self.model_path.split('/')[-1]

        logger.info(f"✅ Loaded model config: {self.model_version}")


    def build_graph(self):
        tf.reset_default_graph()

        self.x = tf.placeholder(tf.float32, [None, self.n_steps, self.n_input], name='input_x')

        self.weight = {
            'hidden': tf.Variable(tf.random_normal([self.n_input, self.n_hidden]), name='weights_hidden'),
            'out': tf.Variable(tf.random_normal([self.n_hidden, self.n_classes], mean=1.0), name='weights_out')
        }

        self.bias = {
            'hidden': tf.Variable(tf.random_normal([self.n_hidden]), name='biases_hidden'),
            'out': tf.Variable(tf.random_normal([self.n_classes]), name='biases_out')
        }

        self.pred = self._lstm_network(self.x, self.weight, self.bias)
        self.saver = tf.train.Saver()

        logger.info("Model graph built")


    def _lstm_network(self, _X, _weights, _biases):
        _X = tf.transpose(_X, [1, 0, 2])
        _X = tf.reshape(_X, [-1, self.n_input])
        _X = tf.nn.relu(tf.matmul(_X, _weights['hidden']) + _biases['hidden'])
        _X = tf.split(_X, self.n_steps, 0)

        lstm_cell_1 = rnn_cell_impl.LSTMCell(self.n_hidden, forget_bias=1.0)
        lstm_cell_2 = rnn_cell_impl.LSTMCell(self.n_hidden, forget_bias=1.0)
        lstm_cells = rnn_cell_impl.MultiRNNCell([lstm_cell_1, lstm_cell_2])

        outputs, states = tf.nn.static_rnn(lstm_cells, _X, dtype=tf.float32)
        return tf.matmul(outputs[-1], _weights['out']) + _biases['out']

    def restore_session(self):
        sess = tf.Session()
        self.saver.restore(sess, f"{self.model_path}/model.ckpt")
        logger.info(f"✅ Model restored succesfully!")
        return sess


def main():
    model_path = '../model/lstm_model_v002'
    loader = ModelLoader(model_path)

if __name__ == '__main__':
    main()


