import logging

import coloredlogs

from Coach import Coach
from laniakeaSmallMap.LaniakeaGame import LaniakeaGame as Game
from laniakeaSmallMap.pytorch.NNet import NNetWrapper as nn
from utils import *


log = logging.getLogger(__name__)

coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

args = dotdict({
    'numIters': 20, 
    'numEps': 90,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 5,        #
    'updateThreshold': 0.53,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 10000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 20,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 10,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': True,
    'load_folder_file': ('temp','checkpoint_5.pth.tar'),
    'numItersForTrainExamplesHistory': 5,

})


def main():
    log.info('Loading %s...', Game.__name__)
    g = Game()

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)

    if args.load_model:
        log.info('Loading checkpoint "%s/%s"...', args.load_folder_file[0], args.load_folder_file[1])
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    else:
        log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
    c = Coach(g, nnet, args)

    if args.load_model:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')
    c.learn()


if __name__ == "__main__":
    main()
