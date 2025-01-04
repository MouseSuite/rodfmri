import glob
from fmri_proc_fsl import fmri_proc_fsl
import os
from myutils import plot_fmri_overlay
from itertools import product


sublist = glob.glob('/deneb_disk/RodentTools/data/openneuro/ds001890/sub*')
BrainSuitePath = '/home/ajoshi/Software/BrainSuite23a'
atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'

# set environment variable BrainSuiteMCRPath to the path of BrainSuite Matlab Compiler Runtime
os.environ['BrainSuiteMCR'] = '/home/ajoshi/Software/MATLAB/MATLAB_Runtime/R2023a'

# loop over subjects and sessions. Use single for loop using zip
# to loop over both subjects and sessions simultaneously
# and avoid code duplication
sessions = [1, 2]

for s, sess in product(sublist, sessions):

    print(f'Processing subject {s} session {sess}...')

    dirname, subid = os.path.split(s)
    t1_orig = f'{dirname}/{subid}/ses-{sess}/anat/{subid}_ses-{sess}_acq-RARE_T2w.nii'
    fmri_orig = f'{dirname}/{subid}/ses-{sess}/func/{subid}_ses-{sess}_task-rest_acq-EPI_bold.nii'
    fmri2atlas = fmri_orig[:-4] + '.filt.atlas.nii.gz'

    if os.path.isfile(fmri_orig) and not os.path.isfile(fmri2atlas):
        fmri_proc_fsl(t1_orig, fmri_orig, BrainSuitePath, atlas)

    if os.path.isfile(fmri_orig) and os.path.isfile(fmri2atlas):
        plot_fmri_overlay(fmri2atlas, atlas, threshold=3, time_point=3, average_time=False)



