import os
import subprocess
import nibabel as nib



def fmri_proc(t1_orig, fmri, BrainSuitePath,atlas,hp = 0.005,lp = 0.1,FWHM = 0.6, fmri_mask_custom = None):

    # Check if t1_orig is a valid file
    if (t1_orig is None) or (not os.path.isfile(t1_orig)):
        # If t1_orig is None or not a valid file, set ANAT_AVL to False
        ANAT_AVL = False # Anatomical image not found
        print(f"Anatomical image not found: {t1_orig}")

    # Get TR
    x = subprocess.check_output([f'3dinfo -tr {fmri}'],shell=True)
    TR = float(x)


    if ANAT_AVL:
        # Resample T1 to 0.1mm isotropic
        t1 = t1_orig[:-7] + '_ds.nii.gz'
        t1_bse = t1[:-7] + '.bse.nii.gz'
        t1_resample_cmd = f'flirt -in {t1_orig} -ref {t1_orig} -applyisoxfm 0.1 -out {t1}'

        os.system(t1_resample_cmd)


        bse_bin = f'{BrainSuitePath}/bin/bse'
        t1_bse_cmd = f'{bse_bin} -i {t1} -o {t1_bse} --auto'

        os.system(t1_bse_cmd)

        # zip fmri

    # mask image


    if fmri_mask_custom is not None:
        # Use custom mask
        fmri_mask = fmri_mask_custom
        fmri_masked = fmri[:-7] + '_masked.nii.gz'
        apply_mask_cmd = f'3dcalc -a {fmri} -b {fmri_mask} -expr a*b -prefix {fmri_masked}'
        os.system(apply_mask_cmd)
    else:
        fmri_mask = fmri[:-7] +'.mask.nii.gz'
        fmri_masked = fmri[:-7] +'_masked.nii.gz'

        fmri_mask_cmd = f'3dAutomask -prefix {fmri_mask} -dilate 1 {fmri}'
        os.system(fmri_mask_cmd)

        apply_mask_cmd = f'3dcalc -a {fmri} -b {fmri_mask} -expr a*b -prefix {fmri_masked}'
        os.system(apply_mask_cmd)


    # spatial smoothing
    sigma=FWHM/2.3548

    fmri_smooth = fmri[:-7] + '.smooth.nii.gz'
    smooth_cmd = f'fslmaths {fmri_masked} -kernel gauss {sigma} -fmean -mas {fmri_mask} {fmri_smooth}'
    os.system(smooth_cmd)
    #zip_cmd = f'gzip -cvf {fmri} > {fmri}'
    #os.system(zip_cmd)

    # resample to regular grid


    # grand mean scaling
    fmri_gms = fmri[:-7] + '.gms.nii.gz'
    gms_cmd = f'fslmaths {fmri_smooth} -ing 10000 {fmri_gms} -odt float'
    os.system(gms_cmd)


    # band pass filtering and detrending


    fmri_filt = fmri[:-7] + '.filt.nii.gz'
    cmd_bpf = f'3dBandpass -dt {TR} -prefix {fmri_filt} {hp} {lp} {fmri_gms}'

    os.system(cmd_bpf)


    #%% FUNC->standard (3mm)


    # create fMRI mean image to be used as registration target
    fmri_example = fmri[:-7] + '.mean.nii.gz'

    mean_cmd = f'3dTstat -mean -prefix {fmri_example} {fmri_smooth}'
    os.system(mean_cmd)



    if ANAT_AVL:
        # Register t1 to fMRI

        linreg_bin = 'flirt'
        t1_bse_fmri = t1[:-7] + '.fmri.nii.gz'

        lin_align_cmd = f'{linreg_bin} -in {t1_bse} -ref {fmri_example} -out {t1_bse_fmri} -dof 6'
        os.system(lin_align_cmd)

    else:
        # If T1 image is not available, create a dummy T1 image
        t1_bse_fmri = fmri[:-7] + '.fmri.nii.gz'
        # copy mean fmri image to t1_bse_fmri
        copy_cmd = f'cp {fmri_example} {t1_bse_fmri}'
        os.system(copy_cmd)

    # warp subject to atlas

    linreg_bin = 'flirt'
    if ANAT_AVL:
        t1_bse_lin = t1[:-7] + '.lin.atlas.nii.gz'
        mat_file = t1[:-7] + 'anat_2_atlas.lin.mat'
    else:
        t1_bse_lin = fmri[:-7] + '.lin.atlas.nii.gz'
        mat_file = fmri[:-7] + 'fmri_2_atlas.lin.mat'

    lin_align_cmd = f'{linreg_bin} -in {t1_bse_fmri} -ref {atlas} -out {t1_bse_lin} -omat {mat_file}'
    os.system(lin_align_cmd)




    # Warp fmri to atlas
    fmri_warped = fmri[:-7] + '.filt.atlas.nii.gz'
    linwarp_cmd = f'{linreg_bin} -in {fmri_filt} -ref {atlas} -out {fmri_warped} -applyxfm -init {mat_file} -interp trilinear'
    os.system(linwarp_cmd)

