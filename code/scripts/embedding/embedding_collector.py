import os
import sys
import numpy as np
import pandas as pd
from os.path import join as opj
from shutil import copy2
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
from embedding_config import config


order = sys.argv[1]


# Define some functions ########################################################
def _segments_intersect2d(a1, b1, a2, b2):
    s1 = b1 - a1
    s2 = b2 - a2

    s = (-s1[1] * (a1[0] - a2[0]) + s1[0] * (a1[1] - a2[1])) / (-s2[0] * s1[1]
                                                                + s1[0] * s2[1])
    t = (s2[0] * (a1[1] - a2[1]) - s2[1] * (a1[0] - a2[0])) / (-s2[0] * s1[1]
                                                               + s1[0] * s2[1])

    if (s >= 0) and (s <= 1) and (t >= 0) and (t <= 1):
        return True
    else:
        return False


def n_intersections(x):
    intersections = 0
    for i in np.arange(x.shape[0] - 1):
        a1 = x[i, :]
        b1 = x[i + 1, :]
        for j in np.arange(i + 2, x.shape[0] - 1):
            a2 = x[j, :]
            b2 = x[j + 1, :]

            if _segments_intersect2d(a1, b1, a2, b2):
                intersections += 1
    return intersections


def spatial_similarity(emb, orig_pdist):
    # computes correlation between pairwise distances in embedding space and
    # pairwise distances in original space
    emb_pdist = pdist(emb, 'euclidean')
    # invert values to compare Euclidean distance with correlation
    emb_pdist = 0 - emb_pdist
    return pearsonr(emb_pdist, orig_pdist)[0]


# Main collector script ########################################################
events_dir = opj(config['datadir'], 'events')
results_dir = opj(config['datadir'], 'results')
results_path = opj(results_dir, f'order{order}_results.p')
embeddings_dir = opj(config['datadir'], 'embeddings', f'order{order}')

# load video events in original topic space, pre-compute pairwise distance
video_events = np.load(opj(events_dir, 'video_events.npy'))
topic_space_pdist = 1 - pdist(video_events, 'correlation')

embeddings = os.listdir(embeddings_dir)
results = pd.DataFrame(columns=['intersections', 'spatial_recovery'])

for filename in embeddings:
    emb_path = opj(embeddings_dir, filename)
    param_id = os.path.splitext(filename)[0]
    video_embedding = np.load(emb_path, allow_pickle=True)[0]
    n_intersects = n_intersections(video_embedding)
    spatial_recovery = spatial_similarity(video_embedding, topic_space_pdist)

    results.loc[param_id] = [n_intersects, spatial_recovery]

results.to_pickle(results_path)


# Choose optimal embedding #####################################################
# only run if all other collector scripts have finished
if len(os.listdir(results_dir)) == 6:
    optimized_dir = opj(config['datadir'], 'optimized')
    if not os.path.isdir(optimized_dir):
        os.mkdir(optimized_dir)

    good_embeddings = pd.DataFrame(columns=['spatial_recovery'])
    for order in range(1, 7):
        filepath = opj(results_dir, f'order{order}_results.p')
        results = pd.read_pickle(filepath)
        # consider only embeddings with no intersections
        no_intersections = results.loc[results['intersections'] == 0]
        if no_intersections.empty:
            continue

        for ix in no_intersections.index:
            new_ix = f'order{order}_{ix}'
            no_intersections.loc[new_ix] = no_intersections.loc[ix]

    # select embedding that best reflects shape of 100D video trajectory
    optimal_embedding = good_embeddings['spatial_recovery'].idxmax()
    order, *params = optimal_embedding.split('_')[0]
    source_path = opj(embeddings_dir, order, f"{'_'.join(params)}.npy")
    dest_path = opj(optimized_dir, 'embeddings.npy')
    copy2(source_path, dest_path)
