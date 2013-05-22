#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import glob, os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyRegister():
  '''
  Perform a registration between a diffusion and a structural image.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the resampling and registration stage.
    
    required inputs:
      options.diffusion
      options.brain
      options.matrix
      options.smooth
    '''

    # validate inputs
    if not os.path.exists( options.diffusion ):
      raise Exception( 'Could not find the diffusion file!' )
    if not os.path.exists( options.brain ):
      raise Exception( 'Could not find the brain file!' )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    diffusion_file = os.path.join( tempdir, os.path.basename( options.diffusion ) )
    diffusion_file_name = os.path.splitext( os.path.basename( diffusion_file ) )[0]
    # also strip any .nii if the extension was .nii.gz
    diffusion_file_name = diffusion_file_name.replace( '.nii', '' )
    brain_file = os.path.join( tempdir, os.path.basename( options.brain ) )
    resampled_file = os.path.join( tempdir, diffusion_file_name + '_resampled.nii.gz' )
    matrix_file = os.path.join( tempdir, os.path.basename( options.matrix) )

    shutil.copyfile( options.diffusion, diffusion_file )
    shutil.copyfile( options.brain, brain_file )

    if options.smooth:
      interpolation = 1  # trilinear interpolation
    else:
      interpolation = 0  # nearest-neighbor interpolation

    # 1. STEP: resample the data
    Registration.resample( diffusion_file, brain_file, resampled_file, interpolation )

    # 2. STEP: register the resampled file to the target file
    Registration.register( resampled_file, brain_file, matrix_file )

    # 3. STEP: store the resampled data and the registration matrix in the output folder
    shutil.copyfile( matrix_file, options.matrix )
    
    print 'reg done'


#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Register an input scan to a target scan.' )

  entrypoint.add_input( 'd', 'diffusion', 'The diffusion scan to warp.' )
  entrypoint.add_input( 'b', 'brain', 'The brain scan as the target space.' )
  entrypoint.add_input( 'm', 'matrix', 'The matrix output path.' )
  entrypoint.add_flag( 's', 'smooth', 'Perform trilinear interpolation. DEFAULT: False', False )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyRegister.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
