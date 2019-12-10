import os
import glob
import numpy as np
from os.path import join as opj
from shutil import copy2
from nilearn.image import load_img, new_img_like
from searchlight_config import config

video_dir_old = opj(config['datadir'], 'outputs', 'searchlight_video')
recall_dir_old = opj(config['datadir'], 'outputs', 'searchlight_recall')
finished_dir = opj(config['datadir'], 'finished')
video_dir_new = opj(finished_dir, 'searchlight_video')
recall_dir_new = opj(finished_dir, 'searchlight_recall')


N_SUBJECTS = 17
N_PERMS = 100


# make sure all permutations have finished
assert len(os.listdir(opj(video_dir_old, 'perms'))) == N_SUBJECTS * N_PERMS, 'Some video permutations not finished yet'
assert len(os.listdir(opj(recall_dir_old, 'perms'))) == N_SUBJECTS * N_PERMS, 'Some recall permutations not finished yet'

try:
    os.stat(finished_dir)
# create directory structure
except FileNotFoundError:
    print('Creating directory structure...')
    for d_old, d_new in zip([video_dir_old, recall_dir_old],
                            [video_dir_new, recall_dir_new]):
        os.makedirs(opj(d_new, 'perms'), exist_ok=True)
        # copy non-permuted data
        for sub in range(1, 18):
            old_path = opj(d_old, f'sub{sub}.npy')
            new_path = opj(d_new, f'sub{sub}.npy')
            copy2(old_path, new_path)

# collect permutations
ref_img = load_img(opj('????????'))

for perm in range(100):
    print(f'collecting permutation {perm}...')
