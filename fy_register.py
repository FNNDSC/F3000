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
    splitted_dir = os.path.join( tempdir, 'splitted' )
    if not os.path.exists( splitted_dir ):
      os.mkdir( splitted_dir )
    registered_dir = os.path.join( tempdir, 'registered' )
    if not os.path.exists( registered_dir ):
      os.mkdir( registered_dir )
    registered_file = os.path.join( registered_dir, 'deformed.nii.gz' )
    transform_file = os.path.join( registered_dir, 'Affine.txt' )
    warped_dir = os.path.join( tempdir, 'warped' )
    if not os.path.exists( warped_dir ):
      os.mkdir( warped_dir )
    shutil.copyfile( options.input, input_file )
    shutil.copyfile( options.target, target_file )

    if options.smooth:
      interpolation = 1  # trilinear interpolation
    else:
      interpolation = 0  # nearest-neighbor interpolation

    # 1. STEP: resample the data
    #Registration.resample( input_file, target_file, resampled_file, interpolation )

    # 2. STEP: split the resampled volume
    #Registration.splitDiffusion( resampled_file, splitted_dir )
    splitted_files = Utility.natsort( glob.glob( os.path.join( splitted_dir, '*' ) ) )

    # 3. STEP: register the first resampled and splitted scan
    #Registration.register( splitted_files[0], target_file, registered_dir )

    # 4. STEP: apply transform to all splitted files
    for s in splitted_files:
      warped_output_file = os.path.join( warped_dir, os.path.basename( s ) )
      #Registration.warp( s, target_file, transform_file, warped_output_file )

    warped_files = Utility.natsort( glob.glob( os.path.join( warped_dir, '*' ) ) )

    # 5. STEP: merge all warped files back to one volume and store it in the output folder
    Registration.mergeDiffusion( warped_files, os.path.join( options.output, input_file_name + '_registered.nii.gz' ) )
    shutil.copyfile( transform_file, os.path.join( options.output, input_file_name + '_transform.txt' ) )


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
