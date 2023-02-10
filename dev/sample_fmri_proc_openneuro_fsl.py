import os

subid = 'sub-jgrADc1NT'
sess = 2

t1_orig = f'/home/ajoshi/projects/rodfmri/dev/test_cases/{subid}/ses-{sess}/anat/{subid}_ses-{sess}_acq-RARE_T2w.nii'
fmri_orig = f'/home/ajoshi/projects/rodfmri/dev/test_cases/{subid}/ses-{sess}/func/{subid}_ses-{sess}_task-rest_acq-EPI_bold.nii'

t1 = t1_orig[:-4] + '_ds.nii.gz'
t1_bse = t1[:-4] + '.bse.nii.gz'
resample_bin = '/home/ajoshi/BrainSuite21a/svreg/bin/svreg_resample.sh'
atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'

t1_resample_cmd = f'{resample_bin} {t1_orig} {t1} -size 100 100 100'
os.system(t1_resample_cmd)


bse_bin = '/home/ajoshi/BrainSuite21a/bin/bse'
t1_bse_cmd = f'{bse_bin} -i {t1} -o {t1_bse} --auto'

os.system(t1_bse_cmd)


# zip fmri



fmri = fmri_orig #[:-4] + '.nii.gz'

#zip_cmd = f'gzip -cvf {fmri_orig} > {fmri}'
#os.system(zip_cmd)

#fmri resample to regular grid




# create fMRI mean image to be used as registration target
fmri_example = fmri_orig[:-4] + '.mean.nii.gz'

mean_cmd = f'3dTstat -mean -prefix {fmri_example} {fmri}'
os.system(mean_cmd)



# Register t1 to fMRI

linreg_bin = 'flirt'
t1_bse_fmri = t1[:-7] + '.fmri.nii.gz'

lin_align_cmd = f'{linreg_bin} -in {t1_bse} -ref {fmri_example} -out {t1_bse_fmri} -dof 6'
os.system(lin_align_cmd)



# warp subject to atlas

linreg_bin = 'flirt'
t1_bse_lin = t1[:-7] + '.lin.atlas.nii.gz'
mat_file = t1[:-7] + '.lin.mat'

lin_align_cmd = f'{linreg_bin} -in {t1_bse_fmri} -ref {atlas} -out {t1_bse_lin} -omat {mat_file}'
os.system(lin_align_cmd)




# Warp fmri to atlas
fmri_warped = fmri[:-7] + '.atlas.nii.gz'
linwarp_cmd = f'{linreg_bin} -in {fmri} -ref {atlas} -out {fmri_warped} -applyxfm -init {mat_file} -interp trilinear'
os.system(linwarp_cmd)