from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, Activation, Dropout, Dense, Flatten
from tensorflow.keras.optimizers import Adam

from laniakea.actions import MAX_MOVES  # aus deiner encode_action-Logik

class LaniakeaNNet:
    def __init__(self, game, args):
        # Spielparameter
        self.board_x, self.board_y, self.board_c = game.getBoardSize()  # z. B. 8, 6, 16
        self.args = args

        # Eingabe
        self.input_boards = Input(shape=(self.board_x, self.board_y, self.board_c))  # Kein Reshape nötig

        # Convolutional Backbone
        x = Conv2D(args.num_channels, 3, padding='same')(self.input_boards)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='same')(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='same')(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='valid')(x)  # → kleineres Feature Map
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Flatten()(x)
        x = Dropout(args.dropout)(Activation('relu')(BatchNormalization()(Dense(1024)(x))))
        x = Dropout(args.dropout)(Activation('relu')(BatchNormalization()(Dense(512)(x))))

        # ------- Neue Policy-Heads (aufgeteilt) -------
        self.pi_move1   = Dense(MAX_MOVES, activation='softmax', name='pi_move1')     # z. B. 584
        self.pi_move2   = Dense(MAX_MOVES, activation='softmax', name='pi_move2')     # z. B. 584
        self.pi_insert  = Dense(12,         activation='softmax', name='pi_insert')   # 12 mögliche Insert-Reihen
        self.pi_rotate  = Dense(2,          activation='softmax', name='pi_rotate')   # 0 oder 1

        pi1 = self.pi_move1(x)
        pi2 = self.pi_move2(x)
        pir = self.pi_insert(x)
        rot = self.pi_rotate(x)

        # Value-Head (unverändert)
        self.v = Dense(1, activation='tanh', name='v')(x)

        # Keras-Model
        self.model = Model(inputs=self.input_boards, outputs=[pi1, pi2, pir, rot, self.v])
        self.model.compile(
            loss=['categorical_crossentropy',  # für pi1
                  'categorical_crossentropy',  # für pi2
                  'categorical_crossentropy',  # für insert
                  'categorical_crossentropy',  # für rotate
                  'mean_squared_error'],       # für value
            optimizer=Adam(learning_rate=args.lr)
        )
