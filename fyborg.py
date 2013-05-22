#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os

# fyborg imports
from _core import *
from fy_register import FyRegister
from fy_reconstruct import FyReconstruct
from fy_warptracks import FyWarpTracks

workdir = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/new'
outputdir = os.path.join( workdir, 'out' )

if not os.path.exists( outputdir ):
  os.mkdir( outputdir )


options = lambda:0
options.tempdir = Utility.setupEnvironment()

# inputs
options.diffusion = os.path.join( workdir, 'diffusion.nii.gz' )
options.bvals = os.path.join( workdir, 'diffusion.bval' )
options.bvecs = os.path.join( workdir, 'diffusion.bvec' )
options.brain = os.path.join( workdir, 'brain.nii.gz' )
options.segmentation = os.path.join( workdir, 'aparc+aseg.nii.gz' )

# outputs
options.matrix = os.path.join( outputdir, 'diffusion-to-brain.mat' )
options.fibers = os.path.join( outputdir, 'fibers.trk' )
options.fa = os.path.join( outputdir, 'fa.nii.gz' )
options.adc = os.path.join( outputdir, 'adc.nii.gz' )
options.evecs = os.path.join( outputdir, 'evecs.nii.gz' )
options.warped_fibers = os.path.join( outputdir, 'fibers-to-brain.trk' )

# flags
options.smooth = False


FyRegister.run( options )
FyReconstruct.run( options )
FyWarpTracks.run( options )


