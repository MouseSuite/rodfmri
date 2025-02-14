"""
This module provides utilities for working with MRI and fMRI data.
"""

from nilearn import image, plotting

from matplotlib import pyplot as plt

def plot_fmri_overlay(fmri_image_path, anatomical_image_path, 
                       threshold=3, time_point=3, average_time=False):
    """
    Plot an fMRI activation map overlaid on an anatomical image.
    
    Parameters:
    - fmri_image_path (str): Path to the 4D fMRI data (NIfTI file).
    - anatomical_image_path (str): Path to the anatomical image (NIfTI file).
    - threshold (float): Threshold for activation values in the fMRI map.
    - time_point (int, optional): Specific time point to extract from the 4D fMRI image.
    - average_time (bool): Whether to average across time points if time_point is not specified.
    """
    subid = fmri_image_path.split('/')[-1].split('_')[0]
    # Load images
    fmri_img_4d = image.load_img(fmri_image_path)
    anat_img = image.load_img(anatomical_image_path)
    
    # Handle 4D fMRI data
    if fmri_img_4d.ndim == 4:
        if time_point is not None:
            fmri_img_3d = image.index_img(fmri_img_4d, time_point)
        elif average_time:
            fmri_img_3d = image.mean_img(fmri_img_4d)
        else:
            raise ValueError("Specify either 'time_point' or enable 'average_time'.")
    else:
        fmri_img_3d = fmri_img_4d  # Already 3D
    
    # Plot overlay
    plotting.plot_stat_map(fmri_img_3d, bg_img=anat_img, threshold=threshold, alpha=0.5,
                           display_mode='ortho', dim=-0.5, title=f'fmri image:{subid}', output_file=fmri_image_path[:-7] + '.png', cut_coords=(0, 0, 0))  
    #plotting.show()
    #plt.pause(1)  # Pause for a short time to allow the plot to render