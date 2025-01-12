# ||AUM||
# ||Shree Ganeshaya Namaha||

import nibabel as nb

from brainsync import brainSync, normalizeData
import numpy as np

import numpy as sp
from tqdm import tqdm
import glob
import os


sublist = glob.glob("/deneb_disk/RodentTools/data/openneuro/ds001890/sub*")

# Read participants.tsv file
import pandas as pd

part_file = "/deneb_disk/RodentTools/data/openneuro/ds001890/participants.tsv"
part_df = pd.read_csv(part_file, sep="\t")


atlas = "/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz"


v = nb.load(atlas)

msk = v.get_fdata() > 0

size_msk = np.sum(msk)  # size of mask


print(v)
sess_diff_fmri = np.zeros((len(sublist), size_msk))

tg_or_wt = np.zeros((len(sublist), 1))

for i, sub in enumerate(sublist):

    # part_df['participant_id']):

    # sub = f'/deneb_disk/RodentTools/data/openneuro/ds001890/sub-jgrAD{s}'
    s = sub.split("/")[-1][9:]
    print(sub)
    participant_data = part_df[part_df["participant_id"] == s]

    if participant_data["genotype"].values[0] == "C57BL/6":
        tg_or_wt[i] = 1
    elif participant_data["genotype"].values[0] == "3xTG":
        tg_or_wt[i] = 2
    elif participant_data["genotype"].values[0] == "3xTG_hydrocephalus":
        tg_or_wt[i] = 3
    else:
        tg_or_wt[i] = -1
        # this is error! show error message and exit
        print(f'Error: Genotype not found for {sub.split("/")[-1]}')
        exit()

        # tg_or_wt[sublist.index(sub)] = 2

    sub1 = f'{sub}/ses-1/func/{sub.split("/")[-1]}_ses-1_task-rest_acq-EPI_bold.filt.atlas.nii.gz'
    #'/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-1/func/sub-jgrADc1NT_ses-1_task-rest_acq-EPI_b.atlas.nii.gz'

    sub2 = f'{sub}/ses-2/func/{sub.split("/")[-1]}_ses-2_task-rest_acq-EPI_bold.filt.atlas.nii.gz'
    #'/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-2/func/sub-jgrADc1NT_ses-2_task-rest_acq-EPI_b.atlas.nii.gz'

    if not (os.path.isfile(sub1) and os.path.isfile(sub2)):

        print(f"Both sessions not found in {s}\n Skipping...")
        tg_or_wt[i] = -2

        continue

    f1 = nb.load(sub1)
    f2 = nb.load(sub2)

    f1img = f1.get_fdata()[msk].T
    f2img = f2.get_fdata()[msk].T

    print(f1img.shape)
    print(f2img.shape)

    f1img, _, _ = normalizeData(f1img)
    f2img, _, _ = normalizeData(f2img)

    diff = np.sqrt(np.sum((f1img - f2img) ** 2, axis=0))
    corr = np.sum(f1img * f2img, axis=0)

    f2img_sync, _ = brainSync(f1img, f2img)

    diff_sync = np.sqrt(np.sum((f1img - f2img_sync) ** 2, axis=0))
    corr_sync = np.sum(f1img * f2img_sync, axis=0)

    vout = np.zeros(v.shape)
    vout[msk] = diff

    sess_diff_fmri[i, :] = diff

    unsyn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
    unsyn_img.to_filename("unsynced.nii.gz")

    vout[msk] = corr
    unsyn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
    unsyn_img.to_filename("corr_unsynced.nii.gz")

    vout = np.zeros(v.shape)
    vout[msk] = diff_sync

    syn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
    syn_img.to_filename("synced.nii.gz")

    vout[msk] = corr_sync
    syn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
    syn_img.to_filename("corr_synced.nii.gz")

    # Plot before and after syncing and save as png files
    from nilearn import plotting
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(20, 5))

    plotting.plot_stat_map(
        unsyn_img,
        bg_img=atlas,
        threshold=0,
        alpha=0.5,
        display_mode="ortho",
        dim=-0.5,
        title="Unsynced",
        axes=ax[0],
    )
    plotting.plot_stat_map(
        syn_img,
        bg_img=atlas,
        threshold=0,
        alpha=0.5,
        display_mode="ortho",
        dim=-0.5,
        title="Synced",
        axes=ax[1],
    )

    plt.tight_layout()
    # add title
    plt.suptitle(f'{sub.split("/")[-1]}')
    plt.savefig(f'{sub.split("/")[-1]}_synced.png')

    # plt.show()
    # plt.pause(1)
    plt.close()

# save the data
np.savez_compressed("sess_diff_fmri.npz", sess_diff_fmri=sess_diff_fmri, tg_or_wt=tg_or_wt, sublist=sublist, msk=msk, atlas=atlas)

print(f"Done with {sub.split('/')[-1]}")
