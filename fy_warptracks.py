#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyWarpTracks():
  '''
  Warp a TrackVis file.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the warping stage.
    
    required inputs:
      options.fibers
      options.diffusion
      options.brain
      options.matrix
      options.warped_fibers
    '''

    # validate inputs
    if not os.path.exists( options.fibers ):
      raise Exception( 'Could not find the input fibers file!' )
    if not os.path.exists( options.diffusion ):
      raise Exception( 'Could not find the diffusion file!' )
    if not os.path.exists( options.brain ):
      raise Exception( 'Could not find the brain file!' )
    if not os.path.exists( options.matrix ):
      raise Exception( 'Could not find the matrix file!' )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    fibers_file = os.path.join( tempdir, os.path.basename( options.fibers ) )
    diffusion_file = os.path.join( tempdir, os.path.basename( options.diffusion ) )
    brain_file = os.path.join( tempdir, os.path.basename( options.brain ) )
    matrix_file = os.path.join( tempdir, os.path.basename( options.matrix ) )

    shutil.copyfile( options.fibers, fibers_file )
    shutil.copyfile( options.diffusion, diffusion_file )
    shutil.copyfile( options.brain, brain_file )
    shutil.copyfile( options.matrix, matrix_file )

    warped_fibers_file = os.path.join( tempdir, os.path.basename( options.warped_fibers ) )

    # 1. STEP: warp the data
    Registration.warp_fibers( fibers_file, diffusion_file, brain_file, matrix_file, warped_fibers_file )

    # 3. STEP: store the warped TrackVis file in the output folder
    shutil.copyfile( warped_fibers_file, os.path.join( options.warped_fibers ) )


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Warp (transform) a TrackVis file using a FLIRT registration matrix.' )

  entrypoint.add_input( 'f', 'fibers', 'The input TrackVis file.' )
  entrypoint.add_input( 'd', 'diffusion', 'The original diffusion volume.' )
  entrypoint.add_input( 'b', 'brain', 'The original structural scan.' )
  entrypoint.add_input( 'm', 'matrix', 'The FLIRT registration matrix.' )
  entrypoint.add_input( 'wf', 'warped_fibers', 'The output TrackVis file.' )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyWarpTracks.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
