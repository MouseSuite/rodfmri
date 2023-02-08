import os


t1_orig = '/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-1/anat/sub-jgrADc1NT_ses-1_acq-RARE_T2w.nii'
t1 = t1_orig[:-4] + '_ds.nii.gz'
t1_bse = t1[:-4] + '.bse.nii.gz'
resample_bin = '/home/ajoshi/BrainSuite21a/svreg/bin/svreg_resample.sh'

t1_resample_cmd = f'{resample_bin} {t1_orig} {t1} -size 100 100 100'
os.system(t1_resample_cmd)


bse_bin = '/home/ajoshi/BrainSuite21a/bin/bse'
t1_bse_cmd = f'{bse_bin} -i {t1} -o {t1_bse} --auto'

os.system(t1_bse_cmd)


# zip fmri


fmri_orig = '/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-1/func/sub-jgrADc1NT_ses-1_task-rest_acq-EPI_bold.nii'

fmri = fmri_orig[:-4] + '.nii.gz'

zip_cmd = f'gzip -cvf {fmri_orig} > {fmri}'
os.system(zip_cmd)

# create fMRI mean image to be used as registration target
fmri_example = fmri_orig[:-4] + '.mean.nii.gz'

mean_cmd = f'3dTstat -mean -prefix {fmri_example} {fmri}'
os.system(mean_cmd)



# Register t1 to fMRI

linreg_bin = '/home/ajoshi/projects/rodreg/dev/aligner.py'
t1_bse_lin = t1[:-7] + '.lin.nii.gz'

lin_align_cmd = f'{linreg_bin} {t1_bse} {fmri_example} {t1_bse_lin} -l cc'

os.system(lin_align_cmd)



# warp atlas to subj

atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_average_masked.nii.gz'
linreg_bin = '/home/ajoshi/projects/rodreg/dev/aligner.py'
t1_bse_lin = t1[:-7] + '.lin.atlas.nii.gz'
lin_align_cmd = f'{linreg_bin} {t1_bse} {atlas} {t1_bse_lin} -l cc'
os.system(lin_align_cmd)

# bfp processing

apply_warp_to_4D(ddef_file,)


