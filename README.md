# EMEG_Utilities
Software tools for EEG/MEG processing at MRC CBU.

Software utilities for routine processing of EEG/MEG data in fiff-format at the MRC CBU. 
Note: These tools are intended to be used at the MRC Cognition and Brain Sciences Unit.

Fiff_Compute_ICA.py:
Compute ICA decomposition of EEG/MEG data and visualise the results in an HTML file (using MNE-Python).
This is a pre-requisite for Fiff_Apply_ICA.py (below), but can also be useful for visual inspection of raw data (e.g. to check for conspicuous artefacts).

Fiff_Apply_ICA.py:
Applies the ICA decomposition obtained with Fiff_Apply_ICA.py (above) to raw EEG/MEG data (using MNE-Python).

Fiff_HeadPositions.py:
Visualise the head movement from Maxfilter output for raw EEG/MEG data (using MNE-Python).

AverageSensorArray.py:
For a list of fiff-files, determine the one with the most average position of the sensor array.
For example, this can be used as a reference sensor array for the Maxfilter "-trans" option across subjects.

Olaf Hauk, July 2019
