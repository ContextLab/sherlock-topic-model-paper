import sys
import numpy as np
from os.path import join as opj
from brainiak.searchlight.searchlight import Searchlight
from nilearn.image import load_img
from scipy.stats import pearsonr
from searchlight_config import config


# Define voxel function for searchlight
def sfn(l, msk, sl_rad, bcast_var):
    b = l[0][msk,:].T
    c = np.corrcoef(b).ravel()
    return pearsonr(c, bcast_var.ravel())[0]


input_dir = opj(config['datadir'], 'inputs')
traj_path = opj(input_dir, 'models_t100_v50_r10.npy')
warped_dir = opj(input_dir, 'warped')
scan_dir = opj(input_dir, 'fMRI')

subid, perm = int(sys.argv[1]), int(sys.argv[2])

# ensure shift size is consistent across participants
np.random.seed(perm)

# load fMRI data
scan_data = load_img(opj(scan_dir, f'sherlock_movie_s{subid}_10000.nii.gz')).get_data()

# create mask
mask = scan_data[:, :, :, 0] != 10000

# load video model, compute temporal correlation matrix
video = np.load(traj_path, allow_pickle=True)[0]
video_corrmat = np.corrcoef(video)

# shift video model timeseries
shift = np.random.randint(1, video_corrmat.shape[0]-1)
shifted = np.roll(video_corrmat, shift=shift, axis=0)

# recompute shifted correlation matrix
shifted_corrmat = np.corrcoef(shifted)

# create Searchlight object
sl = Searchlight(sl_rad=5)

# distribute data to processes
sl.distribute([scan_data], mask)
sl.broadcast(shifted_corrmat)

# run searchlight, save data
result = sl.run_searchlight(sfn)
np.save()
