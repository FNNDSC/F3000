#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os, tempfile

# third-party imports
import nipy

# fyborg imports
from _core import Registration


workdir = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working'

input = os.path.join( workdir, 'diffusion.nii' )
target = os.path.join( workdir, 'brain.nii' )
output = os.path.join( workdir, 'diffusion_resampled.nii' )

#Registration.resample2(input, target, output)

#Registration.diffusion2structural( input, target, output )

registered_dir = os.path.join(workdir, 'registered')
os.mkdir(registered_dir)
#
Registration.register(output, target, registered_dir)
#

#images = ['/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion0.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion1.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion2.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion3.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion4.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion5.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion6.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion7.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion8.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion9.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion10.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion11.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion12.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion13.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion14.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion15.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion16.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion17.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion18.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion19.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion20.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion21.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion22.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion23.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion24.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion25.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion26.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion27.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion28.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion29.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion30.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion31.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion32.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion33.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion34.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion35.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion36.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion37.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion38.nii', '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/working/resampled/diffusion39.nii']
#image_s = []
#
#for i in images:
#  image_s.append(nipy.load_image(i))
#
#print merge_images(image_s)