#!/imaging/local/software/miniconda/envs/mne0.18/bin/python
"""
==================================================================================
Plot head positions in MEG determined by Maxfilter.
"pos"-files from Maxfilter (option -hp) are required as input.
Based on MNE-Python.
Look here for an example:
https://martinos.org/mne/stable/auto_examples/preprocessing/plot_head_positions.html
==================================================================================
"""
# Olaf Hauk, Python 3, July 2019

print(__doc__)

###
# PARSE INPUT ARGUMENTS
###

from sys import argv, exit
import argparse

from matplotlib import pyplot as plt

import mne

parser = argparse.ArgumentParser(description='MEG head positions.')

parser.add_argument('--FileRaw', help='Input filename.')
parser.add_argument('--FileOut', help='Output filename for figure (default: do not save).\
										If specified, figure will not be shown on screen.', default='')
parser.add_argument('--mode', help='traces|field (default: traces).', default='traces')

args = parser.parse_args()

if len(argv)==1:
    # display help message when no args are passed.
    exit(1)

###
# PROCESS DATA
###

if args.FileOut != '':
	plt.ion()

# Read head position from Maxfilter output
print('Reading positions from %s.' % args.FileRaw)
pos = mne.chpi.read_head_pos(args.FileRaw) 

# Visualise head positions
print('Visualising positions.')
fig = mne.viz.plot_head_positions(pos, mode=args.mode)

# if filename for figure specified in command line
if args.FileOut != '':
	print('Saving figure to %s.' % args.FileOut)

	fig.savefig(args.FileOut)