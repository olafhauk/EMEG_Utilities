#!/imaging/local/software/miniconda/envs/mne0.20/bin/python
"""
Anonymise MEG fiff-files.

==========================================
Anonymise MEG fiff-files using fiff_anonymise.
Search sub-directories of root_paths for fiff-files.
Anonymise those that contain realistic date of birth.
Existing files will be replaced.
For example:
Anonymise_Fiff.py --SearchPaths /imaging/calvin/meg /imaging/hobbes/meg

Type Anonymise_Fiff.py --help for options.
==========================================

OH June 2017, June 2020
"""

print(__doc__)

import os
from sys import argv, exit

# only display help message when no args are passed.
if len(argv) == 1:
    exit(1)

import argparse

from mne.io import read_info

# Parse input arguments

parser = argparse.ArgumentParser(description='Anonymise Fiff data.')

parser.add_argument('--SearchPaths', type=str, nargs='+',
                    help='Paths to search for fiff-files.')

parser.add_argument('--MinYear', help='Minimum possible year of birth '
                    '(default 1930).', type=float, default=1900)

args = parser.parse_args()

# list of paths to search for fiff-files
root_paths = args.SearchPaths

# make sure paths are in list
if type(root_paths) != list:

    root_paths = [root_paths]

bytes_thresh = 35  # threshold for difference in file sizes (bytes)
yob_thresh = args.MinYear  # only consider years-of-birth above this

fiff_list = []  # collect fiff-files in list
for root_path in root_paths:
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in [ff for ff in filenames if ff.endswith('.fif')]:
            fiff_list.append(os.path.join(dirpath, filename))
            print(fiff_list[-1])

n_files = len(fiff_list)

print("\n###\n%d fiff-files to consider.\n###" % n_files)

# command to apply to filename
cmd_string = '/neuro/bin/util/fiff_anonymize '

path_ori = os.getcwd()  # remember current directory

# list of files for which number of bytes don't match
didnt_work = []

print("Anonymising.")
for filename in fiff_list:

    path, fname = os.path.split(filename)

    anon_fname = fname.split('.')[0] + '_anon.fif'

    # change to subject directory, to avoid problems with multiple "."
    os.chdir(path)

    # Excute anonymisation command in linux
    cmd = cmd_string + fname

    try:  # try if it's measurement data at all
        info = read_info(fname)
    except:  # (RuntimeError, TypeError, NameError, ValueError):
        continue  # try next file

    if not (info['subject_info'] is None):
        if ('birthday' in info['subject_info']):
            yob = info['subject_info']['birthday'][0]  # year of birth
            if yob < yob_thresh:  # if subject ridiculously old, next file
                continue
        else:
            continue
    else:
        continue

    try:  # try anonymising
        os.system(cmd)
    except ValueError:
        print("")

    # filename after applying anonymisation command
    anon_fname = fname.split('.')[0] + '_anon.fif'

    # check if everything worked, if yes copy anon to orignal filename
    if os.path.exists(anon_fname):  # if an anonymised file exists
        s1 = os.path.getsize(fname)
        s2 = os.path.getsize(anon_fname)
        diff = s1 - s2

        if diff > bytes_thresh:  # compare file sizes
            didnt_work.append(filename)  # if difference too big, don't remove
        else:  # if file sizes ok
            # keep a safe copy
            keep_fname = fname.split('.')[0] + '_keep_zyx987654321.fif'
            os.rename(fname, keep_fname)

            os.rename(anon_fname, fname)  # rename anonymised file to old file

            s3 = os.path.getsize(fname)
            if s3 == s2:  # if copy successful
                os.remove(keep_fname)  # remove safe copy
                print("Success with %s:" % filename)
            else:
                didnt_work.append(filename)
    else:
        didnt_work.append(filename)

# back to original path
os.chdir(path_ori)
