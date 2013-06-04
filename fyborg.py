#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os

# fyborg imports
from _core import *
from fy_map import FyMap
from fy_prep import FyPrep
from fy_register import FyRegister
from fy_reconstruct import FyReconstruct
from fy_surfacemap import FySurfaceMap
from fy_warptracks import FyWarpTracks




options = lambda:0

# inputs
options.freesurfer_directory = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/FREESURFER'
options.diffusion_directory = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/DIFFUSION_HighRes_Short'
options.output_directory = '/chb/users/daniel.haehn/TMP/FYBORG3000/4543113/latest'

# outputs
options.diffusion = os.path.join( options.output_directory, 'diffusion.nii.gz' )
options.qc_report = os.path.join( options.output_directory, 'diffusion_QCReport.txt' )
options.bvals = os.path.join( options.output_directory, 'diffusion.bval' )
options.bvecs = os.path.join( options.output_directory, 'diffusion.bvec' )
options.brain = os.path.join( options.output_directory, 'brain.nii.gz' )
options.segmentation = os.path.join( options.output_directory, 'aparc+aseg.nii.gz' )
options.lh_smoothwm = os.path.join( options.output_directory, 'lh.smoothwm' )
options.rh_smoothwm = os.path.join( options.output_directory, 'rh.smoothwm' )
options.lh_smoothwm_nover2ras = os.path.join( options.output_directory, 'lh.smoothwm.nover2ras' )
options.rh_smoothwm_nover2ras = os.path.join( options.output_directory, 'rh.smoothwm.nover2ras' )
options.warped_diffusion = os.path.join( options.output_directory, 'diffusion-to-brain.nii.gz' )
options.matrix = os.path.join( options.output_directory, 'fibers-to-brain.mat' )
options.inverse_matrix = os.path.join( options.output_directory, 'brain-to-fibers.mat' )
options.warped_segmentation = os.path.join( options.output_directory, 'aparc+aseg-to-fibers.nii.gz' )
options.fibers = os.path.join( options.output_directory, 'fibers.trk' )
options.fa = os.path.join( options.output_directory, 'fa.nii.gz' )
options.adc = os.path.join( options.output_directory, 'adc.nii.gz' )
options.evecs = os.path.join( options.output_directory, 'evecs.nii.gz' )
options.warped_fibers = os.path.join( options.output_directory, 'fibers-to-brain.trk' )
options.fibers_mapped = os.path.join( options.output_directory, 'fibers-with-vertices.trk' )

options.connectivity_matrix = os.path.join( options.output_directory, 'surface_connectivity.csv' )

# flags
options.smooth = False



#
# Processing pipeline
#
options.tempdir = Utility.setupEnvironment()

if not os.path.exists( options.output_directory ):
  os.mkdir( options.output_directory )


# Utility.parseFreesurferDir( options.freesurfer_directory, options.brain, options.segmentation, options.lh_smoothwm, options.rh_smoothwm )

# FyPrep.run( options )
# FyRegister.run( options )
# FyReconstruct.run( options )
# FyWarpTracks.run( options )

# map in diffusion space
# options.fibers_to_map = options.fibers
# options.volumes_to_map = [options.fa, options.adc]
# FyMap.run( options )

# copy scalars from diffusion space fibers to T1 space fibers
# Utility.copy_scalars( options.fibers_mapped, options.warped_fibers, options.warped_fibers )

# map in T1 space
# options.fibers_to_map = options.warped_fibers
# options.volumes_to_map = [options.segmentation]
# FyMap.run( options )

# map vertices
# options.fibers_to_map = options.warped_fibers
# FySurfaceMap.run(options)

# surface connectivity
# SurfaceConnectivity.connect(options.fibers_mapped, 'smoothwm', options.lh_smoothwm, options.rh_smoothwm, options.connectivity_matrix )

# threshold using label
options.label = os.path.join( options.output_directory, 'lh.cortex.label' )
options.fibers_thresholded = os.path.join( options.output_directory, 'fibers-thresholded2.trk' )
Thresholding.threshold_by_label( options.fibers_mapped, 'smoothwm', options.label, options.fibers_thresholded )

# Utility.teardownEnvironment( options.tempdir )
