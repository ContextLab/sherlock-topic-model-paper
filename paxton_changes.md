# Paxton changes

## Code:
### topic_model_analysis
- dropped two annotations that occurred between end of first scan and beginning of second scan
  - one simply said "blank screen"
  - the other was 1 second long very similar to previous annotation
  - because neither fell during a TR, these were removed from the video topic trajectory in the old analysis anyway
- fixed expected recall text file encoding from 'latin-1' to 'cp1252'
- added some very minor text preprocessing
  - removed punctuation
  - stemmed possessives & contractions
  - previously, problematic punctuation caused "john", "john's", and "john." to all be considered different words
- changes to sliding window parsing
  - old version flaws:
      - first window spanned annotations/sentences 1-`wsize`, second spanned 2-`wsize+1`, etc. For video, this means that 98% of  content ascribed to each TR had actually not yet been viewed.  This also means that first 50 annotations were underrepresented in the topic model's training corpus & first `wsize` annotations/sentences contributed to only fewer resulting topic vectors compared to the rest (e.g., annotation 1 content only contributed to 1/1000 video topic vectors while annotations 50+ contributed to 1/20th of video topic vectors).  This led to weak ability to match early video & recall events correctly
      - Last 50 windows spanned < 50 annotations (e.g., windows[-1] contained only last annotation, windows[-2] contained last 2 annotations, etc.).  As a result, last few topic vectors were created from very short, content-poor documents and topic proportions were volatile & shifted rapidly. This led to weak ability to match late video & recall events correctly.
  - new version changes:
      - windows now "grow" at the beginning in addition to "shrinking" at the end.  Each annotation is represented in training corpus equal number of times & each annotation/sentence appears in same number of video/recall sliding windows.
      - also helps with over-segmenting beginning of trajectory (since, e.g., topic proportions arising from first annotation/sentence are now partially shared by more than only 1 timepoint, and so on)
      - joined annotations/sentences within a window with space rather than comma (was causing tokenization problems for words preceding comma, e.g., "john," != "john")
- changes to mapping of video trajectory to TR units
  - two problems with old approach:
      - previously, all but first vector falling during each TR was dropped, even if first annotation only spanned less of TR than subsequent ones.  Content of *26* windows were dropped entirely due to this
      - topic vectors were mapped to TR by index in video_model, ergo first TR mapped to video_model[0], which was actually created from first 50 annotations.  So nearly all represented content came *after* given TR
  - new version changes:
      - each topic vector is first assigned timepoint at midpoint between onset of first annotation in window and offset of last annotation in window (i.e., midpoint of all represented content)
      - This maps linear timeseries of topic trajectory onto non-linear timseries of annotations, and also corrects relationship between delta t and delta content represented at beginning & end of trajectory where less content comprises sliding windows
      - Resulting timeseries is then mapped to interval [1, 1977) (TR number) and topic trajectory linearly interpolated to 1 vector per TR.
      - Thus the TR topic trajectory's timeseries is based on real-time (seconds), and each TR's topic vector roughly matches a duration-weighted average of windows centered on a timepoint that fell during that TR.
- removed resampling step for recall trajectories (resampled trajectories not used in paper and FFT-based resampling function used assumed periodicity)
- removed some unused imports and function definitions


### eventseg_analysis
- fixed bug in code for choosing optimal K that was causing optimal K - 2 to be chosen
- implemented Wasserstein distance-based K-optimization
- removed unused `score_model` function
- added code to generate K-optimization figures for supplement
- removed event embedding from this notebook, moved to `code/scripts` dir as set of cluster scripts


### eventseg_fig
- now using P17 as example participant
- changed tick frequency for recall subplots


### list_learning_analyses
- added more scatterplots for stats discussed in paper


### brains
- removed unused imports
- moved unused `collect permutations` code to cluster script in `code/scripts/searchlights/searchlight_collector.py`
- no longer sorting permutations after loading (unnecessary, slow)
- combined cells that run same code on video and recall searchlight data
- Fisher z-transform data before running t-test
- cast all nilearn-yielded arrays as 64-bit floats to deal with precision issue
- vectorized permutation correction z-test, significantly sped up
- currently toying with thresholding both positive and negative z-scores (Jeremy's suggestion; may change)
- added code to generate correlation matrices for figure in paper
- added WIP code to plot brains in subplots & construct full figure in notebook
- changed some variable names so they don't overwrite each other


### scripts
- removed existing searchlight scripts, added directory of scripts to run searchlight analyses on HPCC
- fixed voxel function to correlate only upper triangle of topic vector & voxel activity temporal correlation matrices
- fixed bug in video permutations where shifting was done on correlation matrix rather than trajectory
- fixed recall searchlight script to run on non-resampled trajectories
- no longer warping fMRI data based on resampled recall-based DTW path
- added directory of scripts for optimizing embedding seed for trajectory figure


### precision_distinctiveness_fig
- removed Fisher z-transformation from `precision_func` (discussed; decided not applicable here)
- removed hard-coded numbers of events
- removed duplicate scatterplots
- rewrote `distinctiveness_func`
- removed old figure versions and unused code
- updated some matplotlib syntax to work with version in docker container
- added Fisher z-transformation to correlation calculations for scatterplots
- updated formatting of stats annotations on scatterplots
- changed arrangement of small scatterplots so axis labels could be shared
- changed tick frequency for main matchmat plot
- fixed bug in `facecolor` of rectangles for matched events


### trajectory_analysis_and_fig
- changed hard-coded removal of video events with no matched recalls to be automated
- added lots of scratch code that will be removed in final version


### wordle_analysis_and_fig
- wrote function to deal with SPC for correlations (does Fisher z-transform/inverse transform before/after averaging; computes and plots 95% bootstraped CIs)


### corrmats
- updated axis labels from sentence units to window units
- updated axis ticks to change based on individual's trajectory length


### various feature importance analysis/fig notebooks
- renamed `feature_feature_correlation.ipynb` to `feature_similarity.ipynb`
- renamed `feature_model_impact.ipynb` to `feature_importance_fig.ipynb`
- combined `model_structure_features_impact.ipynb` & `movie_recall_correlation_features_impact.ipynb` into `feature_contribution.ipynb`
- largely rewrote code from scratch to make it faster & more readable
- updated topic modeling pipeline to reflect updates to main analysis methods
- fixed temporal structure comparisons to only correlate upper triangle
- removed displayed plots from the two non-figure notebooks
- changed explicit ordering of barplot colors to be set automatically
- flipped red/blue shading of correlation matrix
- changed "Full model" bar label to "All features" to reflect label in paper


# Data:
- saved out relevant data objects with updated results
- removed numerous alternate versions of files from paper revision
- renamed data files generated by feature importance supplementary analyses


# Paper:
- updated all stats to reflect new results
- updated references to number of windows/events throughout
- updated most figures (but haven't formatted any in illustrator yet)
- added text describing new elements of topic modeling procedure
- added some new text to precision/distinctiveness results & methods sections
- updated event segmentation methods to describe Wasserstein distance-based K-optimization
- added some new references to intro and event segmentation methods sections
- updated searchlight methods section


# Dockerfile:
- pinned all package versions for pip install
- updated pinned `quail` commit hash to fix bug
- downgraded `numpy` version to fix compatibility issue with `brainiak`
- downgraded pinned `matplotlib` version to fix compatibility issue with `seaborn.heatmap`
- switched to installing `nilearn` from github to fix compatibility issue with `mpl_toolkits.mpl3d.axes3d.Axes3D`
- upgraded pinned `scipy` version to minimum version with `scipy.stats.wasserstein`
- pinned `xlrd` version to enable `pandas.read_excel`

# README:
- updated tree structure to reflect new cluster script directories in `code/scripts`
