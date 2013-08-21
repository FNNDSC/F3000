#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os, sys

# fyborg imports
from _core import *
from fy_cherrypick_freesurfer import FyCherrypickFreesurfer
from fy_copyscalars import FyCopyScalars
from fy_map import FyMap
from fy_prep import FyPrep
from fy_reconstruct import FyReconstruct
from fy_register import FyRegister
from fy_surfaceconnectivity import FySurfaceConnectivity
from fy_supersurfaceconnectivity import FySuperSurfaceConnectivity
from fy_surfacemap import FySurfaceMap
from fy_warptracks import FyWarpTracks

def run( freesurfer_directory, diffusion_directory, output_directory, decimation_level, verbose=False ):

  # setup temporary environment
  tempdir = Utility.setupEnvironment()

  if not verbose:
    sys.stdout = open( os.devnull, 'wb' )
    sys.stderr = open( os.devnull, 'wb' )

  #
  # GRAB STUFF FROM THE FREESURFER DIR
  #
  brain, segmentation, lh_smoothwm, rh_smoothwm = FyCherrypickFreesurfer.run( freesurfer_directory, output_directory, tempdir )

  #
  # RUN DTI PREP
  #
  diffusion, bvals, bvecs, qc_report = FyPrep.run( diffusion_directory, output_directory, tempdir )

  #
  # REGISTER DIFFUSION TO T1
  #
  smooth = False
  warped_diffusion, warped_segmentation, matrix, inverse_matrix = FyRegister.run( diffusion, segmentation, brain, output_directory, smooth, tempdir )

  #
  # RECONSTRUCT STREAMLINES
  #
  fa, adc, evecs, fibers = FyReconstruct.run( diffusion, warped_segmentation, output_directory, tempdir )

  #
  # WARP STREAMLINES
  #
  fibers_to_brain = os.path.join( output_directory, 'fibers_to_brain.trk' )
  FyWarpTracks.run( fibers, diffusion, brain, matrix, fibers_to_brain, tempdir )

  #
  # MAP SCALARS IN DIFFUSION SPACE
  #
  fibers_mapped = os.path.join( output_directory, 'fibers_mapped.trk' )
  FyMap.run( fibers, [adc, fa], fibers_mapped, tempdir )

  #
  # COPY SCALARS TO WARPED STREAMLINES
  #
  FyCopyScalars.run( fibers_mapped, fibers_to_brain, tempdir )

  #
  # MAP SCALARS IN T1 SPACE
  #
  fibers_to_brain_mapped = os.path.join( output_directory, 'fibers_to_brain_mapped.trk' )
  FyMap.run( fibers_to_brain, [segmentation], fibers_to_brain_mapped, tempdir )

  #
  # MAP SMOOTHWM VERTEX INDICES
  #
  fibers_with_vertices = os.path.join( output_directory, 'fibers_with_vertices.trk' )
  FySurfaceMap.run( fibers_to_brain_mapped, brain, lh_smoothwm, rh_smoothwm, decimation_level, fibers_with_vertices, tempdir )

  #
  # SURFACE CONNECTIVITY
  #
  if float( decimation_level ) < 1.0:
    # use the decimated surfaces now
    lh_smoothwm = lh_smoothwm.replace( '.smoothwm', '.decimated.smoothwm' )
    rh_smoothwm = rh_smoothwm.replace( '.smoothwm', '.decimated.smoothwm' )
  FySurfaceConnectivity.run( fibers_with_vertices, lh_smoothwm, rh_smoothwm, 'smoothwm', output_directory, tempdir )

  #
  # SUPER SURFACE CONNECTIVITY
  #
  radius = 5
  super_decimation_level = 1.0
  FySuperSurfaceConnectivity.run(fibers_with_vertices, brain, lh_smoothwm, rh_smoothwm, radius, super_decimation_level, output_directory, tempdir)
  

  # clean up temporary environment
  sys.stdout = sys.__stdout__
  sys.stderr = sys.__stderr__

  Utility.teardownEnvironment( tempdir )

  print 'All done.'

#
# entry point
#
if __name__ == "__main__":

  print "FYBORG3000 (c) FNNDSC, BCH 2013"

  # always show the help if no arguments were specified
  if len( sys.argv ) < 4:
    print 'USAGE:', sys.argv[0], '{FREESURFER_DIR} {DIFFUSION_DIR} {OUTPUT_DIR} [-v]'
    sys.exit( 1 )

  verbose = ( len( sys.argv ) == 5 )

  run( sys.argv[1], sys.argv[2], sys.argv[3], 0.333, verbose )
