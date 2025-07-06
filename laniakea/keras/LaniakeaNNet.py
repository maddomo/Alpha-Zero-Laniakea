from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, Activation, Dropout, Dense, Flatten
from tensorflow.keras.optimizers import Adam

class LaniakeaNNet():
    def __init__(self, game, args):
        # Game parameters
        self.board_x, self.board_y, self.board_c = game.getBoardSize()  # 8, 6, 16
        self.action_size = game.getActionSize()
        self.args = args

        # Neural Network architecture
        self.input_boards = Input(shape=(self.board_x, self.board_y, self.board_c))  # No need to reshape!
        x = Conv2D(args.num_channels, 3, padding='same')(self.input_boards)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='same')(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='same')(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Conv2D(args.num_channels, 3, padding='valid')(x)
        x = BatchNormalization(axis=-1)(x)
        x = Activation('relu')(x)

        x = Flatten()(x)
        x = Dropout(args.dropout)(Activation('relu')(BatchNormalization()(Dense(256)(x))))
        x = Dropout(args.dropout)(Activation('relu')(BatchNormalization()(Dense(128)(x))))

        self.pi = Dense(self.action_size, activation='softmax', name='pi')(x)  # Policy head
        self.v = Dense(1, activation='tanh', name='v')(x)  # Value head

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(
            loss=['categorical_crossentropy', 'mean_squared_error'],
            optimizer=Adam(learning_rate=args.lr)
        )