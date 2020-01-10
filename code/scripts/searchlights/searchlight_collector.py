import os
import numpy as np
from glob import glob
from os.path import join as opj
from shutil import copy2
from nilearn.image import concat_imgs, load_img, new_img_like
from scipy.stats import ttest_1samp as ttest
from searchlight_config import config

output_dir = opj(config['datadir'], 'outputs')
finished_dir = opj(config['datadir'], 'finished')
ref_img_path = opj(config['datadir'], 'inputs', 'fMRI', 'ref_img.nii.gz')

N_SUBJECTS = 17
N_PERMS = 100


def r2z(r):
    # computes the Fisher z-transformation
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


# make sure all permutations have finished
assert len(os.listdir(opj(output_dir, 'searchlight_video', 'perms'))) == N_SUBJECTS * N_PERMS, \
    'Some video permutations not finished yet'
assert len(os.listdir(opj(output_dir, 'searchlight_recall', 'perms'))) == N_SUBJECTS * N_PERMS, \
    'Some recall permutations not finished yet'

try:
    os.stat(finished_dir)
# create directory structure
except FileNotFoundError:
    print('Creating directory structure...')
    for analysis in ['video', 'recall']:
        dir_old = opj(output_dir, f'searchlight_{analysis}')
        dir_new = opj(finished_dir, f'searchlight_{analysis}')
        os.makedirs(opj(dir_new, 'perms'), exist_ok=True)
        # copy unshifted data
        for sub in range(1, 18):
            old_path = opj(dir_old, f'sub{sub}.npy')
            new_path = opj(dir_new, f'sub{sub}.npy')
            copy2(old_path, new_path)

# collect permutations
ref_img = load_img(ref_img_path)

for perm in range(100):
    print(f'collecting permutation {perm + 1}/100...', end='\r')
    for analysis in ['video', 'recall']:
        imgs = []
        for sub in range(1, 18):
            img_path = glob(opj(output_dir, f'searchlight_{analysis}', 'perms', f'sub{sub}_perm{perm}_*'))[0]
            sub_data = np.load(img_path, allow_pickle=True)
            img = new_img_like(ref_img, sub_data.astype(np.float64))
            imgs.append(img)

        imgs = concat_imgs(imgs)
        imgs_z = r2z(imgs.get_data().astype(np.float64))
        statmap = ttest(np.moveaxis(imgs_z, -1, 0), 0).statistic
        stat_img = new_img_like(ref_img, statmap.astype(np.float64))
        result_path = opj(finished_dir, f'searchlight_{analysis}', 'perms', f'perm{perm}.nii.gz')
        stat_img.to_filename(result_path)
