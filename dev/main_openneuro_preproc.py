import glob
from fmri_proc_fsl import fmri_proc_fsl
import os


sublist = glob.glob('/home/ajoshi/Desktop/openneuro/sub*')
BrainSuitePath = '/home/ajoshi/BrainSuite21a'
atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'


for s in sublist:

    dirname, subid = os.path.split(s)
    sess = 1
    t1_orig = f'{dirname}/{subid}/ses-{sess}/anat/{subid}_ses-{sess}_acq-RARE_T2w.nii'
    fmri_orig = f'{dirname}/{subid}/ses-{sess}/func/{subid}_ses-{sess}_task-rest_acq-EPI_bold.nii'

    if os.path.isfile(fmri_orig):
        fmri_proc_fsl(t1_orig, fmri_orig, BrainSuitePath, atlas)


    sess = 2
    t1_orig = f'{dirname}/{subid}/ses-{sess}/anat/{subid}_ses-{sess}_acq-RARE_T2w.nii'
    fmri_orig = f'{dirname}/{subid}/ses-{sess}/func/{subid}_ses-{sess}_task-rest_acq-EPI_bold.nii'
    
    if os.path.isfile(fmri_orig):
        fmri_proc_fsl(t1_orig, fmri_orig, BrainSuitePath, atlas)
