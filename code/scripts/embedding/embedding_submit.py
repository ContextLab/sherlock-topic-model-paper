#!/usr/bin/python

# create a bunch of job scripts
from embedding_config import config
from subprocess import call
import os
import socket
import getpass
import datetime as dt
from os.path import join as opj


# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
import numpy as np
job_script = opj(os.path.dirname(os.path.realpath(__file__)), 'embedding_cruncher.py')

embeddings_dir = opj(config['datadir'], 'embeddings')
fig_dir = config['figdir']

job_commands = list()
job_names = list()

min_seed = 0
max_seed = 10000

# order 1: recalls, video, avg recall
# order 2: recalls, avg recall, video
# order 3: video, avg recall, recalls
# order 4: video, recalls, avg recall
# order 5: avg recall, recalls, video
# order 6: avg recalls, video, recalls

for order in range(1, 7):
    if not os.path.isdir(opj(embeddings_dir, f'order{order}')):
        os.mkdir(opj(embeddings_dir, f'order{order}'))
    if not os.path.isdir(opj(fig_dir, f'order{order}')):
        os.mkdir(opj(fig_dir, f'order{order}'))
    for division in range(10):
        job_commands.append(f'{job_script} {order} {min_seed} {max_seed} {division}')
        job_names.append(f'optimize_embedding_order{order}_{min_seed}_{max_seed}_{division}')

    # done = [int(os.path.splitext(file)[0][4:]) for file in os.listdir(opj(embeddings_dir, f'order{order}'))]
    # seeds_todo = [s for s in seeds if s not in done]

    # for seed in seeds_todo:
    #     job_commands.append(f'{job_script} {order} {seed}')
    #     job_names.append(f'optimize_embedding_order{order}_seed{seed}')



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
    job_fname = opj(config['scriptdir'], name)
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
    next_lockfile = opj(lock_dir, n+'.LOCK')
    locks.append(next_lockfile)
    if not os.path.isfile(opj(script_dir, n)):
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