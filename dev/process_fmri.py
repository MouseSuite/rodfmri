#!/bin/python3

import os
import subprocess
import nibabel as nib
import argparse

class dscolors:
	red  	 = '\033[91m'
	green  = '\033[92m'
	yellow = '\033[93m'
	blue   = '\033[94m'
	purple = '\033[95m'
	cyan   = '\033[96m'
	clear  = '\033[0m'
	bold   = '\033[1m'
	ul     = '\033[4m'

brainSuitePath='/opt/BrainSuite21a'
atlasPath='/opt/rodenttools/atlases/'

def process(outdir, datapath,subjID,session,atlas):
	sessionFolder=f'{datapath}/{subjID}/ses-{session}'
	t1_orig = f'{sessionFolder}/anat/{subjID}_ses-{session}_acq-RARE_T2w.nii'
	fmri_orig = f'{sessionFolder}/func/{subjID}_ses-{session}_task-rest_acq-EPI_bold.nii'

	subjectOutputDir=f'{outdir}/{subjID}/ses-{session}'
	outputBase=f'{subjectOutputDir}'
	outputAnatDir=f'{outputBase}/{subjID}/ses-{session}/anat/'
	outputFuncDir=f'{outputBase}/{subjID}/ses-{session}/func/'
	subjBase=f'{subjID}_ses-{session}_acq-RARE_T2w'
	subjFuncBase=f'{subjID}_ses-{session}_task-rest_acq-EPI_bold'
	outputAnatBase=outputAnatDir+subjBase+'_ds'
	outputFuncBase=outputFuncDir+subjFuncBase
	resample_bin = f'{brainSuitePath}/svreg/bin/svreg_resample.sh'
	bse_bin = f'{brainSuitePath}/bin/bse'

	print(dscolors.blue+'Initializing output dirs...'+dscolors.clear)
	os.system(f'install -d {outputAnatDir}')
	os.system(f'install -d {outputFuncDir}')

	print(dscolors.blue+'resampling'+dscolors.clear)
	print(dscolors.green+f'3dinfo -tr {fmri_orig}'+dscolors.clear)
	x = subprocess.check_output([f'3dinfo -tr {fmri_orig}'],shell=True)
	TR = float(x)
	hp = 0.005
	lp = 0.1

	t1 = outputAnatBase+'.nii.gz'
	t1_bse = outputAnatBase+'.bse.nii.gz'

	t1_resample_cmd = f'{resample_bin} {t1_orig} {t1} -size 100 100 100'
	os.system(t1_resample_cmd)

	print(dscolors.blue+'Removing non-brain tissue...'+dscolors.clear)
	t1_bse_cmd = f'{bse_bin} -i {t1} -o {t1_bse} --auto'

	os.system(t1_bse_cmd)
	# zip fmri
	fmri = fmri_orig #[:-4] + '.nii.gz'
	# mask image
	fmri_mask = outputFuncBase +'.mask.nii.gz'
	fmri_masked = outputFuncBase +'_masked.nii.gz'

	fmri_mask_cmd = f'3dAutomask -prefix {fmri_mask} -dilate 1 {fmri}'
	os.system(fmri_mask_cmd)
	apply_mask_cmd = f'3dcalc -a {fmri} -b {fmri_mask} -expr a*b -prefix {fmri_masked}'
	os.system(apply_mask_cmd)

	# spatial smoothing
	print(dscolors.blue+'Removing non-brain tissue...'+dscolors.clear)

	FWHM = 0.6
	sigma=FWHM/2.3548

	fmri_smooth = outputAnatBase + '.smooth.nii.gz'
	smooth_cmd = f'fslmaths {fmri_masked} -kernel gauss {sigma} -fmean -mas {fmri_mask} {fmri_smooth}'
	os.system(smooth_cmd)

	# grand mean scaling
	print(dscolors.blue+'Performing grand mean scaling...'+dscolors.clear)
	fmri_gms = outputFuncBase + '.gms.nii.gz'
	gms_cmd = f'fslmaths {fmri_smooth} -ing 10000 {fmri_gms} -odt float'
	os.system(gms_cmd)


	# band pass filtering and detrending
	print(dscolors.blue+'Performing band pass filtering and detrending...'+dscolors.clear)
	fmri_filt = outputFuncBase + '.filt.nii.gz'
	cmd_bpf = f'3dBandpass -dt {TR} -prefix {fmri_filt} {hp} {lp} {fmri_gms}'

	os.system(cmd_bpf)


	#%% FUNC->standard (3mm)

	print(dscolors.blue+'Creating mean image...'+dscolors.clear)
	# create fMRI mean image to be used as registration target
	fmri_example = outputFuncBase + '.mean.nii.gz'
	mean_cmd = f'3dTstat -mean -prefix {fmri_example} {fmri_smooth}'
	os.system(mean_cmd)

	# Register t1 to fMRI
	print(dscolors.blue+'Register t1 to fMRI...'+dscolors.clear)
	linreg_bin = 'flirt'
	t1_bse_fmri = outputAnatBase + '.fmri.nii.gz'

	lin_align_cmd = f'{linreg_bin} -in {t1_bse} -ref {fmri_example} -out {t1_bse_fmri} -dof 6'
	os.system(lin_align_cmd)

	# warp subject to atlas
	print(dscolors.blue+'Warping subject to atlas...'+dscolors.clear)
	linreg_bin = 'flirt'
	t1_bse_lin = outputAnatBase + '.lin.atlas.nii.gz'
	mat_file = outputAnatBase + '.lin.mat'
	lin_align_cmd = f'{linreg_bin} -in {t1_bse_fmri} -ref {atlas} -out {t1_bse_lin} -omat {mat_file}'
	print(dscolors.green+lin_align_cmd+dscolors.clear)
	os.system(lin_align_cmd)

	# Warp fmri to atlas
	print(dscolors.blue+'Warping fmri to atlas...'+dscolors.clear)
	fmri_warped = outputFuncBase + '.filt.atlas.nii.gz'
	linwarp_cmd = f'{linreg_bin} -in {fmri_filt} -ref {atlas} -out {fmri_warped} -applyxfm -init {mat_file} -interp trilinear'
	print(dscolors.green+linwarp_cmd+dscolors.clear)
	os.system(linwarp_cmd)

	print(dscolors.green+'Finished.'+dscolors.clear)

def main():
	# atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'
	# datasetPath='/home/ajoshi/projects/rodfmri/dev/test_cases/'
	atlasfile='hello'
	subid = 'sub-jgrADc11L' #'sub-jgrADc1NT'
	sess = 1

	parser = argparse.ArgumentParser(description='rodent anatomical pipeline')
	parser.add_argument('-p','--datapath', type=str, help='study directory', required=True)
	parser.add_argument('-o','--output-dir', type=str, help='study directory', required=True)
	parser.add_argument('-s','--subjID', type=str, help='subject ID', required=True)
	parser.add_argument('--session', type=int, default=1, help='subject ID')
	parser.add_argument('-a','--atlas', type=str, default='dsurqe64', help='anatomical atlas by name',choices={'dsurqe', 'dsurqe64', 'dsurqe128', 'eae'})
	parser.add_argument('-b','--brainsuite-path', type=str, help='path to BrainSuite installation')
	parser.add_argument('--atlas-image', type=str, help='anatomical atlas image filename (overrides -a)')
	args = parser.parse_args()
	if (args.atlas=='dsurqe'): atlasfile=atlasPath+'/DSURQE_40micron_UCLA/DSURQE_40micron_average_masked.nii.gz'
	elif (args.atlas=='dsurqe64'): atlasfile=atlasPath+'/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'
	elif (args.atlas=='dsurqe128'): atlasfile=atlasPath+'/DSURQE_40micron_UCLA/DSURQE_40micron_128_average_masked.nii.gz'
	if args.atlas_image is not None: atlasfile=args.atlas_image
	if args.brainsuite_path is not None: brainSuitePath=args.atlas_image

	print(args.output_dir,args.datapath,args.subjID,args.session,atlasfile)
	process(args.output_dir,args.datapath,args.subjID,args.session,atlasfile)

if __name__ == "__main__":
	main()
