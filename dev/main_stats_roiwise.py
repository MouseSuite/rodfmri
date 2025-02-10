import numpy as np
import nibabel as nb
from scipy import stats
from statsmodels.stats.multitest import multipletests


# do group difference analysis between 3xTG and WT for sess_diff_fmri
# do group difference analysis between 3xTG and WT for sess_diff_fmri

# load the data


data = np.load("sess_diff_fmri.npz")
sess_diff_fmri = data["sess_diff_fmri"]
tg_or_wt = data["tg_or_wt"][:, 0]
sublist = data["sublist"]
msk = data["msk"]
atlas = str(data["atlas"])

msk_ind = np.where(msk.flatten()>0)[0]

v = nb.load(atlas)
atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64.label.nii.gz'
# Load the atlas labels
atlas_labels = nb.load(atlas).get_fdata()[msk]

# Initialize arrays to store ROI-wise statistics
unique_rois = np.unique(atlas_labels)
# remove 0 id from unuque_rois
unique_rois = unique_rois[unique_rois != 0]

roi_t_stat = np.zeros(len(unique_rois))
roi_p_val = np.zeros(len(unique_rois))

# Perform ROI-wise t-tests
for i, roi in enumerate(unique_rois):
    roi_mask_ind = np.where(atlas_labels == roi)[0]
    ctrl_diff_roi = np.mean(sess_diff_fmri[tg_or_wt == 1, :][:, roi_mask_ind],axis=1)
    tg_diff_roi = np.mean(sess_diff_fmri[tg_or_wt == 2, :][:, roi_mask_ind], axis=1)
    
    t_stat, p_val = stats.ttest_ind(tg_diff_roi, ctrl_diff_roi, axis=0)
    
    print(p_val,end="\n")
    # Average the t-statistics and p-values within the ROI
    roi_t_stat[i] = t_stat
    roi_p_val[i] = p_val

# Correct for multiple comparisons
p_val_corr = multipletests(roi_p_val, alpha=0.05, method="fdr_bh")
roi_p_val = p_val_corr[1]

# Create ROI-wise t-stat and p-val images
roi_t_stat_img = np.zeros(nb.load(atlas).shape)
roi_p_val_img = np.ones(nb.load(atlas).shape)
atlas_labels = nb.load(atlas).get_fdata()

for i, roi in enumerate(unique_rois):
    roi_mask=np.where(atlas_labels==roi)[0]
    roi_t_stat_img[atlas_labels == roi] = roi_t_stat[i]
    roi_p_val_img[atlas_labels == roi] = roi_p_val[i]
    # roi_p_val_img.ravel()[msk_ind[roi_mask]] = roi_p_val[i]

t_stat_img = nb.Nifti1Image(roi_t_stat_img, v.affine, v.header)
t_stat_img.to_filename("t_stat.nii.gz")

p_val_img = nb.Nifti1Image(roi_p_val_img, v.affine, v.header)
p_val_img.to_filename("p_val.nii.gz")

# Plot the t_stat and p_val images
from nilearn import plotting
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1, figsize=(9, 6))

plotting.plot_stat_map(
    "t_stat.nii.gz",
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
    "p_val.nii.gz",
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

#plt.tight_layout()
plt.savefig("t_stat_p_val.png")


# Plor mean of ctrl_diff and tg_diff, and their difference in the same coordinates as above
ctrl_diff_mean = np.mean(ctrl_diff, axis=0)
tg_diff_mean = np.mean(tg_diff, axis=0)

vout = np.zeros(v.shape)
vout[msk] = ctrl_diff_mean

ctrl_diff_mean_img = nb.Nifti1Image(vout, v.affine, v.header)
ctrl_diff_mean_img.to_filename("ctrl_diff_mean.nii.gz")

vout = np.zeros(v.shape)
vout[msk] = tg_diff_mean
tg_diff_mean_img = nb.Nifti1Image(vout, v.affine, v.header)
tg_diff_mean_img.to_filename("tg_diff_mean.nii.gz")

vout = np.zeros(v.shape)
vout[msk] = tg_diff_mean - ctrl_diff_mean
diff_mean_img = nb.Nifti1Image(vout, v.affine, v.header)
diff_mean_img.to_filename("diff_mean.nii.gz")

fig, ax = plt.subplots(3, 1, figsize=(15, 15))

plotting.plot_stat_map(
    ctrl_diff_mean_img,
    bg_img=atlas,
    threshold=0,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="ctrl_diff_mean",
    axes=ax[0],
    colorbar=True,
    cmap="hot",
    vmax=2,
)

plotting.plot_stat_map(
    tg_diff_mean_img,
    bg_img=atlas,
    threshold=0,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="tg_diff_mean",
    axes=ax[1],
    colorbar=True,
    cmap="hot",
    vmax=2,
)

plotting.plot_stat_map(
    diff_mean_img,
    bg_img=atlas,
    threshold=0,
    alpha=0.5,
    display_mode="ortho",
    dim=-0.5,
    title="diff_mean",
    axes=ax[2],
    colorbar=True,
    # cmap='hot',
    cmap="coolwarm",
    vmax=0.5,
)

#plt.tight_layout()
plt.savefig("diff_mean.png")


# plt.show()

# save the data
np.savez_compressed(
    "group_diff_fmri.npz",
    t_stat=roi_t_stat,
    p_val=roi_p_val,
    tg_or_wt=tg_or_wt,
    sublist=sublist,
    msk=msk,
    atlas=atlas,
)


print(f"Done Group difference analysis")
