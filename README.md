# README #

This repository contains scripts and utilities for processing and analyzing fMRI data using BrainSync and other neuroimaging tools.

## What is this repository for?

This repository provides scripts to preprocess fMRI data, perform BrainSync, and conduct statistical analyses on the processed data.

## How do I get set up?

### Prerequisites

- Python 3.x
- Required Python packages: [`nibabel`](/home/ajoshi/my_venv/lib/python3.11/site-packages/nibabel/__init__.py ), [`numpy`](/home/ajoshi/my_venv/lib/python3.11/site-packages/numpy/__init__.py ), [`scipy`](/home/ajoshi/my_venv/lib/python3.11/site-packages/scipy/__init__.py ), [`pandas`](/home/ajoshi/my_venv/lib/python3.11/site-packages/pandas/__init__.py ), [`matplotlib`](/home/ajoshi/my_venv/lib/python3.11/site-packages/matplotlib/__init__.py ), [`nilearn`](/home/ajoshi/my_venv/lib/python3.11/site-packages/nilearn/__init__.py ), [`statsmodels`](/home/ajoshi/my_venv/lib/python3.11/site-packages/statsmodels/__init__.py ), [`tqdm`](/home/ajoshi/my_venv/lib/python3.11/site-packages/tqdm/__init__.py )
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

To preprocess fMRI data using FSL, run the [main_openneuro_preproc.py](http://_vscodecontentref_/2) ) script:
```sh
python dev/main_openneuro_preproc.py
```


### Perform BrainSync
To perform BrainSync on fMRI data, use the dev/main_brainsync.py script:

### Group Analysis
To perform group analysis, use the dev/main_group_diff_3month_6month.py script:

## Contribution guidelines
###Writing tests
Add tests for new features and bug fixes.

### Code review
Submit pull requests for code review before merging changes.

### Other guidelines
Follow PEP 8 for Python code style.

### Who do I talk to?
For questions or support, contact ajoshi@usc.edu.



 
