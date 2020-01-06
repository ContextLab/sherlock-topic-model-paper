import os
import sys
import spurplus
from os.path import join as opj

hostname, username, password = sys.argv[1:]

datadir_local = '../../data/processed/'
emb_path_remote = '/dartfs/rc/lab/D/DBIC/CDL/f0028ph/sherlock-embedding/data/optimized/embeddings.npy'
emb_path_local = opj(datadir_local, 'embeddings.npy')

sl_dir_remote = '/dartfs/rc/lab/D/DBIC/CDL/f0028ph/searchlight-sherlock/data/finished/'
sl_vdir_local = opj(datadir_local, 'searchlight_video')
sl_rdir_local = opj(datadir_local, 'searchlight_recall')

if not os.path.isdir(sl_vdir_local):
    os.mkdir(sl_vdir_local)
if not os.path.isdir(sl_rdir_local):
    os.mkdir(sl_rdir_local)

with spurplus.connect_with_retries(hostname=hostname,
                                   username=username,
                                   password=password) as remote:
                               # copy over embeddings
                               remote.get(emb_path_remote, emb_path_local)
                               # copy over searchlights
                               for analysis in ['video', 'recall']:
                                   src_dir = opj(sl_dir_remote, f'searchlight_{analysis}')
                                   dest_dir = opj(datadir_local, f'searchlight_{analysis}')
                                   perm_dir = opj(src_dir, 'perms')
                                   for sub in range(1, 18):
                                       # unshifted data
                                       src_path = opj(src_dir, f'sub{sub}.npy')
                                       dest_path = opj(dest_dir, f'sub{sub}.npy')
                                       remote.get(src_path, dest_path)
                                   # permuted data
                                   for perm in range(100):
                                       perm_src_path = opj(perm_dir, f'perm{perm}.nii.gz')
                                       perm_dest_path = opj(dest_dir, f'perm{perm}.nii.gz')
                                       remote.get(perm_src_path, perm_dest_path)
