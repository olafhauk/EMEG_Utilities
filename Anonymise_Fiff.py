#!/imaging/local/software/miniconda/envs/mne0.20/bin/python
"""
Anonymise MEG fiff-files.

==========================================
Anonymise MEG fiff-files using fiff_anonymise.
Search sub-directories of root_paths for fiff-files.
Anonymise those that contain realistic date of birth.
Existing files will be replaced.
==========================================

OH June 2017
"""

import os
from mne.io import read_info

# EDIT: list of paths to search for fiff-files
root_paths = ['your_path_1', 'your_path_2']
# e.g. root_paths = ['/imaging/calvin/meg/anon/', '/imaging/hobbes/meg/anon/']

# DO NOT EDIT THE FOLLOWING unless you know what you are doing

bytes_thresh = 35  # threshold for difference in file sizes (bytes)
yob_thresh = 1930  # only consider years-of-birth above this

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
