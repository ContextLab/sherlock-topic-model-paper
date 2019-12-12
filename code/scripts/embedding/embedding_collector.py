import os
import pickle
from shutil import copy2
import numpy as np
import pandas as pd
from os.path import join as opj
from scipy.spatial.distance import pdist, cdist
from embedding_config import config

try:
    from tqdm import trange
    range_ = trange
except ModuleNotFoundError:
    range_ = range

SEEDS = list(range(10001))
# PERCENTILE = 99.95
# METRICS = ['dispersion', 'intersections']
# WEIGHTS = {
#     'dispersion': .5,
#     'intersections': .5
# }

# METRICS = ['intersections']
# WEIGHTS = {
#     'intersections': 1
# }

# METRICS = ['dispersion']
# WEIGHTS = {
#     'dispersion': 1
# }

# METRICS = ['dispersion', 'intersections']
# WEIGHTS = {
#     'dispersion': .75,
#     'intersections': .25
# }

METRICS = ['dispersion', 'intersections']
WEIGHTS = {
    'dispersion': .25,
    'intersections': .75
}

events_dir = opj(config['datadir'], 'events')
embeddings_dir = opj(config['datadir'], 'embeddings')
optimized_dir = opj(config['datadir'], 'optimized')


# Define some functions ########################################################
def r2z(r):
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


def spatial_similarity(embedding, original_pdist, emb_metric):
    """
    computes correlation between pairwise euclidean distance in embedding space
    and correlation distance in original space
    """
    emb_pdist = pdist(embedding, emb_metric)
    if emb_metric == 'correlation':
        emb_pdist = 1 - emb_pdist
    return 1 - pdist((emb_pdist, original_pdist), 'correlation')[0]


# source: https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
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


def dispersion_dist(emb):
    # normalize to fit in unit square
    scaled = ((emb - emb.min(0))*2 / (emb.max(0) - emb.min(0))) - 1
    avg_point = scaled.mean(0)
    return cdist(np.atleast_2d(avg_point), scaled, 'euclidean').mean()

# OLD OPTIMIZE_EMBEDDING function
# def optimize_embedding(opt_results, seeds=None, metrics=None, weights=None, percentile=-1):
#     """
#     chooses an optimal UMAP embedding based on a weighted combination of
#     optimization metrics
#     Parameters
#     ----------
#     opt_results :   dict
#                     dictionary of {optimization metric: array}
#                     where the array holds the results of the optimization
#                     metric for each seed
#
#     seeds       :   list-like (default None)
#                     random seed numbers corresponding to the indices of arrays
#                     in opt_results.  Useful when optimizing over a range of
#                     seeds that doesn't start at 0 or is unordered.  Defaults to
#                     indices of opt_results arrays.
#
#     metrics     :   list-like (default None)
#                     which metrics to consider in optimization. If None, all
#                     metrics are considered
#
#     weights     :   dict (default None)
#                     weights (values) to apply to optimization metrics (keys)
#                     considered. If None, all metrics are weighted equally.
#
#     percentile  :   int or float (default -1)
#                     The percentile above which "optimal" embeddings (by the
#                     weighted combination of metrics) will be returned.  If
#                     -1, only the single best embedding is returned.
#
#     Returns
#     ----------
#     optimal_embs : dict
#                    a nested dictionary of {rectype: {optimal seed: embedding}}
#
#     """
#     if not metrics:
#         metrics = list(opt_results.keys())
#     if not weights:
#         weights = {m: 1 / len(metrics) for m in metrics}
#     if not seeds:
#         seeds = np.arange(len(opt_results[metrics[0]]))
#     seeds = np.array(seeds)
#
#     assert sum(weights.values()) == 1, 'weights must sum to 1'
#     assert metrics == list(weights.keys()), 'you must pass a weight value for each metric considered'
#     assert all(seeds.shape == opt_results[m].shape for m in metrics), 'number of seeds must match the number of results'
#
#     scores = pd.DataFrame()
#     for metric in metrics:
#         asc = False if metric == 'intersections' else True
#         res = pd.Series(opt_results[metric])
#         scores[metric] = res.rank(pct=True, ascending=asc)
#
#     scores.index = seeds
#     weighted = (scores * weights).sum(axis=1)
#
#     if percentile == -1:
#         optimal_seeds = weighted.idxmax()
#     else:
#         top_perc = weighted.loc[weighted.rank(pct=True) > percentile / 100].index
#         optimal_seeds = top_perc.values
#
#     return optimal_seeds


def score_embedding(results, metrics=None, weights=None):
    if not metrics:
        metrics = list(results.keys())
    if not weights:
        weights = {m: 1 / len(metrics) for m in metrics}

    assert sum(weights.values()) == 1, 'weights must sum to 1'
    assert metrics == list(weights.keys()), 'you must pass a weight value for each metric considered'

    scores = pd.DataFrame()
    for metric in metrics:
        asc = False if metric == 'intersections' else True
        res = pd.Series(results[metric])
        scores[metric] = res.rank(pct=True, ascending=asc)

    weighted = (scores * weights).sum(axis=1)
    return weighted


def optimize_embedding(opt_results, metrics, weights, n_best=10):
    orders_scores = pd.DataFrame()
    for order, results in opt_results.items():
        orders_scores[order] = score_embedding(results, metrics=metrics, weights=weights)

    return orders_scores.stack().nlargest(n_best).index.values

##################################################
# load events in original topic space
video_events = np.load(opj(events_dir, 'video_events.npy'))
avg_recall_events = np.load(opj(events_dir, 'avg_recall_events.npy'))
recall_events = np.load(opj(events_dir, 'recall_events.npy'), allow_pickle=True)

orig_pdist = 1 - pdist(video_events, 'correlation')

orders = [f'order{ord}' for ord in range(1, 7)]
order_results = {}

for order in orders:
    results_path = opj(optimized_dir, f'{order}_results.p')
    embs_dir = opj(embeddings_dir, order)

    # load optimization results if already run
    if os.path.isfile(results_path):
        print(f'loading results for {order}...')
        with open(results_path, 'rb') as f:
            order_results[order] = pickle.load(f)
        continue

    # skip order if not all seeds finished
    elif len(os.listdir(embs_dir)) < len(SEEDS):
        print(f'skipping {order} -- not all seeds finished')
        continue

    # otherwise compute results
    print(f'computing results for {order}...')
    dispersion = np.full((len(SEEDS),), np.nan)
    intersections = np.full((len(SEEDS),), np.nan)
    similarity_euc = np.full((len(SEEDS),), np.nan)
    similarity_corr = np.full((len(SEEDS),), np.nan)

    for ix, seed in enumerate(range_(SEEDS[0], SEEDS[-1]+1)):
        fpath = opj(embs_dir, f'seed{seed}.npy')
        embeddings = np.load(fpath, allow_pickle=True)
        video_embedding = embeddings[0]
        avg_recall_embedding = embeddings[1]
        recall_embeddings = embeddings[2:]

        dispersion[ix] = dispersion_dist(video_embedding)
        intersections[ix] = n_intersections(video_embedding)
        similarity_euc[ix] = spatial_similarity(video_embedding,
                                                     orig_pdist,
                                                     'euclidean')
        similarity_corr[ix] = spatial_similarity(video_embedding,
                                                 orig_pdist,
                                                 'correlation')

    results_dict = {
        'dispersion': dispersion,
        'intersections': intersections,
        'similarity_euc': similarity_euc,
        'similarity_corr': similarity_corr
    }

    with open(results_path, 'wb') as f:
        pickle.dump(results_dict, f)

    order_results[order] = results_dict

################################################################################
output = {}

opt_params = optimize_embedding(order_results, metrics=METRICS, weights=WEIGHTS, n_best=10)
suffix = '-'.join([str(m) + str(w) for m, w in zip(METRICS, WEIGHTS.values())])

print('suffix is', suffix)
for seed, order in opt_params:
    emb_path = opj(embeddings_dir, order, f'seed{seed}.npy')
    opt_path = opj(optimized_dir, f'{order}_seed{seed}_{suffix}.npy')
    copy2(emb_path, opt_path)