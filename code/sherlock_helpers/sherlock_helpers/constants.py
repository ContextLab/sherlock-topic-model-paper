"""
This module contains variables and constant values used across multiple
analysis notebooks in a centralized location.
"""
from pathlib import Path
import numpy as np

# paths for loading data and saving figures
RAW_DIR = Path('/mnt/data/raw')
DATA_DIR = RAW_DIR.parent.joinpath('processed')
FIG_DIR = Path('/mnt/paper/figs')


# video sliding window length (in annotations)
VIDEO_WSIZE = 50
# recall sliding window length (in sentences)
RECALL_WSIZE = 10
# text vectorizer parameters
VECTORIZER_PARAMS = {
    'model': 'CountVectorizer',
    'params': {
        'stop_words': 'english'
    }
}
# topic model parameters
SEMANTIC_PARAMS = {
    'model': 'LatentDirichletAllocation',
    'params': {
        'n_components': 100,
        'learning_method': 'batch',
        'random_state': 0
    }
}


# hand-annotated memory performance for each participant (from Chen et al., 2017)
HAND_REC = np.array([27, 24, 32, 33, 32, 39, 30, 39,
                     28, 40, 34, 38, 47, 38, 27, 37, 39])
# number of HMM-identified recall events for each participant
N_REC_EVENTS = np.array([11, 16, 12, 10, 10, 12, 11, 16,
                         14, 15, 15, 23, 29, 16, 13, 17, 22])

# min and max x- and y-bound for embedding space grid
SCALE = 30
