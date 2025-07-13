import numpy as np
class AIPlayer:
    """
    AI player that uses a neural network to predict moves.
    """
    def __init__(self, game, player, nnet, name, file=None):
        self.game = game
        self.nnet = nnet
        # Find first file in the folder
        if file is None:
            import os
            files = [f for f in os.listdir("models/" + name) if f.endswith('.pth.tar')]
            if files:
                file = files[0]
            else:
                raise FileNotFoundError("No model file found in the specified folder.")
            
        # Load the neural network model
        self.nnet.load_checkpoint(folder="models/" + name, filename=file)
        self.player = player

    def get_action(self, board):
        """Get the next action for the AI player."""

        # Convert board to canonical form
        tensor_board = self.nnet.board_to_tensor(board, self.player)
        can_board = self.game.getCanonicalForm(tensor_board, self.player)
        pi, v = self.nnet.predict(can_board)
        valids = self.game.getValidMoves(can_board, 1)

        # Mask invalid moves
        pi = pi * valids
        sum_pi = np.sum(pi)

        #Normalize probabilities
        if sum_pi > 0:
            pi /= sum_pi

        move = np.argmax(pi)

        self.last_action = move
        move = self.nnet.decode_action(move)
        if self.player == -1:
            move = self.nnet.mirror_action(move) # Mirror action for other player
        return move

    def get_last_action(self):
        """Get the last action taken by the AI player."""
        move = self.nnet.decode_action(move)
        if self.player == -1:
            move = self.nnet.mirror_action(move)
        return move
