import socket
import os

config = dict()

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
# job creation options
config['startdir'] = '/dartfs/rc/lab/D/DBIC/CDL/f0028ph/searchlights/'
config['workingdir'] = os.path.join(config['startdir'], 'scripts')
config['datadir'] = os.path.join(config['startdir'], 'data')
config['template'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run_job_cluster.sh')
config['scriptdir'] = os.path.join(config['workingdir'], 'scripts')
config['lockdir'] = os.path.join(config['workingdir'], 'locks')


# runtime options
config['jobname'] = "searchlight"  # default job name
config['q'] = "largeq"  # options: default, test, largeq
config['nnodes'] = 1  # how many nodes to use for this one job
config['ppn'] = 8  # how many processors to use for this one job (assume 4GB of RAM per processor)
config['walltime'] = '12:00:00'  # maximum runtime, in h:MM:SS
config['cmd_wrapper'] = "python"  # replace with actual command wrapper (e.g. matlab, python, etc.)

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
