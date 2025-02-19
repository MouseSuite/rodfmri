# README #

This repository contains scripts and utilities for processing and analyzing fMRI data using BrainSync and other neuroimaging tools.

## What is this repository for?

This repository provides scripts to preprocess fMRI data, perform BrainSync, and conduct statistical analyses on the processed data.
BrainSync is a method for synchronizing fMRI time-series data across subjects.  Please cite the following publication if you use this method:

Joshi, A. A., Chong, M., Li, J., Choi, S., & Leahy, R. M. (2018). Are you thinking what I'm thinking? Synchronization of resting fMRI time-series across subjects. NeuroImage, 172, 740-752. https://doi.org/10.1016/j.neuroimage.2018.01.058


### Prerequisites

- Python 3.x
- BrainSuite software
- FSL software

### Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required Python packages:
    ```sh
    pip install nibabel numpy scipy pandas matplotlib nilearn statsmodels tqdm
    ```

3. Set the environment variable for BrainSuite Matlab Compiler Runtime:
    ```sh
    export BrainSuiteMCR=/path/to/MATLAB_Runtime/R2023a
    ```

### Configuration

Update the paths in the scripts to match your local setup, such as the paths to the BrainSuite and FSL installations, and the data directories.

## How to run the scripts

### Preprocess fMRI data


The `fmri_proc.py` script preprocesses fMRI data using a combination of FSL and BrainSuite tools. The preprocessing steps include resampling the T1 image, brain extraction, masking the fMRI image, spatial smoothing, grand mean scaling, band-pass filtering, and registration to an atlas. These steps are essential for preparing the fMRI data for further analysis.

## Usage
To use the fmri_proc.py script, call the fmri_proc function with the appropriate arguments:

- `t1_orig`: Path to the original T1-weighted anatomical image.
- `fmri`: Path to the fMRI image.
- `BrainSuitePath`: Path to the BrainSuite installation directory.
- `atlas`: Path to the atlas image.
- `hp`: High-pass filter cutoff frequency (default: 0.005 Hz).
- `lp`: Low-pass filter cutoff frequency (default: 0.1 Hz).
- `FWHM`: Full-width at half-maximum for spatial smoothing (default: 0.6 mm).

## Algorithm
The preprocessing algorithm consists of the following steps:

1. **Resample T1 Image**: Resample the T1-weighted anatomical image to 0.1mm isotropic resolution using FSL's `flirt` tool.
2. **Brain Extraction**: Perform brain extraction on the resampled T1 image using BrainSuite's `bse` tool.
3. **fMRI Masking**: Create a brain mask for the fMRI image using AFNI's `3dAutomask` tool and apply the mask using `3dcalc`.
4. **Spatial Smoothing**: Apply spatial smoothing to the masked fMRI image using FSL's `fslmaths` tool with a Gaussian kernel.
5. **Grand Mean Scaling**: Perform grand mean scaling on the smoothed fMRI image using FSL's `fslmaths` tool.
6. **Band-Pass Filtering**: Apply band-pass filtering to the grand mean scaled fMRI image using AFNI's `3dBandpass` tool.

7. Registration to Atlas:
   - Create an fMRI mean image using AFNI's `3dTstat` tool.
   - Register the T1 image to the fMRI mean image using our machine learning-based tool or FSL's `flirt` tool.
   - Register the T1 image to the atlas using FSL's `flirt` tool.
   - Warp the fMRI data to the atlas using FSL's `flirt` tool.

By following these steps, the fMRI data is preprocessed and aligned to a standard anatomical space, making it ready for further analysis. 


## Sample scripts

To preprocess fMRI data, run the ```dev/main_openneuro_preproc.py``` script. The script processes fMRI data for each subject and session aligning to an atlas.
```
python main_openneuro_preproc.py
```
The code that does the preprocessing is ```fmri_proc_fsl.py```.


### Sample scripts for statistics and group analysis
To perform group analysis, use the ```dev/main_group_diff_3month_6month.py``` script:
To perform BrainSync on fMRI data, use the ```dev/main_brainsync.py script```:



## License
This project is licensed under the GPL (V2) License - see the [LICENSE](License_gpl-2.0.txt) file for details.

## Support
For technical support, please contact [ajoshi@usc.edu](mailto:ajoshi@usc.edu).

## Acknowledgments
- This project is supported by NIH Grant R01-NS121761 (PIs: David Shattuck and Allan MacKenzie-Graham).



 
