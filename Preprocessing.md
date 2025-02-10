# fMRI Preprocessing with FSL and BrainSuite

This document provides detailed documentation for the `fmri_proc_fsl.py` script, which preprocesses fMRI data using FSL and BrainSuite tools. 

## Introduction

The `fmri_proc_fsl.py` script preprocesses fMRI data using a combination of FSL and BrainSuite tools. The preprocessing steps include resampling the T1 image, brain extraction, masking the fMRI image, spatial smoothing, grand mean scaling, band-pass filtering, and registration to an atlas. These steps are essential for preparing the fMRI data for further analysis.

## Usage
To use the fmri_proc_fsl.py script, call the fmri_proc_fsl function with the appropriate arguments:

. t1_orig: Path to the original T1-weighted anatomical image.
. fmri: Path to the fMRI image.
. BrainSuitePath: Path to the BrainSuite installation directory.
. atlas: Path to the atlas image.
. hp: High-pass filter cutoff frequency (default: 0.005 Hz).
. lp: Low-pass filter cutoff frequency (default: 0.1 Hz).
. FWHM: Full-width at half-maximum for spatial smoothing (default: 0.6 mm).

## Algorithm
The preprocessing algorithm consists of the following steps:

1. Resample T1 Image: Resample the T1-weighted anatomical image to 0.1mm isotropic resolution using FSL's flirt tool.
2. Brain Extraction: Perform brain extraction on the resampled T1 image using BrainSuite's bse tool.
3. fMRI Masking: Create a brain mask for the fMRI image using AFNI's 3dAutomask tool and apply the mask using 3dcalc.
4. Spatial Smoothing: Apply spatial smoothing to the masked fMRI image using FSL's fslmaths tool with a Gaussian kernel.
5. Grand Mean Scaling: Perform grand mean scaling on the smoothed fMRI image using FSL's fslmaths tool.
6. Band-Pass Filtering: Apply band-pass filtering to the grand mean scaled fMRI image using AFNI's 3dBandpass tool.

7. Registration to Atlas:
 - Create an fMRI mean image using AFNI's 3dTstat tool.
 - Register the T1 image to the fMRI mean image using FSL's flirt tool.
 - Register the T1 image to the atlas using FSL's flirt tool.
 - Warp the fMRI data to the atlas using FSL's flirt tool.

By following these steps, the fMRI data is preprocessed and aligned to a standard anatomical space, making it ready for further analysis. 
