#!/usr/bin/python

# create a bunch of job scripts
import os
import socket
import getpass
import datetime as dt
from subprocess import call
from searchlight_config import config


# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
from os.path import isfile, dirname, realpath, join as opj
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import correlation

N_PERMS = 100

input_dir = opj(config['datadir'], 'inputs')
traj_path = opj(input_dir, 'models_t100_v50_r10.npy')
warped_dir = opj(input_dir, 'warped')
scan_dir = opj(input_dir, 'fMRI')
video_jobscript = opj(dirname(realpath(__file__)), 'searchlight_permute_video.py')
recall_jobscript = opj(dirname(realpath(__file__)), 'searchlight_permute_recall.py')

# temporally align recall trajectories to video TR timeseries
video_traj, recall_trajs = np.load(traj_path, allow_pickle=True)

for sub, rec_traj in enumerate(recall_trajs):
    sub_dtw_path = opj(warped_dir, f'sub{sub + 1}.npy')

    if not isfile(sub_dtw_path):
        dist, path = fastdtw(video_traj, rec_traj, dist=correlation)
        warped_ix = [i[1] for i in path]
        rec_dtw = rec_traj[warped_ix]
        np.save(sub_dtw_path, rec_dtw)

# create jobs for submission
job_commands = list()
job_names = list()
for perm in range(N_PERMS):
    for subid in range(1, 18):
        job_names.append(f'searchlight_video_{subid}_{perm}')
        job_commands.append(f'{video_jobscript} {subid} {perm}')

        job_names.append(f'searchlight_recall_{subid}_{perm}')
        job_commands.append(f'{recall_jobscript} {subid} {perm}')


# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======

assert(len(job_commands) == len(job_names))


# job_command is referenced in the run_job.sh script
# noinspection PyBroadException,PyUnusedLocal
def create_job(name, job_command):
    # noinspection PyUnusedLocal,PyShadowingNames
    def create_helper(s, job_command):
        x = [i for i, char in enumerate(s) if char == '<']
        y = [i for i, char in enumerate(s) if char == '>']
        if len(x) == 0:
            return s

        q = ''
        index = 0
        for i in range(len(x)):
            q += s[index:x[i]]
            unpacked = eval(s[x[i]+1:y[i]])
            q += str(unpacked)
            index = y[i]+1
        return q

    # create script directory if it doesn't already exist
    try:
        os.stat(config['scriptdir'])
    except:
        os.makedirs(config['scriptdir'])

    template_fd = open(config['template'], 'r')
    job_fname = os.path.join(config['scriptdir'], name)
    new_fd = open(job_fname, 'w+')

    while True:
        next_line = template_fd.readline()
        if len(next_line) == 0:
            break
        new_fd.writelines(create_helper(next_line, job_command))
    template_fd.close()
    new_fd.close()
    return job_fname


# noinspection PyBroadException
def lock(lockfile):
    try:
        os.stat(lockfile)
        return False
    except:
        fd = open(lockfile, 'w')
        fd.writelines('LOCK CREATE TIME: ' + str(dt.datetime.now()) + '\n')
        fd.writelines('HOST: ' + socket.gethostname() + '\n')
        fd.writelines('USER: ' + getpass.getuser() + '\n')
        fd.writelines('\n-----\nCONFIG\n-----\n')
        for k in config.keys():
            fd.writelines(k.upper() + ': ' + str(config[k]) + '\n')
        fd.close()
        return True


# noinspection PyBroadException
def release(lockfile):
    try:
        os.stat(lockfile)
        os.remove(lockfile)
        return True
    except:
        return False


script_dir = config['scriptdir']
lock_dir = config['lockdir']
lock_dir_exists = False
# noinspection PyBroadException
try:
    os.stat(lock_dir)
    lock_dir_exists = True
except:
    os.makedirs(lock_dir)

# noinspection PyBroadException
try:
    os.stat(config['startdir'])
except:
    os.makedirs(config['startdir'])

locks = list()
for n, c in zip(job_names, job_commands):
    # if the submission script crashes before all jobs are submitted, the lockfile system ensures that only
    # not-yet-submitted jobs will be submitted the next time this script runs
    next_lockfile = os.path.join(lock_dir, n+'.LOCK')
    locks.append(next_lockfile)
    if not os.path.isfile(os.path.join(script_dir, n)):
        if lock(next_lockfile):
            next_job = create_job(n, c)

            if ('discovery' in socket.gethostname()) or ('ndoli' in socket.gethostname()):
                submit_command = 'echo "[SUBMITTING JOB: ' + next_job + ']"; mksub'
            else:
                submit_command = 'echo "[RUNNING JOB: ' + next_job + ']"; sh'

            call(submit_command + " " + next_job, shell=True)

# all jobs have been submitted; release all locks
for l in locks:
    release(l)
if not lock_dir_exists:  # remove lock directory if it was created here
    os.rmdir(lock_dir)
