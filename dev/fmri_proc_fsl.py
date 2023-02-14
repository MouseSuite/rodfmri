import os
import subprocess
import nibabel as nib



def fmri_proc_fsl(t1_orig, fmri, BrainSuitePath,atlas):

    # Get TR
    x = subprocess.check_output([f'3dinfo -tr {fmri}'],shell=True)
    TR = float(x)


    # HPF and LP cutoffs
    hp = 0.005
    lp = 0.1

    t1 = t1_orig[:-4] + '_ds.nii.gz'
    t1_bse = t1[:-4] + '.bse.nii.gz'
    resample_bin = f'{BrainSuitePath}/svreg/bin/svreg_resample.sh'

    t1_resample_cmd = f'{resample_bin} {t1_orig} {t1} -size 100 100 100'
    os.system(t1_resample_cmd)


    bse_bin = f'{BrainSuitePath}/bin/bse'
    t1_bse_cmd = f'{bse_bin} -i {t1} -o {t1_bse} --auto'

    os.system(t1_bse_cmd)

    # zip fmri

    # mask image

    fmri_mask = fmri[:-4] +'.mask.nii.gz'
    fmri_masked = fmri[:-4] +'_masked.nii.gz'

    fmri_mask_cmd = f'3dAutomask -prefix {fmri_mask} -dilate 1 {fmri}'
    os.system(fmri_mask_cmd)

    apply_mask_cmd = f'3dcalc -a {fmri} -b {fmri_mask} -expr a*b -prefix {fmri_masked}'
    os.system(apply_mask_cmd)

    # spatial smoothing
    FWHM = 0.6
    sigma=FWHM/2.3548

    fmri_smooth = fmri[:-4] + '.smooth.nii.gz'
    smooth_cmd = f'fslmaths {fmri_masked} -kernel gauss {sigma} -fmean -mas {fmri_mask} {fmri_smooth}'
    os.system(smooth_cmd)
    #zip_cmd = f'gzip -cvf {fmri} > {fmri}'
    #os.system(zip_cmd)

    # resample to regular grid


    # grand mean scaling
    fmri_gms = fmri[:-4] + '.gms.nii.gz'
    gms_cmd = f'fslmaths {fmri_smooth} -ing 10000 {fmri_gms} -odt float'
    os.system(gms_cmd)


    # band pass filtering and detrending


    fmri_filt = fmri[:-4] + '.filt.nii.gz'
    cmd_bpf = f'3dBandpass -dt {TR} -prefix {fmri_filt} {hp} {lp} {fmri_gms}'

    os.system(cmd_bpf)


    #%% FUNC->standard (3mm)


    # create fMRI mean image to be used as registration target
    fmri_example = fmri[:-4] + '.mean.nii.gz'

    mean_cmd = f'3dTstat -mean -prefix {fmri_example} {fmri_smooth}'
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
    fmri_warped = fmri[:-4] + '.filt.atlas.nii.gz'
    linwarp_cmd = f'{linreg_bin} -in {fmri_filt} -ref {atlas} -out {fmri_warped} -applyxfm -init {mat_file} -interp trilinear'
    os.system(linwarp_cmd)

