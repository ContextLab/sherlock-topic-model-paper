# This file contains variables and functions used across multiple analysis
# notebooks (in /code/notebooks/) in a centralized location.  Both variables
# and functions are grouped according to their use, and tagged with the notebooks
# in which they're imported for easy searching

import re
import numpy as np
import pandas as pd
from fastdtw import fastdtw
from IPython.display import display, Markdown
from scipy.spatial.distance import correlation

import matplotlib.patches as patches

# provide link to this file on GitHub for reference
github_link = "https://github.com/contextlab/sherlock-topic-model-paper/blob/master/code/helpers/analysis_helpers.py"
info_msg = Markdown(f"Functions and variables used across multiple notebooks can be found [here]({github_link})")
display(info_msg)


#####################################
#          RE-USED VARIABLES        #
#####################################

# topic modeling parameters
# topic_model_analysis.ipynb, feature_contribution.ipynb, feature_similarity.ipynb, precision_detail.ipynb
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

# scale for embedding-space trajectory figures
# trajectory_analysis_and_fig.ipynb, wordle_analysis_and_fig.ipynb
SCALE = 30

# hand-annotated memory performance & number of HMM-identified recall events
# eventseg_analysis.ipynb, list-learning_analysis.ipynb, precision_distinctiveness_fig.ipynb
HAND_REC = np.array([27, 24, 32, 33, 32, 39, 30, 39, 28, 40, 34, 38, 47, 38, 27, 37, 39])
# list-learning_analysis.ipynb, precision_distinctiveness_fig.ipynb
N_REC_EVENTS = np.array([11, 16, 12, 10, 10, 12, 11, 16, 14, 15, 15, 23, 29, 16, 13, 17, 22])


#####################################
#          RE-USED FUNCTIONS        #
#####################################

# text preprocessing
# topic_model_analysis.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
def format_text(text):
    if isinstance(text, pd.Series):
        text = ' '.join(list(text.dropna()))
        pattern = "[^\w\s]+"
    else:
        pattern = "[^.\w\s]+"

    no_possessive = text.lower().replace("'s", '')
    punc_stripped = re.sub(pattern, '', no_possessive)
    return punc_stripped


# topic_model_analysis.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
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


# topic_model_analysis.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
def get_video_timepoints(window_spans, annotations):
    timepoints = []
    for first, last in window_spans:
        window_onset = annotations.loc[first, 'Start Time (s) ']
        window_offset = annotations.loc[last - 1, 'End Time (s) ']
        timepoints.append((window_onset + window_offset) / 2)

    return np.array(timepoints)


# dynamic time-warping recall trajectories
# searchlight_fig.ipynb, feature_contribution.ipynb
def warp_recall(recall_traj, video_traj, return_paths=False):
    dist, path = fastdtw(video_traj, recall_traj, dist=correlation)
    recall_path = [i[1] for i in path]
    warped_recall = recall_traj[recall_path]
    if return_paths:
        video_path = [i[0] for i in path]
        return warped_recall, video_path, recall_path
    else:
        return warped_recall


# masking long-timescale temporal correlations
# searchlight_fig.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
def kth_diag_indices(arr, k):
    row_ix, col_ix = np.diag_indices_from(arr)
    return row_ix[:-k], col_ix[k:]


# searchlight_fig.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
def find_diag_limit(corrmat):
    for k in range(corrmat.shape[0]):
        d = np.diag(corrmat, k=k)
        if ~(d > 0).any():
            return k


# searchlight_fig.ipynb, feature_contribution.ipynb, feature_similarity.ipynb
def create_diag_mask(corrmat, diag_limit=None):
    diag_mask = np.zeros_like(corrmat, dtype=bool)
    if diag_limit is None:
        diag_limit = find_diag_limit(corrmat)
    for k in range(1, diag_limit):
        ix = kth_diag_indices(diag_mask, k)
        diag_mask[ix] = True
    return diag_mask


# Fisher Z-transformation & inverse transformation
# precision_distinctiveness_fig.ipynb, searchlight_analyses.ipynb, wordle_analysis_and_fig.ipynb
def r2z(r):
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


# wordle_analysis_and_fig.ipynb
def z2r(z):
    with np.errstate(invalid='ignore', divide='ignore'):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


# wordle_analysis_and_fig.ipynb
def corr_mean(rs, axis=0):
    return z2r(np.nanmean([r2z(r) for r in rs], axis=axis))


# plotting temporal correlation matrices
# eventseg_fig.ipynb, corrmats.ipynb
def draw_bounds(ax, model):
    bounds = np.where(np.diff(np.argmax(model.segments_[0], axis=1)))[0]
    bounds_aug = np.concatenate(([0],bounds,[model.segments_[0].shape[0]]))
    for i in range(len(bounds_aug)-1):
        rect = patches.Rectangle((bounds_aug[i], bounds_aug[i]), bounds_aug[i+1]-bounds_aug[i],
                                 bounds_aug[i+1]-bounds_aug[i], linewidth=1, edgecolor='#FFF9AE',
                                 facecolor='none')
        ax.add_patch(rect)
    return ax


# adding arrows to trajectory embedding plots
# trajectory_analysis_and_fig.ipynb, wordle_analysis_and_fig.ipynb
def add_arrows(axes, x, y, **kwargs):
    # spacing of arrows
    aspace = .05
    aspace *= SCALE
    # r is the distance spanned between pairs of points
    r = [0]
    for i in range(1,len(x)):
        dx = x[i]-x[i-1]
        dy = y[i]-y[i-1]
        r.append(np.sqrt(dx*dx+dy*dy))
    r = np.array(r)
    # rtot is a cumulative sum of r, it's used to save time
    rtot = []
    for i in range(len(r)):
        rtot.append(r[0:i].sum())
    rtot.append(r.sum())
    arrowData = [] # will hold tuples of x,y,theta for each arrow
    arrowPos = 0 # current point on walk along data
    rcount = 1
    while arrowPos < r.sum():
        x1,x2 = x[rcount-1],x[rcount]
        y1,y2 = y[rcount-1],y[rcount]
        da = arrowPos-rtot[rcount]
        theta = np.arctan2((x2-x1),(y2-y1))
        ax = np.sin(theta)*da+x1
        ay = np.cos(theta)*da+y1
        arrowData.append((ax,ay,theta))
        arrowPos+=aspace
        while arrowPos > rtot[rcount+1]:
            rcount+=1
            if arrowPos > rtot[-1]:
                break

    # could be done in above block if you want
    for ax,ay,theta in arrowData:
        # use aspace as a guide for size and length of things
        # scaling factors were chosen by experimenting a bit
        axes.arrow(ax,ay,
                   np.sin(theta)*aspace/10,np.cos(theta)*aspace/10,
                   head_width=aspace/3, **kwargs)
