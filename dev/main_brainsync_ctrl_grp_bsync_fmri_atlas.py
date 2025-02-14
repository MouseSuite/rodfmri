# ||AUM||
# ||Shree Ganeshaya Namaha||

import nibabel as nb

from brainsync import brainSync, normalizeData
import numpy as np

import numpy as sp
from tqdm import tqdm
import glob
import os
from brainsync import groupBrainSync
import time

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

num_time = 600
num_sub = 46
fmri_data_all_sub = np.zeros((size_msk, num_time, num_sub))
tg_or_wt = np.zeros((num_sub, 1))

nsub = 0

for i, sub in enumerate(sublist):

    print(f"Processing {sub}, {i} out of {len(sublist)}")
    # part_df['participant_id']):

    # sub = f'/deneb_disk/RodentTools/data/openneuro/ds001890/sub-jgrAD{s}'
    s = sub.split("/")[-1][9:]
    participant_data = part_df[part_df["participant_id"] == s]

    if participant_data["genotype"].values[0] == "C57BL/6":
        tg_or_wt[nsub] = 1
        tg_or_wt[nsub + 1] = 1
    elif participant_data["genotype"].values[0] == "3xTG":
        tg_or_wt[nsub] = 2
        tg_or_wt[nsub + 1] = 2
    elif participant_data["genotype"].values[0] == "3xTG_hydrocephalus":
        tg_or_wt[nsub] = 3
        tg_or_wt[nsub + 1] = 3
    else:
        tg_or_wt[nsub] = -1
        tg_or_wt[nsub + 1] = -1

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
        tg_or_wt[nsub] = -2
        tg_or_wt[nsub + 1] = -2

        continue

    f1 = nb.load(sub1)
    f2 = nb.load(sub2)

    f1img = f1.get_fdata()[msk]
    f2img = f2.get_fdata()[msk]

    fmri_data_all_sub[:, :, nsub] = f1img
    nsub += 1
    fmri_data_all_sub[:, :, nsub] = f2img
    nsub += 1


# save the data
np.savez(
    "sess_diff_fmri_all_sub.npz",
    fmri_data_all_sub=fmri_data_all_sub,
    tg_or_wt=tg_or_wt,
    sublist=sublist,
    msk=msk,
    atlas=atlas,
)

# load the data
data = np.load("sess_diff_fmri_all_sub.npz")
fmri_data_all_sub = data["fmri_data_all_sub"]
tg_or_wt = data["tg_or_wt"][:, 0]

msk = data["msk"]
atlas = str(data["atlas"])

# do group brainSync

ctrl_data = fmri_data_all_sub[:, :, tg_or_wt == 1]


# swap 0 and 1st dimension
ctrl_data = np.swapaxes(ctrl_data, 0, 1)  # Make it TxVxS

# measure time taken

start_time = time.time()
X2, Os, Costdif, TotalError = groupBrainSync(ctrl_data)
end_time = time.time()

print(f"Time taken for groupBrainSync: {end_time - start_time} seconds")

np.savez(
    "group_diff_fmri.npz",
    X2=X2,
    Os=Os,
    Costdif=Costdif,
    TotalError=TotalError,
    tg_or_wt=tg_or_wt,
    sublist=sublist,
    msk=msk,
    atlas=atlas,
    fmri_data_all_sub=fmri_data_all_sub,
    ctrl_data=ctrl_data,
)

