#!/imaging/local/software/miniconda/envs/mne0.18/bin/python
"""
==================================================================================
Apply pre-computed ICA to EEG/MEG data in fiff-format to remove eye-movement artefacts.
Requires ICA decomposition from Fiff_Compute_ICA.py.
For more help, type Fiff_Compute_ICA.py -h.
Based on MNE-Python.
For a tutorial on ICA in MNE-Python, look here:
https://martinos.org/mne/stable/auto_tutorials/preprocessing/plot_artifacts_correction_ica.html
==================================================================================
"""
# Olaf Hauk, Python 3, July 2019

print(__doc__)

###
# PARSE INPUT ARGUMENTS
###

from sys import argv, exit
import argparse

parser = argparse.ArgumentParser(description='Apply ICA.')

parser.add_argument('--FileRawIn', help='Input filename for raw data (no suffix).')
parser.add_argument('--FileICA', help='Output file for ICA decomposition (no suffix, default FileRawIn).', default='')
parser.add_argument('--FileRawOut', help='Output filename for raw data (no suffix, default FileRawIn).', default='')
parser.add_argument('--ICAcomps', help='ICA components to remove (default: as specified in precomputed ICA).', nargs='+', type=int, default=[])

args = parser.parse_args()

if len(argv)==1:
    # display help message when no args are passed.
    exit(1)

from sys import argv, exit

from os import path as op

from shutil import copyfile

import numpy as np

import importlib

import mne
from mne.preprocessing import ICA

print('MNE Version: %s\n' % mne.__version__)
print(mne)

###
# create filenames
###

# raw-filenames to be subjected to ICA for this subject
raw_fname_in = args.FileRawIn + '.fif'

# save raw with ICA applied and artefacts removed
if args.FileRawOut == '':

    raw_fname_out = args.FileRawIn + '_ica_raw.fif'

else:

    raw_fname_out = args.FileRawOut + '.fif'

# file with ICA decomposition
if args.FileICA == '':

    ica_fname_in = args.FileRawIn + '-ica.fif'

else:

    ica_fname_in = args.FileICA + '-ica.fif'

###
# APPLY ICA
###

print('Reading raw file %s' % raw_fname_in)
raw = mne.io.read_raw_fif(raw_fname_in, preload=True)

print('Reading ICA file %s' % ica_fname_in)
ica = mne.preprocessing.read_ica(ica_fname_in)

# if ICA components to be removed specified on command line
if args.ICAcomps != []:

    ica.exclude = args.ICAcomps

print('Applying ICA to raw file, removing components:')
print(' '.join(str(x) for x in ica.exclude))

ica.apply(raw)

print('Saving raw file with ICA applied to %s' % raw_fname_out)
raw.save(raw_fname_out, overwrite=True)