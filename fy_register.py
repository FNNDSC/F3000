#!/usr/bin/env python

#
# FYBORG3000
#

# standard imports
import os, shutil, sys, tempfile

# fyborg imports
from _core import *


class FyRegister():
  '''
  Perform a registration between two scans.
  '''

  @staticmethod
  def run( options ):
    '''
    Runs the resampling and registration stage.
    
    required inputs:
      options.input
      options.target
      options.output
    '''

    # validate inputs
    if not os.path.exists( options.input ):
      raise Exception( 'Could not find the input file!' )
    if not os.path.exists( options.target ):
      raise Exception( 'Could not find the target file!' )
    if not os.path.exists( options.output ):
      os.mkdir( options.output )

    # use a temporary workspace
    tempdir = options.tempdir
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( options.input ) )
    input_file_name = os.path.splitext( os.path.basename( input_file ) )[0]
    target_file = os.path.join( tempdir, os.path.basename( options.target ) )
    resampled_file = os.path.join( tempdir, input_file_name + '_resampled.nii.gz' )
    registered_file = os.path.join( tempdir, 'deformed.nii.gz' )
    affine_file = os.path.join( tempdir, 'Affine.txt' )
    shutil.copyfile( options.input, input_file )
    shutil.copyfile( options.target, target_file )

    if options.smooth:
      interpolation = 1  # trilinear interpolation
    else:
      interpolation = 0  # nearest-neighbor interpolation

    # 1. STEP: resample the data
    Registration.resample( input_file, target_file, resampled_file, interpolation )

    # 2. STEP: register the resampled data
    Registration.register( resampled_file, target_file, tempdir )

    # 3. STEP: copy registered data to output folder
    shutil.copyfile( registered_file, os.path.join( options.output, input_file_name + '_registered.nii.gz' ) )
    shutil.copyfile( affine_file, os.path.join( options.output, input_file_name + '_transform.txt' ) )

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Register an input scan to a target scan.' )

  entrypoint.add_input( 'i', 'input', 'The input scan to warp. F.e. a diffusion scan.' )
  entrypoint.add_input( 't', 'target', 'The target scan (fixed volume). F.e. a structural scan.' )
  entrypoint.add_input( 'o', 'output', 'The output folder.' )
  entrypoint.add_flag( 's', 'smooth', 'Perform trilinear interpolation. DEFAULT: False', False )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  options.tempdir = Utility.setupEnvironment()

  FyRegister.run( options )

  # clean up temporary environment
  Utility.teardownEnvironment( options.tempdir )
