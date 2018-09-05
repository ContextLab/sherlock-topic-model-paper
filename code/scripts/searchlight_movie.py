import sys
import numpy as np
from nilearn.image import load_img
from brainiak.searchlight.searchlight import Searchlight

subid = sys.argv[1]
data = load_img('/idata/cdl/data/fMRI/andy/sherlock/data/sherlock_movie_s%s_10000.nii.gz' % str(subid)).get_data()

mask = data[:,:,:,0]!=10000
model = np.load('/idata/cdl/data/fMRI/andy/sherlock/data/movie_corrmat.npy')
params = dict(sl_rad=5)

# Create searchlight object
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

np.save('/idata/cdl/data/fMRI/andy/sherlock/analyses/searchlight_movie/s%s' % str(subid), result)
