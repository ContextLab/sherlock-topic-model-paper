import socket
import os

config = dict()

# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
# job creation options

#add additional checks for your local machine here...
# ******** check kiewit hostname from eduroam ********

config['startdir'] = '/dartfs/rc/lab/D/DBIC/CDL/f0028ph/sherlock-embedding'
config['workingdir'] = os.path.join(config['startdir'], 'scripts')
config['datadir'] = os.path.join(config['startdir'], 'data')
config['figdir'] = os.path.join(config['startdir'], 'figures')
config['template'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run_job_cluster.sh')
config['scriptdir'] = os.path.join(config['workingdir'], 'scripts')
config['lockdir'] = os.path.join(config['workingdir'], 'locks')


# runtime options
config['jobname'] = "embedding"  # default job name
config['q'] = "largeq"  # options: default, test, largeq
config['nnodes'] = 1  # how many nodes to use for this one job
config['ppn'] = 1  # how many processors to use for this one job (assume 4GB of RAM per processor)
config['walltime'] = '12:00:00'  # maximum runtime, in h:MM:SS
config['cmd_wrapper'] = "python"  # replace with actual command wrapper (e.g. matlab, python, etc.)
# ====== MODIFY ONLY THE CODE BETWEEN THESE LINES ======
