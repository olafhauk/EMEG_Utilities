#!/imaging/local/software/miniconda/envs/mne0.18/bin/python
"""
==================================================================================
Compute ICA decomposition for raw EEG/MEG data in fiff-format
to remove eye- or heart-related artefacts.
Components will be identified based on EOG or ECG channels, respectively.
Results will be visualised in an HTML file.
By default, 1 component per channel (EOG and ECG) will be removed.
For more help, type Fiff_Compute_ICA.py -h.
Pre-requisite for Fiff_Apply_ICA.py.
Based on MNE-Python.
For a tutorial on ICA in MNE-Python, look here:
https://martinos.org/mne/stable/auto_tutorials/preprocessing/plot_artifacts_correction_ica.html
==================================================================================
"""
# Olaf Hauk, Python 3, July 2019, Feb 2020

###
# PARSE INPUT ARGUMENTS
###

from sys import argv, exit
import argparse

import numpy as np

import matplotlib.pyplot as plt

import mne
from mne.preprocessing import ICA, create_eog_epochs, create_ecg_epochs
from mne.report import Report

parser = argparse.ArgumentParser(description='Compute ICA.')

parser.add_argument('--FileRaw', help='Input filename.')
parser.add_argument('--FileICA', help='Output file for ICA decomposition (default FileRaw-ica.fif).', default='')
parser.add_argument('--FileHTML', help='Output filename for HTML file with figures (default FileRaw_ica.html).', default='')
parser.add_argument('--EOG', help='EOG channel name(s) for correlations (e.g. EOG062, default none).', nargs='+', default=[])
parser.add_argument('--ECG', help='ECG channel name(s) for correlations (default none).', nargs='+', default=[])
parser.add_argument('--maxEOG', help='Maximum number of EOG components to remove (default 1).', type=int, default=1)
parser.add_argument('--maxECG', help='Maximum number of ECG components to remove (default 1, if --ECG not none).', type=int, default=1)

parser.add_argument('--ECGmeth', help='Method for ECG artefact detection (ctps|correlation).', default='ctps')
parser.add_argument('--EOGthresh', help='Threshold for z-score of EOG artefact detection.', type=float, default=3.)
parser.add_argument('--ECGthresh', help='Threshold for ECG artefact detection. Must accompany --ECGmeth.', type=float, default=0.25)

parser.add_argument('--ChanTypes', help='Which channel types to use (eeg|meg, default meg).', nargs='+', default=['meg'])
parser.add_argument('--RejEEG', help='Artefact threshold for EEG (uV, default 1e-3).', type=float, default=1e-3)
parser.add_argument('--RejGrad', help='Artefact threshold for Gradiometers (default 4e-10T/m).', type=float, default=4e-10)
parser.add_argument('--RejMag', help='Artefact threshold for Magnetometers (default 1e-11T).', type=float, default=1e-11)
parser.add_argument('--n_pca_comps', help='Number of components or explained fraction for pre-ICA PCA (default: 0.99).', type=str, default='0.99')
parser.add_argument('--method', help='Method for ICA decomposition (fastica|infomax|picard, default fastica).', type=str, default='fastica')

args = parser.parse_args()

print('MNE %s.\n' % mne.__version__)

if len(argv) == 1:
    # display help message when no args are passed.
    exit(1)

print(mne)

###
# ANALAYSIS PARAMETERS
###

# epoch length
tmin, tmax = -0.2, 0.2

if '.' in args.n_pca_comps:
    # if float, select n_components by explained variance of PCA
    n_components = float(args.n_pca_comps)
    print('Number of PCA components by fraction of variance (%f)' %
          n_components)

else:

    n_components = int(args.n_pca_comps)
    print('Number of PCA components: %d.' % n_components)

method = args.method  # for comparison with EEGLAB try "extended-infomax" here
print('\nUsing ICA method %s.' % method)

decim = 3  # downsample data to save time

# same random state for each ICA (not sure if beneficial?)
random_state = 23

# whether to plot on screen or only to html
show = False

# get filename stem for case with and without suffix .fif
filestem = args.FileRaw.split('.fif')[0]

# raw data input filename
if args.FileRaw[-4:] != '.fif':

    raw_fname_in = args.FileRaw + '.fif'

else:

    raw_fname_in = args.FileRaw

# filename for ICA output
if args.FileICA == '':

    ica_fname_out = filestem + '-ica.fif'

else:

    ica_fname_out = args.FileICA


# filename for ICA output
if args.FileHTML == '':

    fname_html = filestem + '-ica.html'

else:

    fname_html = args.FileHTML


###
# START ICA
###

report = Report(subject=raw_fname_in, title='ICA:')

print('###\nReading raw file %s.' % raw_fname_in)

# Read raw data
raw = mne.io.read_raw_fif(raw_fname_in, preload=True)

# They say high-pass filtering helps
print('High-pass filtering raw data at 1Hz.')
raw.filter(1., None, fir_design='firwin')

# which channel types to use
to_pick = {'meg': False, 'eeg': False, 'eog': False, 'stim': False,
           'exclude': 'bads'}

# pick channel types as specified
print('Using channel types: ')
for chtype in args.ChanTypes:

    print(chtype + ' ')
    to_pick[chtype.lower()] = True

picks_meg_eeg_eog = mne.pick_types(raw.info, meg=to_pick['meg'],
                                   eeg=to_pick['eeg'],
                                   eog=True, ecg=True, stim=to_pick['stim'],
                                   exclude=to_pick['exclude'])

# to remove non-physiological artefacts (parameters based on MNE example)
reject = {}
if to_pick['meg'] is True:

    reject['mag'] = args.RejMag
    reject['grad'] = args.RejGrad
    print('Thresholds for MEG: Grad %.1e, Mag %.1e.' % (reject['grad'],
          reject['mag']))

if to_pick['eeg'] is True:

    reject['eeg'] = args.RejEEG
    print('Threshold for EEG: %.1e.' % reject['eeg'])

picks_meg = mne.pick_types(raw.info, meg=to_pick['meg'], eeg=to_pick['eeg'],
                           eog=to_pick['eog'], stim=to_pick['stim'],
                           exclude=to_pick['exclude'])

# Compute ICA model ########################################################

print('###\nDefine the ICA object instance using %s. Number of PCA components\
       based on: %s.' % (method, str(n_components)))
ica = ICA(n_components=n_components, method=method, random_state=random_state)

print('Fitting ICA.')

ica.fit(raw, picks=picks_meg, decim=decim, reject=reject)
print(ica)

print('Plotting ICA components.')

# plot for specified channel types
for ch_type in reject.keys():

    fig_ic = ica.plot_components(ch_type=ch_type, show=show)

    captions = [ch_type.upper() + ' Components' for i in fig_ic]

    report.add_figs_to_section(fig_ic, captions=captions,
                               section='ICA Components', scale=1)

# indices of ICA components to be removed across EOG and ECG
ica_inds = []

###
# EOG COMPONENTS
###

# for all specified EOG channels
eog_inds = []  # ICA components found to be bad for EOG
eog_scores = []  # corresponding ICA scores

for eog_ch in args.EOG:

    print('\n###\nFinding components for EOG channel %s.\n' % eog_ch)

    # get single EOG trials
    eog_epochs = create_eog_epochs(raw, ch_name=eog_ch, reject=reject)

    eog_average = eog_epochs.average()  # average EOG epochs

    # find via correlation
    inds, scores = ica.find_bads_eog(eog_epochs, ch_name=eog_ch,
                                     threshold=args.EOGthresh)

    if inds != []:  # if some bad components found

        print('###\nEOG components and scores for channel %s:\n' % eog_ch)
        for [ee, ss] in zip(inds, scores):

            print('%d: %.2f\n' % (ee, ss))

        # look at r scores of components
        fig_sc = ica.plot_scores(scores, exclude=inds, show=show)

        report.add_figs_to_section(fig_sc, captions='%s Scores' % eog_ch,
                                   section='%s ICA component scores' % eog_ch,
                                   scale=1)
        # we can see that only one component is highly correlated and that this
        # component es', scale=1)

        print('Plotting raw ICA sources.')
        fig_rc = ica.plot_sources(raw, exclude=inds, show=show)

        report.add_figs_to_section(fig_rc, captions='%s Sources' % eog_ch,
                                   section='%s raw ICA sources' % eog_ch,
                                   scale=1)

        print('Plotting EOG average sources.')
        # look at source time course
        fig_so = ica.plot_sources(eog_average, exclude=inds, show=show)

        report.add_figs_to_section(fig_so, captions='%s Sources' % eog_ch,
                                   section='%s ICA Sources' % eog_ch, scale=1)

        print('Plotting EOG epochs properties.')
        fig_pr = ica.plot_properties(eog_epochs, picks=inds,
                                     psd_args={'fmax': 35.},
                                     image_args={'sigma': 1.}, show=show)

        txt_str = '%s Properties' % eog_ch
        captions = [txt_str for i in fig_pr]

        report.add_figs_to_section(fig_pr, captions=captions,
                                   section='%s ICA Properties' % eog_ch,
                                   scale=1)

        print(ica.labels_)

        # Remove ICA components ###############################################
        fig_ov = ica.plot_overlay(eog_average, exclude=inds, show=show)
        # red -> before, black -> after.

        report.add_figs_to_section(fig_ov, captions='%s Overlay' % eog_ch,
                                   section='%s ICA Overlay' % eog_ch,
                                   scale=1)

        plt.close('all')

        eog_inds += inds  # keep bad ICA components
        eog_scores += list(scores[inds])  # keep scores for bad ICA components

    else:

        print('\n###\n!!!Nothing bad found for %s!!!\n###\n' % eog_ch)

if (eog_inds != []) and (args.maxEOG > 0):  # if there are bad ECG components

    # deal with case where there are more bad ICA components than specified
    n_comps = np.min([args.maxEOG, len(eog_inds)])

    print('\n###\nUsing %d out of %d detected ICA components for EOG.' %
          (n_comps, len(eog_inds)))

    for [c, s] in zip(eog_inds, eog_scores):

        print('Component %d with score %f.' % (c, s))

    # sort to find ICA components with highest scores
    idx_sort = np.argsort(np.abs(eog_scores))

    # only keep desired number of bad ICA components with highest scores
    ica_inds += [eog_inds[idx] for idx in idx_sort[-n_comps:]]


###
# ECG COMPONENTS
###

# for all specified EOG channels

ecg_inds = []  # ICA components found to be bad for ECG
ecg_scores = []  # corresponding ICA scores

for ecg_ch in args.ECG:

    print('\n###\nFinding components for ECG channel %s.\n' % ecg_ch)

    # get single ECG trials
    ecg_epochs = create_ecg_epochs(raw, ch_name=ecg_ch, reject=reject)

    ecg_average = ecg_epochs.average()  # average ECG epochs

    # find bad ICA ECG components
    inds, scores = ica.find_bads_ecg(ecg_epochs, ch_name=ecg_ch,
                                     method=args.ECGmeth,
                                     threshold=args.ECGthresh)

    if inds != []:  # if some bad components found

        print('ECG components and scores:\n')
        for [ee, ss] in zip(inds, scores):

            print('%d: %.2f\n' % (ee, ss))

        # look at r scores of components
        fig_sc = ica.plot_scores(scores, exclude=inds, show=show)

        report.add_figs_to_section(fig_sc, captions='%s Scores' % ecg_ch,
                                   section='%s component scores' % ecg_ch,
                                   scale=1)

        print('Plotting raw ICA sources.')
        fig_rc = ica.plot_sources(raw, exclude=inds, show=show)

        report.add_figs_to_section(fig_rc, captions='%s Sources' % ecg_ch,
                                   section='%s raw sources' % ecg_ch, scale=1)

        print('Plotting ECG average sources.')
        # look at source time course
        fig_so = ica.plot_sources(ecg_average, exclude=inds, show=show)

        report.add_figs_to_section(fig_so, captions='%s Sources' % ecg_ch,
                                   section='%s ICA Sources' % ecg_ch, scale=1)

        print('Plotting ECG epochs properties.')
        fig_pr = ica.plot_properties(ecg_epochs, picks=inds,
                                     psd_args={'fmax': 35.},
                                     image_args={'sigma': 1.}, show=show)

        txt_str = '%s Properties' % ecg_ch
        captions = [txt_str for i in fig_pr]

        report.add_figs_to_section(fig_pr, captions=captions,
                                   section='%s ICA Properties' % ecg_ch,
                                   scale=1)

        print(ica.labels_)

        # Remove ICA components ###############################################
        fig_ov = ica.plot_overlay(ecg_average, exclude=inds, show=show)
        # red -> before, black -> after. Yes! We remove quite a lot!

        report.add_figs_to_section(fig_ov, captions='%s Overlay' % ecg_ch,
                                   section='%s ICA Overlay' % ecg_ch, scale=1)

        plt.close('all')

        ecg_inds += inds  # keep bad ICA components
        ecg_scores += list(scores[inds])  # keep bad ICA components

    else:

        print('\n###\n!!!Nothing bad found for %s!!!\n###\n' % ecg_ch)


if (ecg_inds != []) and (args.maxECG > 0):  # if there are bad ECG components

    # deal with case where there are more bad ICA components than specified
    n_comps = np.min([args.maxECG, len(ecg_inds)])

    print('\n###\nUsing %d out of %d detected ICA components for ECG.' %
          (n_comps, len(ecg_inds)))

    for [c, s] in zip(ecg_inds, ecg_scores):

        print('Component %d with score %f.' % (c, s))

    # sort to find ICA components with highest scores
    idx_sort = np.argsort(np.abs(ecg_scores))

    # only keep desired number of bad ICA components with highest scores
    ica_inds += [ecg_inds[idx] for idx in idx_sort[-n_comps:]]

if ica_inds != []:

    print('\n###\nSpecifying %d components to be removed:' % len(ica_inds))
    print(' '.join(str(x) for x in ica_inds))
    print('You can use Fiff_Apply_ICA now.\n###')

else:

    print('\n###\nNo bad ICA components found anywhere.')

# specify components to be removed
ica.exclude = ica_inds

###
# SAVE ICA
###

# from now on the ICA will reject this component even if no exclude
# parameter is passed, and this information will be stored to disk
# on saving

print('\nSaving ICA to %s' % (ica_fname_out))
ica.save(ica_fname_out)

print('Saving HTML report to {0}'.format(fname_html))
report.save(fname_html, overwrite=True, open_browser=True)
