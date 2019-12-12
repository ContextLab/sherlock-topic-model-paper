import sys
import numpy as np
import hypertools as hyp
from os.path import join as opj
from embedding_config import config

order, min_seed, max_seed, division = [int(i) for i in sys.argv[1:]]

seeds = np.split(np.arange(min_seed, max_seed), 10)[division]
if division == 9:
    seeds = list(seeds) + [10000]

events_dir = opj(config['datadir'], 'events')
embeddings_dir = opj(config['datadir'], 'embeddings')

video_events = np.load(opj(events_dir, 'video_events.npy'))
avg_recall_events = np.load(opj(events_dir, 'avg_recall_events.npy'))
recall_events = np.load(opj(events_dir, 'recall_events.npy'), allow_pickle=True)

if order == 1:
    to_reduce = list(recall_events) + [video_events] + [avg_recall_events]
elif order == 2:
    to_reduce = list(recall_events) + [avg_recall_events] + [video_events]
elif order == 3:
    to_reduce = [video_events] + [avg_recall_events] + list(recall_events)
elif order == 4:
    to_reduce = [video_events] + list(recall_events) + [avg_recall_events]
elif order == 5:
    to_reduce = [avg_recall_events] + list(recall_events) + [video_events]
else:
    to_reduce = [avg_recall_events] + [video_events] + list(recall_events)

for seed in seeds:
    np.random.seed(seed)
    embeddings = hyp.reduce(to_reduce,
                            reduce={
                                'model': 'UMAP',
                                'params': {
                                    'random_state': seed
                                }
                            },
                            ndims=2)

    if order == 1:
        video_embedding = embeddings[-2]
        recall_embeddings = embeddings[:-2]
        avg_recall_embedding = embeddings[-1]
    elif order == 2:
        video_embedding = embeddings[-1]
        recall_embeddings = embeddings[:-2]
        avg_recall_embedding = embeddings[-2]
    elif order == 3:
        video_embedding = embeddings[0]
        recall_embeddings = embeddings[2:]
        avg_recall_embedding = embeddings[1]
    elif order == 4:
        video_embedding = embeddings[0]
        recall_embeddings = embeddings[1:-1]
        avg_recall_embedding = embeddings[-1]
    elif order == 5:
        video_embedding = embeddings[-1]
        recall_embeddings = embeddings[1:-1]
        avg_recall_embedding = embeddings[0]
    else:
        video_embedding = embeddings[1]
        recall_embeddings = embeddings[2:]
        avg_recall_embedding = embeddings[0]

    np.save(opj(embeddings_dir, f'order{order}', f'seed{seed}.npy'),
            [video_embedding, avg_recall_embedding, recall_embeddings])
