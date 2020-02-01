import sys
import numpy as np
from os.path import join as opj
from brainiak.searchlight.searchlight import Searchlight
from nilearn.image import load_img
from scipy.stats import pearsonr
from searchlight_config import config


# voxel function for searchlight
def sfn(l, msk, sl_rad, bcast_var):
    video_corrs, diag_mask = bcast_var
    sl_activity = l[0][msk, :].T
    sl_corrs = np.corrcoef(sl_activity)[diag_mask]
    return pearsonr(sl_corrs, video_corrs)[0]


def kth_diag_indices(arr, k):
    row_ix, col_ix = np.diag_indices_from(arr)
    return row_ix[:-k], col_ix[k:]


subid, perm = int(sys.argv[1]), int(sys.argv[2])

input_dir = opj(config['datadir'], 'inputs')
traj_path = opj(input_dir, 'models_t100_v50_r10.npy')
scan_path = opj(input_dir, 'fMRI', f'sherlock_movie_s{subid}.nii.gz')
results_dir = opj(config['datadir'], 'outputs', 'searchlight_video')

# load video model
video_model = np.load(traj_path, allow_pickle=True)[0]

# load fMRI data, create mask
scan_data = load_img(scan_path).get_data()
mask = (scan_data != 0).all(axis=3)


try:
    # ensure random shift is consistent across participants
    np.random.seed(perm)
    shift = np.random.randint(1, video_model.shape[0] - 1)
    result_path = opj(results_dir, 'perms', f'sub{subid}_perm{perm}_shift{shift}.npy')
except ValueError:
    # run searchlight on unaltered data (perm == -1)
    shift = 0
    result_path = opj(results_dir, f'sub{subid}.npy')

# shift recall model timeseries
shifted = np.roll(video_model, shift=shift, axis=0)

# subject 5 has some missing TRs at the end and was padded to length of other
# subjects. Truncate fMRI data and topic trajectory to exclude filler data
if subid == 5:
    shifted = shifted[:1925, :]
    scan_data = scan_data[:, :, :, :1925]

# compute shifted recall correlation matrix
shifted_corrmat = np.corrcoef(shifted)

# isolate off-diagonal values with video model temporal correlations > 0
# this was precomputed to save permutation runtime with:
# for k in range(1976):
#     d = np.diag(np.corrcoef(video_model), k=k)
#     if ~(d > 0).any():
#         DIAG_LIMIT = k
#         break
DIAG_LIMIT = 238
diag_mask = np.zeros_like(shifted_corrmat, dtype=bool)

for k in range(1, DIAG_LIMIT):
    ix = kth_diag_indices(diag_mask, k)
    diag_mask[ix] = True

video_corrs = shifted_corrmat[diag_mask]
to_broadcast = (video_corrs, diag_mask)

# create Searchlight object
sl = Searchlight(sl_rad=2)

# distribute data to processes
sl.distribute([scan_data], mask)
sl.broadcast(to_broadcast)

# run searchlight, save data
result = sl.run_searchlight(sfn)
np.save(result_path, result)
