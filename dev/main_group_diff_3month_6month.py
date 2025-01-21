import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
from brainsync import brainSync, normalizeData
import nibabel as nb
from scipy import stats

from statsmodels.stats.multitest import multipletests

from nilearn import plotting
import matplotlib.pyplot as plt



# load group brainSync data
data = np.load("group_diff_fmri.npz")
fmri_atlas = data["X2"]
Os = data["Os"]
Costdif = data["Costdif"]
TotalError = data["TotalError"]
tg_or_wt = data["tg_or_wt"]
sublist = data["sublist"]
msk = data["msk"]
atlas = str(data["atlas"])
fmri_data_all_sub = data["fmri_data_all_sub"]
ctrl_data = data["ctrl_data"]

"""
tg_or_wt[nsub] = -2 # both sessions are not available
tg_or_wt[nsub] = 1 # control group
tg_or_wt[nsub] = 2 # TG group
"""

ctrl_grp = fmri_data_all_sub[:, :, tg_or_wt == 1]   # control group 
ctrl_3month = ctrl_grp[:, :, 0::2]  # control group 3 month data
ctrl_6month = ctrl_grp[:, :, 1::2]  # control group 6 month data


tg_grp = fmri_data_all_sub[:, :, tg_or_wt == 2]   # TG group 
tg_3month = tg_grp[:, :, 0::2]  # TG group 3 month data
tg_6month = tg_grp[:, :, 1::2]  # TG group 6 month data


print("ctrl_3month shape: ", ctrl_3month.shape)

ctrl_diff = np.zeros((ctrl_3month.shape[2], ctrl_3month.shape[0]))
tg_diff = np.zeros((tg_3month.shape[2], tg_3month.shape[0]))

for i in range(ctrl_3month.shape[2]):

    f1img = ctrl_3month[:, :, i]
    f1img, _, _ = normalizeData(f1img.T)
    f2img, _, _ = normalizeData(fmri_atlas)

    diff = np.sqrt(np.sum((f1img - f2img) ** 2, axis=0))
    f2img_sync, _ = brainSync(f1img, f2img)
    diff_sync = np.sqrt(np.sum((f1img - f2img_sync) ** 2, axis=0))
    ctrl_diff[i, :] = diff_sync



for i in range(tg_3month.shape[2]):
    f1img = tg_3month[:, :, i]
    f1img, _, _ = normalizeData(f1img.T)
    f2img, _, _ = normalizeData(fmri_atlas)

    diff = np.sqrt(np.sum((f1img - f2img) ** 2, axis=0))
    f2img_sync, _ = brainSync(f1img, f2img)
    diff_sync = np.sqrt(np.sum((f1img - f2img_sync) ** 2, axis=0))
    tg_diff[i, :] = diff_sync


t_stat, p_val = stats.ttest_ind(tg_diff, ctrl_diff, axis=0)

nan_msk = np.isnan(t_stat)
t_stat[nan_msk] = 0
p_val[nan_msk] = 1
# correct for multiple comparisons

p_val_corr = multipletests(p_val, alpha=0.05, method="fdr_bh")

p_val = p_val_corr[1]

# load atlas nifti image

v = nb.load(atlas)

vout = np.zeros(v.shape)
vout[msk] = t_stat

t_stat_img = nb.Nifti1Image(vout, v.affine, v.header)
t_stat_img.to_filename("t_stat_3m.nii.gz")

vout[msk] = p_val
#20*(0.05 - p_val)*(p_val<0.05)

p_val_img = nb.Nifti1Image(vout, v.affine, v.header)
p_val_img.to_filename("p_val_3m.nii.gz")

# Plot the t_stat and p_val images


fig, ax = plt.subplots(2, 1, figsize=(9, 6))

plotting.plot_stat_map(
    "t_stat_3m.nii.gz",
    bg_img=atlas,
    threshold=1e-6,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="t_stat",
    axes=ax[0],
    colorbar=True,
    vmax=5,
    vmin=-5,
    cmap="coolwarm",
)

plotting.plot_stat_map(
    "p_val_3m.nii.gz",
    bg_img=atlas,
    threshold=0,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="p_val",
    axes=ax[1],
    colorbar=True,
    vmax=0.05,
    cmap="hot_r",  # Inverted colormap
)

plt.savefig("3m_diff.png")

plt.show()



# Do the same for 6 month data
ctrl_diff = np.zeros((ctrl_6month.shape[2], ctrl_6month.shape[0]))
tg_diff = np.zeros((tg_6month.shape[2], tg_6month.shape[0]))

for i in range(ctrl_6month.shape[2]):
    f1img = ctrl_6month[:, :, i]
    f1img, _, _ = normalizeData(f1img.T)
    f2img, _, _ = normalizeData(fmri_atlas)

    diff = np.sqrt(np.sum((f1img - f2img) ** 2, axis=0))
    f2img_sync, _ = brainSync(f1img, f2img)
    diff_sync = np.sqrt(np.sum((f1img - f2img_sync) ** 2, axis=0))
    ctrl_diff[i, :] = diff_sync

for i in range(tg_6month.shape[2]):
    f1img = tg_6month[:, :, i]
    f1img, _, _ = normalizeData(f1img.T)
    f2img, _, _ = normalizeData(fmri_atlas)

    diff = np.sqrt(np.sum((f1img - f2img) ** 2, axis=0))
    f2img_sync, _ = brainSync(f1img, f2img)
    diff_sync = np.sqrt(np.sum((f1img - f2img_sync) ** 2, axis=0))
    tg_diff[i, :] = diff_sync

t_stat, p_val = stats.ttest_ind(tg_diff, ctrl_diff, axis=0)

nan_msk = np.isnan(t_stat)
t_stat[nan_msk] = 0
p_val[nan_msk] = 1
# correct for multiple comparisons

p_val_corr = multipletests(p_val, alpha=0.05, method="fdr_bh")

p_val = p_val_corr[1]

# load atlas nifti image

v = nb.load(atlas)

vout = np.zeros(v.shape)
vout[msk] = t_stat

t_stat_img = nb.Nifti1Image(vout, v.affine, v.header)
t_stat_img.to_filename("t_stat_6m.nii.gz")

vout[msk] = p_val
#20*(0.05 - p_val)*(p_val<0.05)

p_val_img = nb.Nifti1Image(vout, v.affine, v.header)
p_val_img.to_filename("p_val_6m.nii.gz")

# Plot the t_stat and p_val images


fig, ax = plt.subplots(2, 1, figsize=(9, 6))

plotting.plot_stat_map(
    "t_stat_6m.nii.gz",
    bg_img=atlas,
    threshold=1e-6,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="t_stat",
    axes=ax[0],
    colorbar=True,
    vmax=5,
    vmin=-5,
    cmap="coolwarm",
)

plotting.plot_stat_map(
    "p_val_6m.nii.gz",
    bg_img=atlas,
    threshold=0,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="p_val",
    axes=ax[1],
    colorbar=True,
    vmax=0.05,
    cmap="hot_r",  # Inverted colormap
)

plt.savefig("6m_diff.png")
plt.show()

# End of main_group_diff_3month_6month.py
