import sys
import numpy as np
from nilearn.image import load_img
from brainiak.searchlight.searchlight import Searchlight
import pandas as pd

subid = int(sys.argv[1])
perm = int(sys.argv[2])

np.random.seed(perm)

# load fmri data
data = load_img('/idata/cdl/data/fMRI/andy/sherlock/data/sherlock_movie_s%s_10000.nii.gz' % str(subid)).get_data()

# load dtw warp path and extract the movie path
#path = np.load('/idata/cdl/data/fMRI/andy/sherlock/data/s%s_dtw_path.npy' % str(subid))
#movie_path = np.array(list(map(lambda x: x[0], path)))

# reindex the fmri data with the movie path
#data = data[:,:,:, movie_path]

# create the mask
mask = data[:,:,:,0]!=10000

# load video model
model = np.load('/idata/cdl/data/fMRI/andy/sherlock/data/movie_corrmat.npy')

# shift the video model
shift = np.random.randint(1, model.shape[0]-1)
shifted = np.roll(model, shift=shift, axis=0)

# recompute shifted correlation matrix
model = pd.DataFrame(shifted).T.corr().values

# Create searchlight object
params = dict(sl_rad=5)
sl = Searchlight(**params)

# Distribute data to processes
sl.distribute([data], mask)
sl.broadcast(model)

# Define voxel function
def sfn(l, msk, myrad, bcast_var):
    from scipy.spatial.distance import cdist
    from scipy.stats import pearsonr
    b = l[0][msk,:].T
    c = 1 - cdist(b, b, 'correlation').ravel()
    return pearsonr(c, bcast_var.ravel())[0]

# Run searchlight
result = sl.run_searchlight(sfn)
np.save('/idata/cdl/data/fMRI/andy/sherlock/analyses/searchlight_movie/perms/s%s_perm%s_shift%s' % (str(subid), str(perm), str(shift)), result)
