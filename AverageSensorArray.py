#!/imaging/local/software/miniconda/envs/mne0.18/bin/python
"""
==================================================================================
Find fiff-file with the most average sensor array position in a list of files.
For example to be used for maxfilter -trans.
A text file with the list of fiff-files needs to be specified:
One line per file, each file with full path.
An example text file can be found here:
/imaging/local/software/mne_python/Utilities/AverageSensorArray/fiff_file_list.txt
E.g., run in command line: AverageSensorArray fiff_file_list.txt
==================================================================================
"""
# Olaf Hauk, Python 3, July 2019

print(__doc__)

from sys import argv, exit

import argparse

from numpy import mean, sum

import mne

print('MNE %s.\n' % mne.__version__)

from mne.io import read_info

if not argv[1:]:

    exit()

print(mne)

parser = argparse.ArgumentParser(description='Determine average MEG sensor array across fiff-files.')

parser.add_argument('--filelist', help='Text file with one fiff-file per line.')

args = parser.parse_args()

fid = open(args.filelist)

filelist = fid.read().splitlines()

fid.close()

# list with origins per file
coors = []

for file in filelist:

    print(file)

    info = read_info(file)

    # 4th column is device coordinate origin in head coordinates.
    # https://mail.nmr.mgh.harvard.edu/pipermail//mne_analysis/2008-September/000092.html
    transmat = info['dev_head_t']['trans']

    coor = -1000.*transmat[0:3,3] # mm and "-", compatible with "HPI fit" on screen during recording
    print('%.1f %.1f %.1f\n' % (coor[0], coor[1], coor[2]))

    coors.append(coor)


# mean coordinate
coor_m = mean(coors, axis=0)

# Euclidean distance from mean per subject
diffs = sum((coors - coor_m)**2, axis=1)**0.5

# Find minimum and maximum
min_idx, min_val = diffs.argmin(), diffs.min()
max_idx, max_val = diffs.argmax(), diffs.max()

# Output indices starting with 1

for [di,dd] in enumerate(diffs):

    print('Subject %d: Dev %.1fmm (%.1f %.1f %.1f)\n' % (di+1, dd, coors[di][0], coors[di][1], coors[di][2]))

print('Average coordinate (mm): %.1f %.1f %.1f\n' % (coor_m[0], coor_m[1], coor_m[2]))

print('Most average subject coordinate (mm): %.1f %.1f %.1f\n' % (coors[min_idx][0], coors[min_idx][1], coors[min_idx][2]))

print('Least average subject coordinate (mm): %.1f %.1f %.1f\n' % (coors[max_idx][0], coors[max_idx][1], coors[max_idx][2]))

print('#########################################################################')
print('The MOST AVERAGE subject is #%d (dev %.1fmm): %s.' % (min_idx+1, min_val, filelist[min_idx]))
print('#########################################################################')

print('For comparison, the least average subject is #%d (dev %.1fmm): %s.\n' % (max_idx+1, max_val, filelist[max_idx]))

# Done