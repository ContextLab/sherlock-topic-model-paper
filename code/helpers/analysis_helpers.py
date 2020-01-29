# This file contains variables and functions used across multiple analysis
# notebooks (in /code/notebooks/) in a centralized location.  Both variables
# and functions are grouped according to their use

import re
import numpy as np
import pandas as pd
from IPython.display import display, Markdown

# provide link to this file on GitHub for reference
github_link = "https://github.com/contextlab/sherlock-topic-model-paper/blob/master/code/helpers/analysis_helpers.py"
info_msg = Markdown(f"Functions and variables used across multiple notebooks can be found [here]({github_link})")
display(info_msg)


#####################################
#          RE-USED VARIABLES        #
#####################################

# Topic modeling parameters
N_TOPICS = 100
VIDEO_WSIZE = 50
RECALL_WSIZE = 10
VECTORIZER_PARAMS = {
    'model' : 'CountVectorizer',
    'params' : {
        'stop_words' : 'english'
    }
}
SEMANTIC_PARAMS = {
    'model' : 'LatentDirichletAllocation',
    'params' : {
        'n_components' : N_TOPICS,
        'learning_method' : 'batch',
        'random_state' : 0
    }
}




#####################################
#          RE-USED FUNCTIONS        #
#####################################

# text preprocessing
def format_text(text):
    if isinstance(text, pd.Series):
        text = ' '.join(list(text.dropna()))
        pattern = "[^\w\s]+"
    else:
        pattern = "[^.\w\s]+"

    no_possessive = text.lower().replace("'s", '')
    punc_stripped = re.sub(pattern, '', no_possessive)
    spaced = ' '.join(punc_stripped.split())
    return punc_stripped


def parse_windows(textlist, wsize):
    windows = []
    w_lengths = []
    for ix in range(1, wsize):
        start, end = 0, ix
        w_lengths.append((start, end))
        windows.append(' '.join(textlist[start : end]))

    for ix in range(len(textlist)):
        start = ix
        end = ix + wsize if ix + wsize <= len(textlist) else len(textlist)
        w_lengths.append((start, end))
        windows.append(' '.join(textlist[start : end]))

    return windows, w_lengths


def get_video_timepoints(window_spans, annotations):
    timepoints = []
    for first, last in window_spans:
        window_onset = annotations.loc[first, 'Start Time (s) ']
        window_offset = annotations.loc[last - 1, 'End Time (s) ']
        timepoints.append((window_onset + window_offset) / 2)

    return np.array(timepoints)
