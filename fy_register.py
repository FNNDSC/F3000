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
  Register one or two scans to a target by performing resampling and alignment.
  '''

  @staticmethod
  def run( input, input2, target, output, smooth, tempdir ):
    '''
    Runs the resampling and registration stage.
    '''

    # validate inputs
    if not os.path.exists( input ):
      raise Exception( 'Could not find the input file!' )
    if not os.path.exists( target ):
      raise Exception( 'Could not find the target file!' )

    if not os.path.exists( output ):
      # create output directory
      os.mkdir( output )

    # use a temporary workspace
    # .. and copy all working files
    input_file = os.path.join( tempdir, os.path.basename( input ) )
    input_file_name = Utility.get_file_name( input_file )
    target_file = os.path.join( tempdir, os.path.basename( target ) )
    target_file_name = Utility.get_file_name( target_file )
    if input2:
      input2_file = os.path.join( tempdir, os.path.basename( input2 ) )
      input2_file_name = Utility.get_file_name( input2_file )
      warped_input2_file = os.path.join( tempdir, input2_file_name + '_to_' + input_file_name + '.nii.gz' )
    else:
      warped_input2_file = ''
    resampled_file = os.path.join( tempdir, input_file_name + '_resampled.nii.gz' )
    matrix_file = os.path.join( tempdir, input_file_name + '_to_' + target_file_name + '.mat' )
    inverse_matrix_file = os.path.join( tempdir, target_file_name + '_to_' + input_file_name + '.mat' )

    warped_input_file = os.path.join( tempdir, os.path.basename( input_file_name + '_to_' + target_file_name + '.nii.gz' ) )

    shutil.copyfile( input, input_file )
    shutil.copyfile( target, target_file )
    if input2:
      shutil.copyfile( input2, input2_file )

    if options.smooth:
      interpolation = 1  # trilinear interpolation
    else:
      interpolation = 0  # nearest-neighbor interpolation

    # 1. STEP: resample the data
    Registration.resample( input_file, target_file, resampled_file, interpolation )

    # 2. STEP: register the resampled file to the target file
    Registration.register( resampled_file, target_file, matrix_file, warped_input_file )

    # 3. STEP: create the inverse matrix
    Registration.invert_matrix( matrix_file, inverse_matrix_file )

    if input2:
      # 4. STEP: warp the second input towards the real input
      Registration.warp( input2_file, input_file, inverse_matrix_file, warped_input2_file )

    # 5. STEP: store the warped data and the registration matrices in the output folder
    shutil.copy( matrix_file, output )
    shutil.copy( inverse_matrix_file, output )
    shutil.copy( warped_input_file, output )
    if input2:
      shutil.copy( warped_input2_file, output )

    return os.path.join( output, os.path.basename( warped_input_file ) ), os.path.join( output, os.path.basename( warped_input2_file ) ), os.path.join( output, os.path.basename( matrix_file ) ), os.path.join( output, os.path.basename( inverse_matrix_file ) )

#
# entry point
#
if __name__ == "__main__":
  entrypoint = Entrypoint( description='Register one scan to a target by performing resampling and alignment. Can perform inverse warping on the way.' )

  entrypoint.add_input( 'i', 'input', 'The scan to warp.' )
  entrypoint.add_input( 'i2', 'input2', 'Another scan to warp using the inverse matrix (meaning towards the input rather than the target).', False )  # not required
  entrypoint.add_input( 't', 'target', 'The scan to use as target space.' )
  entrypoint.add_input( 'o', 'output', 'The output directory.' )
  entrypoint.add_flag( 's', 'smooth', 'Perform trilinear interpolation. DEFAULT: False', False )

  options = entrypoint.parse( sys.argv )

  # attach a temporary environment
  tempdir = Utility.setupEnvironment()

  print '-' * 80
  print os.path.splitext( os.path.basename( __file__ ) )[0] + ' running'

  if not options.verbose:
    sys.stdout = open( os.devnull, 'wb' )

  a, b, c, d = FyRegister.run( options.input, options.input2, options.target, options.output, options.smooth, tempdir )

  sys.stdout = sys.__stdout__

  print 'Done!'
  print 'Output warped input file: ', a
  if options.input2:
    print 'Output inverse warped second input file: ', b
  print 'Output matrix file: ', c
  print 'Output inverse matrix file: ', d
  print '-' * 80

  # clean up temporary environment
  Utility.teardownEnvironment( tempdir )
