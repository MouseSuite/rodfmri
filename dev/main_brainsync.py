#||AUM||
#||Shree Ganeshaya Namaha||

import nibabel as nb

from brainsync import brainSync, normalizeData
import numpy as np

import scipy as sp


atlas = '/deneb_disk/RodentTools/Atlases/DSURQE_40micron_UCLA/DSURQE_40micron_64_average_masked.nii.gz'


v = nb.load(atlas)

msk = v.get_fdata() > 0


print(v)


sub1 = '/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc11L/ses-1/func/sub-jgrADc11L_ses-1_task-rest_acq-EPI_b.atlas.nii.gz'
#'/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-1/func/sub-jgrADc1NT_ses-1_task-rest_acq-EPI_b.atlas.nii.gz'

sub2 = '/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc11L/ses-2/func/sub-jgrADc11L_ses-2_task-rest_acq-EPI_b.atlas.nii.gz'
#'/home/ajoshi/projects/rodfmri/dev/test_cases/sub-jgrADc1NT/ses-2/func/sub-jgrADc1NT_ses-2_task-rest_acq-EPI_b.atlas.nii.gz'


f1 = nb.load(sub1)
f2 = nb.load(sub2)

f1img = f1.get_fdata()[msk].T
f2img = f2.get_fdata()[msk].T

print(f1img.shape)
print(f2img.shape)

f1img, _, _ =  normalizeData(f1img)
f2img, _, _ =  normalizeData(f2img)


diff = np.sqrt(np.sum((f1img - f2img)**2, axis=0))
corr = np.sum(f1img*f2img, axis=0)


f2img_sync, _ = brainSync(f1img, f2img)

diff_sync = np.sqrt(np.sum((f1img - f2img_sync)**2, axis=0))
corr_sync = np.sum(f1img*f2img_sync, axis=0)


vout = np.zeros(v.shape)
vout[msk] = diff

unsyn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
unsyn_img.to_filename('unsynced.nii.gz')

vout[msk] = corr
unsyn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
unsyn_img.to_filename('corr_unsynced.nii.gz')


vout = np.zeros(v.shape)
vout[msk] = diff_sync

syn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
syn_img.to_filename('synced.nii.gz')

vout[msk] = corr_sync
syn_img = nb.Nifti1Image(vout, f1.affine, f1.header)
syn_img.to_filename('corr_synced.nii.gz')

